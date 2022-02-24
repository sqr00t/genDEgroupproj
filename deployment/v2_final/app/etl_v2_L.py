import logging
from InserterDemo import insert_csv_redshift, s3filename_to_tablename

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(event)
    s3_file_name = event['Records'][0]['s3']['object']['key']
    table_name = s3filename_to_tablename(s3_file_name)
    
    insert_csv_redshift(table_name, s3_file_name)