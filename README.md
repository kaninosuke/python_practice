# Python Practice Project

This project provides robust utilities for interacting with AWS S3 and RDS (via Data API).

## Features

- **S3Utility**: String operations and file uploads with exponential backoff.
- **RdsUtility**: PostgreSQL SELECT operations using RDS Data API with exponential backoff.
- **Custom Error Handling**: Consistent error classes (`S3ServiceError`, `RDSServiceError`).

## Environment Variables

The following environment variables can be used to customize the behavior:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `S3_MAX_RETRIES` | Max retry attempts for S3 operations. | `3` |
| `RDS_MAX_RETRIES` | Max retry attempts for RDS operations. | `3` |

### Priority Order
For `max_retries` configuration, the priority is:
1.  **Constructor Argument**: Passed directly when initializing the utility.
2.  **Environment Variable**: Set in the OS/shell environment.
3.  **Default Value**: Fixed at `3` if neither of the above is provided.

## Usage

### S3 Utility
```python
from python_practice import S3Utility

s3 = S3Utility(region_name='us-east-1')
content = s3.get_object_as_string('my-bucket', 'path/to/key')
```

### RDS Utility
```python
from python_practice import RdsUtility

rds = RdsUtility(
    resource_aws_arn='arn:aws:rds:...',
    secret_aws_arn='arn:aws:secretsmanager:...',
    database='my_db'
)
rows = rds.execute_select("SELECT * FROM table")
```

## Setup

1. Create a virtual environment: `python -m venv .venv`
2. Install dependencies: `pip install -e .`

## Testing

To run the unit tests, you first need to install the testing dependencies:

```bash
pip install -e ".[test]"
```

Then, run the tests using `pytest`:

```bash
pytest
```

The tests use `moto` (for S3) and `unittest.mock` (for RDS) to simulate AWS services, so no real AWS credentials are required to run them.
