from aws_cdk import (
    Stack,
    Aws,
    aws_iam as iam,
    aws_ssm as ssm
)
from constructs import Construct


class SageMakerRoleStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        role_name: str,
        workspace_bucket: str,
        project_prefix: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.sagemaker_role = iam.Role(
            self,
            "SageMakerExecutionRole",
            role_name=role_name,
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            inline_policies={
                f"{project_prefix}-sm-s3-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:DeleteObject",
                                "s3:ListBucket",
                                "s3:GetBucketLocation",
                                "s3:GetBucketAcl"
                            ],
                            resources=[
                                f"arn:aws:s3:::{workspace_bucket}",
                                f"arn:aws:s3:::{workspace_bucket}/*"
                            ],
                        )
                    ]
                ),
                f"{project_prefix}-sm-logs-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=[f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:/aws/sagemaker/*"],
                        )
                    ]
                ),
                f"{project_prefix}-sm-ecr-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage"
                            ],
                            resources=[f"arn:aws:ecr:{Aws.REGION}:{Aws.ACCOUNT_ID}:repository/{project_prefix}*"],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "ecr:GetAuthorizationToken"
                            ],
                            resources=["*"],
                        )
                    ]
                ),
                f"{project_prefix}-sm-network-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ec2:CreateNetworkInterface",
                                "ec2:DescribeNetworkInterfaces",
                                "ec2:DeleteNetworkInterface",
                                "ec2:AssignPrivateIpAddresses",
                                "ec2:UnassignPrivateIpAddresses",
                                "ec2:DescribeSubnets",
                                "ec2:DescribeSecurityGroups",
                                "ec2:DescribeVpcs",
                                "ec2:DescribeDhcpOptions",
                                "ec2:DescribeVpcEndpoints",
                                "ec2:DescribeAvailabilityZones"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
                
        )

        ####################################################
        # Put SSM Params
        ####################################################

        self.sagemaker_exec_role_arn = ssm.StringParameter(
            self,
            "SageMakerExecRoleArn",
            parameter_name="/telco-churn/sagemaker/exec-role-arn",
            string_value=self.sagemaker_role.role_arn,
        )