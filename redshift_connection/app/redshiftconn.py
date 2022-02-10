import psycopg2, logging#, boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        conn = psycopg2.connect(
            database="team3_cafe",
            user="team3",
            password="86E0cb72-8433-11ec-9900-b29c4ad2293b",
            host="redshiftcluster-bie5pcqdgojl.cje2eu9tzolt.eu-west-1.redshift.amazonaws.com",
            port=5439
            )
        logger.info("Connection test successful!")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(error)
    finally:
        conn.close()
        logger.info("Connection closed.")