import pytest
import os
from moto import mock_aws
from python_practice import S3Utility, S3ServiceError

@mock_aws
class TestS3Utility:
    def test_put_and_get_string(self):
        s3_util = S3Utility(region_name="us-east-1")
        bucket = "test-bucket"
        key = "test.txt"
        content = "hello world"
        
        # Setup: Create bucket
        s3_util.s3_client.create_bucket(Bucket=bucket)
        
        # Test put
        success = s3_util.put_string_to_s3(bucket, key, content)
        assert success is True
        
        # Test get
        retrieved = s3_util.get_object_as_string(bucket, key)
        assert retrieved == content

    def test_put_file_to_s3(self, tmp_path):
        s3_util = S3Utility(region_name="us-east-1")
        bucket = "test-bucket"
        key = "test-file.txt"
        
        # Setup: Create bucket and local file
        s3_util.s3_client.create_bucket(Bucket=bucket)
        local_file = tmp_path / "hello.txt"
        local_file.write_text("file content")
        
        # Test put_file
        success = s3_util.put_file_to_s3(bucket, key, str(local_file))
        assert success is True
        
        # Verify content
        retrieved = s3_util.get_object_as_string(bucket, key)
        assert retrieved == "file content"

    def test_put_file_not_found(self):
        s3_util = S3Utility(region_name="us-east-1")
        with pytest.raises(S3ServiceError, match="File not found"):
            s3_util.put_file_to_s3("bucket", "key", "non_existent_file.txt")

    def test_s3_service_error_on_get(self):
        s3_util = S3Utility(region_name="us-east-1")
        # Bucket not created yet, should raise S3ServiceError
        with pytest.raises(S3ServiceError):
            s3_util.get_object_as_string("no-bucket", "key")
