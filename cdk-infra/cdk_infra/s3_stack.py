from aws_cdk import (
    # Duration,
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
    aws_iam as iam
)
from constructs import Construct

class S3BucketStack(Stack):

    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            workspace_name: str, 
            pipeline_name: str, 
            s3_auto_delete_role_name: str,
            project_prefix: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.s3_auto_delete_role = iam.Role(
            self,
            "S3AutoDeleteRole",
            role_name=s3_auto_delete_role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                f"{project_prefix}-s3-auto-delete-logs-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=["arn:aws:logs:*:*:*"]
                        )
                    ]
                ),
            }
        )

        self.workspace_bucket = s3.Bucket(
            self, "WorkspaceBucket",
            bucket_name=workspace_name,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        self.workspace_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ArnPrincipal(self.s3_auto_delete_role.role_arn)],
                actions=[
                    "s3:DeleteObject*",
                    "s3:GetBucket*",
                    "s3:List*",
                    "s3:PutBucketPolicy",
                ],
                resources=[
                    self.workspace_bucket.bucket_arn,
                    f"{self.workspace_bucket.bucket_arn}/*",
                ],
            )
        )

        self.pipeline_bucket = s3.Bucket(
            self, "PipelineBucket",
            bucket_name=pipeline_name,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        self.pipeline_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ArnPrincipal(self.s3_auto_delete_role.role_arn)],
                actions=[
                    "s3:DeleteObject*",
                    "s3:GetBucket*",
                    "s3:List*",
                    "s3:PutBucketPolicy",
                ],
                resources=[
                    self.pipeline_bucket.bucket_arn,
                    f"{self.pipeline_bucket.bucket_arn}/*",
                ],
            )
        )

