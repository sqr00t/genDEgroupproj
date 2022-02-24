import logging, redshift_connector
from boto3 import client
from json import loads as json_to_dict
from contextlib import closing

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def s3filename_to_tablename(s3_filename):
    return s3_filename.replace('.csv', ',').split(',')[1]

def insert_csv_redshift(table_name: str, filename: str):    
    ## Get credentials from parameter store
    ssm_client = client("ssm")
    redshift_parameters = ssm_client.get_parameters(
        Names=["team3_creds"],
        WithDecryption=True)

    # deconstruct json parameters to get required details
    cred_dict = json_to_dict(redshift_parameters['Parameters'][0]['Value'])

    with closing(
        redshift_connector.connect(
            database="team3_cafe",
            user=cred_dict['user'],
            password=cred_dict['password'],
            host=cred_dict['host'],
            port=cred_dict['port']
            )
        ) as conn:
        with closing(conn.cursor()) as cursor:
            conn.autocommit = True
            if table_name == "_ordersproducts":
                statements = [f"CREATE TEMP TABLE staging (LIKE deployment.orders_products);",
                             (f"COPY staging FROM 's3://team3-demo-processed/{filename}'"
                               "IAM_ROLE 'arn:aws:iam::696036660875:role/RedshiftS3Role'"
                               "FORMAT AS CSV DELIMITER ',' "
                               "REGION AS 'eu-west-1';"),
                              """
                              INSERT INTO deployment.orders_products
                                SELECT * FROM staging
                                WHERE (staging.order_id,staging.product_id) NOT IN (
                                SELECT DISTINCT order_id,product_id FROM deployment.orders_products);
                              """,
                               "DROP TABLE staging"]

            elif table_name == "_stores":
                statements = ["CREATE TEMP TABLE staging (LIKE deployment.stores);",
                            (f"COPY staging FROM 's3://team3-demo-processed/{filename}'"
                              "IAM_ROLE 'arn:aws:iam::696036660875:role/RedshiftS3Role'"
                              "FORMAT AS CSV DELIMITER ',' "
                              "REGION AS 'eu-west-1';"),
                              """
                              INSERT INTO deployment.stores
                                SELECT * FROM staging
                                WHERE staging.store_id NOT IN (
                                SELECT DISTINCT store_id FROM deployment.stores);
                              """,
                              "DROP TABLE staging"]

            elif table_name == "_products":
                statements = ["CREATE TEMP TABLE staging (LIKE deployment.products);",
                            (f"COPY staging FROM 's3://team3-demo-processed/{filename}'"
                              "IAM_ROLE 'arn:aws:iam::696036660875:role/RedshiftS3Role'"
                              "FORMAT AS CSV DELIMITER ',' "
                              "REGION AS 'eu-west-1';"),
                              """
                              INSERT INTO deployment.products
                                SELECT * FROM staging
                                WHERE staging.product_id NOT IN (
                                SELECT DISTINCT product_id FROM deployment.products);
                              """,
                              "DROP TABLE staging"]

            elif table_name == "_orders":
                statements = ["CREATE TEMP TABLE staging (LIKE deployment.orders);",
                            (f"COPY staging FROM 's3://team3-demo-processed/{filename}'"
                              "IAM_ROLE 'arn:aws:iam::696036660875:role/RedshiftS3Role'"
                              "FORMAT AS CSV DELIMITER ',' "
                              "REGION AS 'eu-west-1';"),
                              """
                              INSERT INTO deployment.orders
                                SELECT * FROM staging
                                WHERE staging.order_id NOT IN (
                                SELECT DISTINCT order_id FROM deployment.orders);
                              """,
                              "DROP TABLE staging"]
            else: logger.info(f"Invalid table: {table_name[1:]}")

            try:
                cursor.execute('SET search_path TO deployment;')
                for statement in statements:
                    cursor.execute(statement)
                logger.info("Successfully inserted")
            except (Exception, redshift_connector.DatabaseError) as e:
                raise e