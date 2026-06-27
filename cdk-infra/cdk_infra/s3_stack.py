from aws_cdk import (
    # Duration,
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
)
from constructs import Construct

class S3BucketStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, workspace_name: str, pipeline_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.workspace_bucket = s3.Bucket(
            self, "WorkspaceBucket",
            bucket_name=workspace_name,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        self.pipeline_bucket = s3.Bucket(
            self, "PipelineBucket",
            bucket_name=pipeline_name,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

