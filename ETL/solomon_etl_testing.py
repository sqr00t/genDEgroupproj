import pandas as pd
import logging, os, redshift_connector
from json import loads as json_to_dict
from hashlib import shake_256
from boto3 import client, resource
from sqlalchemy import create_engine
from sqlalchemy import TIMESTAMP as ts

logger = logging.getLogger()
logger.setLevel(logging.INFO)

### Loader to Redshift
def send_df(tablename: str, _dataframe: pd.DataFrame, indexing=None):
    ## define schema name to send tables to
    schema_name = 'testschema'
    
    ## Get credentials from parameter store
    ssm_client = client("ssm")
    redshift_parameters = ssm_client.get_parameters(
        Names=["team3_creds"],
        WithDecryption=True)

    # deconstruct json parameters to get required details
    cred_string = redshift_parameters['Parameters'][0]['Value'] # gets the credentials but has \n

    # convert cred_string json to dict
    cred_dict = json_to_dict(cred_string)
    
    # extract login details from cred_dict
    database="team3_cafe"
    user=cred_dict['user']
    password=cred_dict['password']
    host=cred_dict['host']
    port=cred_dict['port']
    
    ## Connect to db and to_sql
    try:
        # Database SQLAlchemy engine, make into context manager to auto-dispose after running commands
        engine = create_engine(f'redshift+redshift_connector://{user}:{password}@{host}:{port}/{database}')

        # Sets indexing of df to push to db
        if indexing == None:
            index_bool = False
        else:
            indexing = indexing
            index_bool = True

        # send df to db
        _dataframe.to_sql(name=tablename, con=engine, schema=schema_name, if_exists='append', index=index_bool, index_label=indexing, dtype={'timestamp': ts(timezone=False)})
    except (Exception, redshift_connector.DatabaseError) as error:
        return logger.info(error)
    finally:
        # Dispose engine and connection, if engine creation successful
        if engine:
            engine.dispose()
            return logger.info(f"Added data to {tablename}. Connection closed.")

def handler(event, context):
    ### Stuff to do when triggered on new csv in bucket event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_file_name = event['Records'][0]['s3']['object']['key']

    # Use boto3 to download the event s3 object key to the /tmp directory.
    s3 = resource('s3')
    s3.meta.client.download_file(bucket_name, s3_file_name, f'/tmp/{s3_file_name}')

    # Confirm file downloaded to /tmp/ and log file name
    dl_to_tmp = os.path.isfile('/tmp/' + s3_file_name)
    logger.info(f'File {s3_file_name} downloaded to /tmp/: {dl_to_tmp}')

    ### Extracting data from csv to df
    ## Loading data from csv
    # Load csv. csv does not have header in first row, set header=None
    df = pd.read_csv('/tmp/' + s3_file_name, header=None)

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

    ## orders table
    orders_table = pd.DataFrame(df[['order_id', 'timestamp', 'store_name', 'total_price', 'payment_type']]).drop_duplicates(ignore_index=True)

    # Merge store_id with respective store_name in orders_table
    orders_table = orders_table.merge(stores_table, how='left', on='store_name')

    # Drop store_name in orders_table
    orders_table.drop('store_name', axis=1, inplace=True)

    ## products table
    # drop duplicate products
    products_table = pd.DataFrame(df[['item_name', 'item_size', 'item_price']]).drop_duplicates(ignore_index=True)

    # Make unique product_id of 16 characters for orders table, using concatenated string of row values
    products_table['product_id'] = products_table.astype(str).sum(1).apply(lambda x: shake_256(x.encode()).hexdigest(8))

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

    ### Load tables to desired table in schema, schema defined in send_df function definition
    send_df("stores", stores_table)
    send_df("orders", orders_table)
    send_df("products", products_table)
    send_df("orders_products", orders_products)