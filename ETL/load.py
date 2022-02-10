from sqlalchemy import create_engine



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

# send_df("stores", stores_table)
# send_df("orders", orders_table)
# send_df("products", products_table)
# send_df("orders_products", orders_products)