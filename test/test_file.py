import boto3
from moto import mock_s3
import os, pytest

## setup
test_bucket='test_bucket'
test_s3_file='test.csv'

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

def mock_file_creation(credentials):
    # define s3client actions
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket=test_bucket)
    s3_client.put_object(Bucket=test_bucket, Key=test_s3_file, Body='')

def dl(src_f, dest_f):
    s3 = boto3.resource('s3')
    s3.Bucket(test_bucket).download_file(src_f, dest_f)
  
##tests
@mock_s3
def test_dl():
    s3 = boto3.client('s3', region_name='us-east-1')
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    s3.create_bucket(Bucket=test_bucket)

    s3.put_object(Bucket=test_bucket, Key=test_s3_file, Body='')
    dl(test_s3_file, test_s3_file)

    assert os.path.isfile(test_s3_file)

@mock_s3
def test_dl_file_from_s3():
    """https://stackoverflow.com/questions/58564394/mock-boto3-response-for-downloading-file-from-s3"""
    # define resources
    mock_file_creation(aws_credentials)
    s3_resource = boto3.resource("s3")

    # test action
    s3_resource.meta.client.download_file(test_bucket, test_s3_file, f'/tmp/{test_s3_file}')

    # assert file downloaded
    assert os.path.isfile('/tmp/test.csv')
