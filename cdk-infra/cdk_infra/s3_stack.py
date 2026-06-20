from aws_cdk import (
    # Duration,
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
)
from constructs import Construct
from datetime import datetime

class S3BucketStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        test_bucket = s3.Bucket(
            self, "TestBucket",
            bucket_name="test-bucket-" + datetime.now().strftime("%Y%m%d%H%M%S"),
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
