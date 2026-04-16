from ..utils import S3Utility, RdsUtility

def run_some_feature():

    s3 = S3Utility()
    print("foo_module/bar.py: S3Utility successfully imported from utils via relative import.")

    
    # RdsUtility Sample
    # rds = RdsUtility(resource_aws_arn='arn...', secret_aws_arn='arn...', database='my_db')

    # print("foo_module/bar.py: RdsUtility sample added.")

if __name__ == "__main__":
    run_some_feature()
