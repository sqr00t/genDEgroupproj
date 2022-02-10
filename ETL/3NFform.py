#import modin.pandas as pd ##EXPERIMENTAL (modin is a lot faster for larger datasets, requires config)
import pandas as pd
from hashlib import shake_256
from sqlalchemy import create_engine
from sqlalchemy import TIMESTAMP as ts

### Load csv. csv does not have header in first row, set header=None
df = pd.read_csv('chesterfield_25-08-2021_09-00-00.csv', header=None)

###TODO EDA notes

## store_name can be dropped and used as table name. Make script to:
# 1. Cleanse data
# 2. Generate pgsql db create table script with table name of store-name_payment-type,
#    and 3NF schema (if not exists)
# 3. Normalise and split tables
# 4. df.to_sql(table name, etc.)

## List for setting df column names, set column names
# Cannot set index name to 'id' or 'order_id' as 1NF would increase redundancy,
# and cause index to not be unique, timestamp would be uniquely identifiable if separate tables for payment_type.
df.columns = ['timestamp', 'store_name', 'customer_name', 'basket_items', 'total_price', 'payment_type', 'card_number']
sql_table_name = list(df.store_name.unique())[0]

## Convert date-time to timestamp
#https://stackoverflow.com/questions/54312802/pandas-convert-from-datetime-to-integer-timestamp
#df['timestamp'] = (pd.to_datetime(df['timestamp']).view(np.int64) / 10**9).astype(int)
df['timestamp'] = pd.to_datetime(df['timestamp'])

## Generate a uuid for 'id'? >> Just make a separate 'order_id' column, containing hash of
## concatenated string of values in row. When using pd.to_sql(), add index=False arg.
# Deprecated: Copy index to new 'order_id' column
#df['order_id'] = df.index
df['order_id'] = df.astype(str).sum(1).apply(lambda x: shake_256(x.encode()).hexdigest(8))

### Remove sensitive data (customer_name and card_number). <Drop>/Hash

## OPTIONAL/DEPRECATE: Hash card/customer name instead of dropping, after making order_id. SHA256 hash function
def hash_col(col_name):
    df[col_name] = df[col_name].apply(
        lambda x: 
            shake_256(x.encode()).hexdigest(8)
    )

# Hash customer_name.
hash_col('customer_name')

# card_number fields are type: float. Convert to str before hashing.
df['card_number'] = df['card_number'].astype(str)
hash_col('card_number')

# Temp: Drop hashed customer_name and card_number columns as they are optional.
df.drop(['customer_name', 'card_number'], axis=1, inplace=True)

# inspect
print(f"df has {df.shape[0]} rows")
df.head(10)

## Split basket_items by comma-separated values - not expanding:
df['basket_items'] = df['basket_items'].str.split(', ')
df = df.explode('basket_items')

## Convenient NF1 for basket_items, rsplit items into: 'item', 'price'
df[['item', 'item_price']] = df['basket_items'].str.rsplit(' - ', n=1, expand=True)

## Further split 'size', 'product/drink'
df[['item_size', 'item_name']] = df['item'].str.split(' ', n=1, expand=True)

# is more splits meaningful? (probably not)

## New processed table, drop 'item' as it is processed?
#df_processed = df.drop(['store_name','basket_items', 'item'], axis=1)

# inspect
print(f"Exploded df in 1NF has {df.shape[0]} rows")
df.head(10)

## stores table needs to have: store_id, store_name
stores_table = pd.DataFrame(df[['store_name']]).drop_duplicates(subset='store_name', keep='first')
stores_table['store_id'] = stores_table.astype(str).sum(1).apply(lambda x: shake_256(x.encode()).hexdigest(5))

# Inspect
stores_table

## Orders table needs to have: order_id, timestamp, store_id, total_price, payment_type
# Stretch: hashed customer_name, hashed card_number
orders_table = pd.DataFrame(df[['order_id', 'timestamp', 'store_name', 'total_price', 'payment_type']]).drop_duplicates(ignore_index=True)

# Merge store_id with respective store_name in orders_table
orders_table = orders_table.merge(stores_table, how='left', on='store_name')

# Drop store_name in orders_table
orders_table.drop('store_name', axis=1, inplace=True)

# Inspect
orders_table

## Products table needs to have: product_id, item_name, item_size, item_price
products_table = pd.DataFrame(df[['item_name', 'item_size', 'item_price']]).drop_duplicates(ignore_index=True)

# new column: products_id is a hash of concatenated strings of row values. may not require after drop_duplicates
products_table['product_id'] = products_table.astype(str).sum(1).apply(lambda x: shake_256(x.encode()).hexdigest(8))

# Inspect
products_table

## orders_products table has: order_id, product_id, quantity
orders_products = df.drop(['timestamp', 'store_name', 'basket_items', 'total_price', 'payment_type', 'item'], axis=1)

# Merge item_price, item_size, and item_price with products_id in products_table
orders_products = orders_products.merge(products_table, on=['item_price', 'item_size', 'item_name'], how="left")

# Collapse repeated rows by grouping and counting duplicates with chained size() method
# https://stackoverflow.com/questions/35584085/how-to-count-duplicate-rows-in-pandas-dataframe
orders_products = orders_products.groupby(orders_products.columns.tolist(), as_index=False).size()

# Drop 'item_price', 'item_size', 'item_name', as merge does not drop them.
orders_products = orders_products.drop(['item_price', 'item_size', 'item_name'], axis=1)

# Rename 'size' to 'quantity'
orders_products.rename(columns={'size':'quantity'}, inplace=True)

# Inspect
more_than_zero = orders_products.value_counts().sum()
more_than_one = orders_products.loc[orders_products['quantity'] > 1].value_counts().sum()
more_than_two = orders_products.loc[orders_products['quantity'] > 2].value_counts().sum()

print(f"orders_products rows with quantity > 0: {more_than_zero}\norders_products rows with quantity > 1: {more_than_one}\norders_products rows with quantity > 2: {more_than_two}\n")
orders_products


### Unittests

##TODO unittest timestamp conversion assert
#df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

##TODO Assert corresponding order_id and product_id relates to the correct quantity - just started..
check_order = orders_products.iloc[0]['order_id']
check_product = orders_products.iloc[0]['product_id']

fetched_product = products_table.loc[products_table['product_id'] == check_product]
fetched_order = orders_table.loc[orders_table['order_id'] == check_order]


###To SQL script
def send_df(tablename, dataframe, indexing=None):    
    # Database SQLAlchemy engine
    engine = create_engine(f'postgresql+psycopg2://root:password@localhost/postgres')
    
    # Sets indexing of df to push to db
    if indexing == None:
        index_bool = False
    else:
        indexing = indexing
        index_bool = True
    
    dataframe.to_sql(name=tablename, con=engine, if_exists='append', index=index_bool, index_label=indexing, dtype={'timestamp': ts(timezone=False)})

    # Close engine and connection - does engine auto-close connections and its pooled connection(s)?
    engine.dispose()

send_df("stores", stores_table)
send_df("orders", orders_table)
send_df("products", products_table)
send_df("orders_products", orders_products)