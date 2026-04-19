from .utils import S3Utility, RdsUtility

def main():
    s3 = S3Utility()
    print("main.py: S3Utility successfully imported from utils.")

    # s3_content = s3.get_object_as_string('my-bucket', 'test.txt')

    # RdsUtility Sample
    # rds = RdsUtility(resource_aws_arn='arn...', secret_aws_arn='arn...', database='my_db')

    # rows = rds.execute_select("SELECT * FROM users LIMIT 10")
    # print(f"RDS rows: {rows}")
    print("main.py: RdsUtility sample added (commented out).")

if __name__ == "__main__":
    main()
