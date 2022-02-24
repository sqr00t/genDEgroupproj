import logging
from inserter import insert_csv_redshift

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(event)
    s3_file_name = event['Records'][0]['s3']['object']['key']

    insert_csv_redshift('products', s3_file_name)