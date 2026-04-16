
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import List, Dict, Any, Optional
import logging
import os
from ..errors import RDSServiceError

logger = logging.getLogger(__name__)

# Constants for RDS Utility
DEFAULT_RDS_MAX_RETRIES = 3
RDS_INITIAL_ATTEMPT_COUNT = 1


class RdsUtility:

    def __init__(self, resource_aws_arn: str, secret_aws_arn: str, database: str, region_name: Optional[str] = None, max_retries: Optional[int] = None):

        # Priority Logic: Argument > Environment Variable > Default
        if max_retries is None:
            env_val = os.environ.get('RDS_MAX_RETRIES')
            if env_val is not None:
                try:
                    max_retries = int(env_val)
                except ValueError:
                    logger.warning(f"Invalid RDS_MAX_RETRIES value '{env_val}'. Falling back to default ({DEFAULT_RDS_MAX_RETRIES}).")
                    max_retries = DEFAULT_RDS_MAX_RETRIES
            else:
                max_retries = DEFAULT_RDS_MAX_RETRIES

        config = Config(
            retries={
                'max_attempts': max_retries + RDS_INITIAL_ATTEMPT_COUNT,
                'mode': 'standard'
            }
        )
        self.rds_client = boto3.client('rds-data', region_name=region_name, config=config)
        self.resource_aws_arn = resource_aws_arn
        self.secret_aws_arn = secret_aws_arn
        self.database = database

    def execute_select(self, sql: str) -> List[Dict[str, Any]]:

        try:
            response = self.rds_client.execute_statement(
                resourceArn=self.resource_aws_arn,
                secretArn=self.secret_aws_arn,
                database=self.database,
                sql=sql,
                includeResultMetadata=True
            )
            
            return self._parse_response(response)

        except ClientError as e:
            raise RDSServiceError(f"Failed to execute RDS query: {sql}") from e
        except Exception as e:
            raise RDSServiceError("An unexpected error occurred during RDS SELECT") from e

    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:

        if 'records' not in response or 'columnMetadata' not in response:
            return []

        column_names = [col['name'] for col in response['columnMetadata']]
        results = []

        for record in response['records']:
            row = {}
            for i, value_dict in enumerate(record):
                column_name = column_names[i]
                # RDS Data API returns values in a dict with a single key representing the type
                # e.g., {'stringValue': 'example'} or {'longValue': 123} or {'isNull': True}
                val = None
                if 'isNull' not in value_dict or not value_dict['isNull']:
                    # Extract the first available value
                    val = next(iter(value_dict.values()))
                row[column_name] = val
            results.append(row)

        return results
