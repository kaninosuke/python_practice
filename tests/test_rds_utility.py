import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from python_practice import RdsUtility, RDSServiceError

class TestRdsUtility:
    @patch("boto3.client")
    def test_execute_select_success(self, mock_boto_client):
        # Setup mock client and response
        mock_rds = MagicMock()
        mock_boto_client.return_value = mock_rds
        
        mock_response = {
            "columnMetadata": [
                {"name": "id"},
                {"name": "name"}
            ],
            "records": [
                [{"longValue": 1}, {"stringValue": "Alice"}],
                [{"longValue": 2}, {"stringValue": "Bob"}]
            ]
        }
        mock_rds.execute_statement.return_value = mock_response
        
        # Initialize and test
        rds = RdsUtility(resource_aws_arn="arn:res", secret_aws_arn="arn:sec", database="db")
        results = rds.execute_select("SELECT * FROM users")
        
        # Assertions
        assert len(results) == 2
        assert results[0] == {"id": 1, "name": "Alice"}
        assert results[1] == {"id": 2, "name": "Bob"}
        mock_rds.execute_statement.assert_called_once()

    @patch("boto3.client")
    def test_execute_select_empty(self, mock_boto_client):
        mock_rds = MagicMock()
        mock_boto_client.return_value = mock_rds
        mock_rds.execute_statement.return_value = {}
        
        rds = RdsUtility(resource_aws_arn="arn:res", secret_aws_arn="arn:sec", database="db")
        results = rds.execute_select("SELECT * FROM empty_table")
        
        assert results == []

    @patch("boto3.client")
    def test_execute_select_client_error(self, mock_boto_client):
        mock_rds = MagicMock()
        mock_boto_client.return_value = mock_rds
        
        # Simulate ClientError
        error_response = {"Error": {"Code": "AccessDenied", "Message": "No access"}}
        mock_rds.execute_statement.side_effect = ClientError(error_response, "ExecuteStatement")
        
        rds = RdsUtility(resource_aws_arn="arn:res", secret_aws_arn="arn:sec", database="db")
        with pytest.raises(RDSServiceError, match="Failed to execute RDS query"):
            rds.execute_select("SELECT * FROM secrets")

    @patch("boto3.client")
    def test_parse_response_with_null(self, mock_boto_client):
        mock_rds = MagicMock()
        mock_boto_client.return_value = mock_rds
        
        mock_response = {
            "columnMetadata": [{"name": "note"}],
            "records": [[{"isNull": True}]]
        }
        mock_rds.execute_statement.return_value = mock_response
        
        rds = RdsUtility(resource_aws_arn="arn:res", secret_aws_arn="arn:sec", database="db")
        results = rds.execute_select("SELECT note FROM table")
        
        assert results == [{"note": None}]
