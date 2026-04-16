import os
import pytest
import boto3
from moto import mock_aws

@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="session")
def s3_client(aws_credentials):
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")
