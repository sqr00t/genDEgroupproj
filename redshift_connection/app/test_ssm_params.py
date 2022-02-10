#import boto3
from json import loads as j_conv
import datetime

response = {
    'Parameters': [
        {
            'Name': 'team3_creds',
            'Type': 'SecureString',
            'Value': '{\n"host": "testhost",\n"port": 5439,\n"password": "testpassword",\n"user": "team3"\n}',
            'Version': 1,
            'LastModifiedDate': datetime.datetime(2022, 2, 2, 14, 32, 7, 758000),
            'ARN': 'arn:aws:ssm:eu-west-1:696036660875:parameter/team3_creds', 'DataType': 'text'
            }
        ]
    }

def test_get_parameters():
    """tests whether selection from response is desired json string of credentials"""
    # mocked response
    mocked_response = response

    # Expected
    expected = '{\n"host": "testhost",\n"port": 5439,\n"password": "testpassword",\n"user": "team3"\n}'

    # Actual
    actual = mocked_response['Parameters'][0]['Value']

    # assert response manipulation == params
    assert actual == expected

def test_json_conversion():
    """test desired json parameters converted to python dictionary that we can further manipulate"""
    # mocked output json paramaters
    params = response['Parameters'][0]['Value']

    # Expected
    expected = {
        "host": "testhost",
        "port": 5439,
        "user": "team3",
        "password": "testpassword"
    }

    # Actual
    actual = j_conv(params)

    assert actual == expected

def test_params_host():
    """tests splicing of creds host value"""
    assert False

def test_params_port():
    """tests splicing of creds port value"""
    assert False

def test_params_user():
    """tests splicing of creds user value"""
    assert False

def test_params_password():
    """tests splicing of creds password value"""
    assert False
