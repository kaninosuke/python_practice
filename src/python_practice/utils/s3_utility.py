
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional, Union, List, Dict, Any
import logging
import os
from ..errors import S3ServiceError

logger = logging.getLogger(__name__)

# Constants for S3 Utility

DEFAULT_S3_MAX_RETRIES = 3
S3_INITIAL_ATTEMPT_COUNT = 1
DEFAULT_S3_ENCODING = 'utf-8'
DEFAULT_S3_CONTENT_TYPE = 'text/plain'


class S3Utility:

    def __init__(self, region_name: Optional[str] = None, max_retries: Optional[int] = None):

        # Priority Logic: Argument > Environment Variable > Default
        if max_retries is None:
            env_val = os.environ.get('S3_MAX_RETRIES')
            if env_val is not None:
                try:
                    max_retries = int(env_val)
                except ValueError:
                    logger.warning(f"Invalid S3_MAX_RETRIES value '{env_val}'. Falling back to default ({DEFAULT_S3_MAX_RETRIES}).")
                    max_retries = DEFAULT_S3_MAX_RETRIES
            else:
                max_retries = DEFAULT_S3_MAX_RETRIES

        config = Config(
            retries={
                'max_attempts': max_retries + S3_INITIAL_ATTEMPT_COUNT,
                'mode': 'standard'
            }
        )
        self.s3_client = boto3.client('s3', region_name=region_name, config=config)

    def get_object_as_string(self, bucket_name: str, object_key: str, encoding: str = DEFAULT_S3_ENCODING) -> Optional[str]:

        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            body = response['Body'].read()
            return body.decode(encoding)
        except ClientError as e:
            raise S3ServiceError(f"Failed to get object {object_key} from S3") from e
        except Exception as e:
            raise S3ServiceError("An unexpected error occurred during S3 GET") from e

    def put_string_to_s3(self, bucket_name: str, object_key: str, content: str, content_type: str = DEFAULT_S3_CONTENT_TYPE, encoding: str = DEFAULT_S3_ENCODING) -> bool:

        try:
            body = content.encode(encoding)
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=body,
                ContentType=content_type
            )
            logger.info(f"Successfully uploaded string to s3://{bucket_name}/{object_key}")
            return True
        except ClientError as e:
            raise S3ServiceError(f"Failed to upload string to S3: {object_key}") from e
        except Exception as e:
            raise S3ServiceError("An unexpected error occurred during S3 string PUT") from e

    def put_file_to_s3(self, bucket_name: str, object_key: str, file_path: str) -> bool:

        if not os.path.exists(file_path):
            raise S3ServiceError(f"File not found: {file_path}")


        try:
            self.s3_client.upload_file(file_path, bucket_name, object_key)
            logger.info(f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_key}")
            return True
        except ClientError as e:
            raise S3ServiceError(f"Failed to upload file to S3: {file_path}") from e
        except Exception as e:
            raise S3ServiceError("An unexpected error occurred during S3 file upload") from e
