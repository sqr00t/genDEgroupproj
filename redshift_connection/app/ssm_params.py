import psycopg2, logging, boto3
from json import loads as conv_json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    ssm_client = boto3.client("ssm")

    # get creds from ssm paramaters
    # ssm:GetParameters and ssm:GetParametersByPath permissions required
    # or ssm:GetParameter for ssm_client.get_parameter()
    # would it be possible with only ssm:GetParameterByPath ? change to use get_parameter?
    redshift_parameters = ssm_client.get_parameters(
        Names=["team3_creds"],
        WithDecryption=True)

    # log dict of creds
    logger.info(f"delete this log after test: {redshift_parameters}")

    # deconstruct json parameters to required details
    cred_string = redshift_parameters['Parameters'][0]['Value'] # gets the credentials but has \n

    # convert cred_string json to dict
    cred_dict = conv_json(cred_string)

    try:
        conn = psycopg2.connect(
            database="team3_cafe",
            user=cred_dict['user'],
            password=cred_dict['password'],
            host=cred_dict['host'],
            port=cred_dict['port']
            )
        logger.info("Connection test successful!")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(error)
    finally:
        if conn:
            conn.close()
            logger.info("Connection closed.")
        else:
            logger.info("Failed to connect.")
