# Solution 1

import pandas_redshift as pr

pr.connect_to_redshift(dbname = "team3_cafe",
                        host = "redshiftcluster-bie5pcqdgojl.cje2eu9tzolt.eu-west-1.redshift.amazonaws.com",
                        port = 5439,
                        user = "team3",
                        password = "86E0cb72-8433-11ec-9900-b29c4ad2293b")

pr.pandas_to_redshift(data_frame = df,
                        redshift_table_name = 'sales_data')

# Solution 2

from sqlalchemy import create_engine

 conn = create_engine('postgresql://team3:86E0cb72-8433-11ec-9900-b29c4ad2293b@redshiftcluster-bie5pcqdgojl.cje2eu9tzolt.eu-west-1.redshift.amazonaws.com/team3_cafe')

df.to_sql('sales_data', conn, index=False, if_exists='replace')

# Solution 3 

from red_panda import RedPanda

redshift_conf = {
    "user": "team3:",
    "password": "86E0cb72-8433-11ec-9900-b29c4ad2293b",
    "host": "redshiftcluster-bie5pcqdgojl.cje2eu9tzolt.eu-west-1.redshift.amazonaws.com",
    "port": 5439,
    "dbname": "team3_cafe"
    }

aws_conf = {
    # "aws_access_key_id": "<access_key>",
    # "aws_secret_access_key": "<secret_key>",
    "aws_session_token": "temporary-token-if-you-have-one",
}

rp = RedPanda(redshift_conf, aws_conf)
s3_bucket = "bucketname"
s3_path = "subfolder if any" # optional, if you don't have any sub folders
s3_file_name = "filename" # optional, randomly generated if not provided
rp.df_to_redshift(df, "table_name", bucket=s3_bucket, path=s3_path, append=False)

# solution 4


AWS CLI Command - 

$ aws ssm get-parameters --name team3_creds --with-decryption
{
    "Parameters": [
        {
            "Name": "team3_creds",
            "Type": "SecureString",
            "Value": "{\n\"host\": \"redshiftcluster-bie5pcqdgojl.cje2eu9tzolt.eu-west-1.redshift.amazonaws.com\",\n\"port\": 5439,\n\"password\": \"86E0cb72-8433-11ec-9900-b29c4ad2293b\",\n\"user\": \"team3\"\n}",
            "Version": 1,
            "LastModifiedDate": "2022-02-02T14:32:07.758000+00:00",
            "ARN": "arn:aws:ssm:eu-west-1:696036660875:parameter/team3_creds",
            "DataType": "text"
        }
    ],
    "InvalidParameters": []
}


import json
import boto3
 
ssm_client = boto3.client("ssm")
redshift_parameters = ssm_client.get_parameters(Names=["team3_creds",],
    WithDecryption=False
)