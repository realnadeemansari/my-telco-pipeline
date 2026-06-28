from aws_cdk import (
    Stack,
    aws_iam as iam,
    CfnOutput,
    Aws
)
from constructs import Construct

class IAMStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            s3_auto_delete_role_name,
            pipeline_bucket,
            workspace_bucket,
            project_prefix,
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
                f"{project_prefix}-s3-auto-delete-s3-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:DeleteObject*",
                                "s3:GetBucket*",
                                "s3:List*",
                                "s3:PutBucketPolicy"
                            ],
                            resources=[
                                f"arn:aws:s3:::{pipeline_bucket}",
                                f"arn:aws:s3:::{pipeline_bucket}/*",
                                f"arn:aws:s3:::{workspace_bucket}",
                                f"arn:aws:s3:::{workspace_bucket}/*"
                            ]
                        )
                    ]
                )
            }
        )