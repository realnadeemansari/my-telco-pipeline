from aws_cdk import (
    # Duration,
    RemovalPolicy,
    Stack,
    Aws,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ssm as ssm
)
from constructs import Construct


class S3BucketStack(Stack):

    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            workspace_name: str, 
            pipeline_name: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.s3_vpc_endpoint_id = ssm.StringParameter.value_for_string_parameter(
            self,
            "/telco-churn/network/s3-gateway-endpoint-id"
        )
        self.sagemaker_execution_role_arn = ssm.StringParameter.value_for_string_parameter(
            self,
            "/telco-churn/sagemaker/exec-role-arn"
        )

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

        # self.workspace_bucket.add_to_resource_policy(
        #     iam.PolicyStatement(
        #         sid="AllowOnlyThroughVpcEndpoint",
        #         effect=iam.Effect.DENY,
        #         actions=["s3:*"],
        #         resources=[
        #             f"{self.workspace_bucket.bucket_arn}",
        #             f"{self.workspace_bucket.bucket_arn}/*"
        #         ],
        #         principals=[iam.AnyPrincipal()],
        #         conditions={
        #             "StringNotEquals": {
        #                 "aws:sourceVpce": self.s3_vpc_endpoint_id
        #             },
        #             "ArnNotEquals": {
        #                "aws:PrincipalArn": self.sagemaker_execution_role_arn
        #             }
        #         }
        #     )
        # )

