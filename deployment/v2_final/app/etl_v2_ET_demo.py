import pandas as pd
import logging, os
from hashlib import shake_256
from boto3 import resource

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = resource('s3')
       
def csv_to_bucket(csvname: str, _dataframe: pd.DataFrame):
    try:
        ### Save processed _dataframe to .csv in tmp
        _dataframe.to_csv(f"/tmp/{csvname}", header=False, index=False)
        logger.info(f"Extract and Transformation completed to: '{csvname}'")

        ### Upload CSV to bucket with s3 resource
        s3.meta.client.upload_file(f"/tmp/{csvname}", 'team3-demo-processed', csvname)
        logger.info(f"Uploaded '{csvname}' to team3-demo-processed bucket root")

    except Exception as e:
        logger.info(e)

def handler(event, context):
    ### Stuff to do when triggered on new csv in bucket event
    logger.info(event)
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_file_name = event['Records'][0]['s3']['object']['key'] # '2022/2/16/widnes_16-02-2022_08-00-00.csv'
    file_name = s3_file_name.replace('/', '')

    # Use boto3 to download the event s3 object key to the /tmp directory.
    # https://python.tutorialink.com/aws-s3-lambda-how-do-you-download-image-from-tmp-that-has-a-prefix/
    s3.meta.client.download_file(bucket_name, s3_file_name, f'/tmp/{file_name}') # modify s3_file_name to the actual filename as subdir creation not supported

    # Confirm file downloaded to /tmp/ and log file name
    dl_to_tmp = os.path.isfile('/tmp/' + file_name)
    logger.info(f'File {file_name} downloaded to /tmp/: {dl_to_tmp}')

    ### Extracting data from csv to df
    ## Loading data from csv
    # Load csv. csv does not have header in first row, set header=None
    df = pd.read_csv('/tmp/' + file_name, header=None)

    # List for setting df column names, set column names
    df.columns = ['timestamp', 'store_name', 'customer_name', 'basket_items', 'total_price', 'payment_type', 'card_number']

    ## Initial data cleaning steps
    # Convert date-time to timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Make unique order_id of 16 characters for orders table, using concatenated string of row values
    df['order_id'] = df.astype(str).sum(1).apply(lambda x: shake_256(x.encode()).hexdigest(8))

    # Drop customer_name and card_number columns to remove PII
    df.drop(['customer_name', 'card_number'], axis=1, inplace=True)

    ### Transform to 1NF
    # Split basket_items by comma-separated values outputs values in field as list
    df['basket_items'] = df['basket_items'].str.split(', ')
    df = df.explode('basket_items')

    # Expand list from previous step into separate columns
    df[['item', 'item_price']] = df['basket_items'].str.rsplit(' - ', n=1, expand=True)

    # Further split 'item' to 'item_size', 'item_name'
    df[['item_size', 'item_name']] = df['item'].str.split(' ', n=1, expand=True)

    ### Transform to 3NF
    ## stores table
    # drop duplicate store names
    stores_table = pd.DataFrame(df[['store_name']]).drop_duplicates(subset='store_name', keep='first')

    # make unique store_id of 10 characters for stores table
    stores_table['store_id'] = stores_table.astype(str).sum(1).apply(lambda x: shake_256(x.encode()).hexdigest(5))

    #### final stores table
    stores_final = pd.DataFrame(stores_table[['store_id', 'store_name']])
    
    ## orders table
    orders_table = pd.DataFrame(df[['order_id', 'timestamp', 'store_name', 'total_price', 'payment_type']]).drop_duplicates(ignore_index=True)

    # Merge store_id with respective store_name in orders_table
    orders_table = orders_table.merge(stores_table, how='left', on='store_name')

    # Drop store_name in orders_table
    orders_table.drop('store_name', axis=1, inplace=True)
    
    #### final orders table
    orders_final = pd.DataFrame(orders_table[['order_id', 'timestamp', 'store_id', 'total_price', 'payment_type']])

    ## products table
    # drop duplicate products
    products_table = pd.DataFrame(df[['item_name', 'item_size', 'item_price']]).drop_duplicates(ignore_index=True)

    # Make unique product_id of 16 characters for orders table, using concatenated string of row values
    products_table['product_id'] = products_table.astype(str).sum(1).apply(lambda x: shake_256(x.encode()).hexdigest(8))

    #### final products table
    products_final = pd.DataFrame(products_table[['product_id', 'item_name', 'item_size', 'item_price']])

    ## orders_products linking table
    # drop redundant columns
    orders_products = df.drop(['timestamp', 'store_name', 'basket_items', 'total_price', 'payment_type', 'item'], axis=1)

    # Merge item_price, item_size, and item_price with respective products_id in products_table
    orders_products = orders_products.merge(products_table, on=['item_price', 'item_size', 'item_name'], how="left")

    # Aggregate repeated rows by grouping and counting duplicates with chained size() method
    orders_products = orders_products.groupby(orders_products.columns.tolist(), as_index=False).size()

    # Drop 'item_price', 'item_size', 'item_name', as merge does not drop them, not needed after merge
    orders_products = orders_products.drop(['item_price', 'item_size', 'item_name'], axis=1)

    # Rename 'size' column from aggregation to 'quantity'
    orders_products.rename(columns={'size':'quantity'}, inplace=True)

    #### final orders_products table
    orders_products_final = pd.DataFrame(orders_products[['order_id', 'product_id', 'quantity']])

    ### Save _processed.csv to /tmp, then send to respective bucket
    csv_to_bucket(f"{file_name}_stores.csv", stores_final)
    csv_to_bucket(f"{file_name}_orders.csv", orders_final)
    csv_to_bucket(f"{file_name}_products.csv", products_final)
    csv_to_bucket(f"{file_name}_ordersproducts.csv", orders_products_final)