from aws_cdk import (
    Stack,
    Aws,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_ec2 as ec2
)
from constructs import Construct


class LambdaStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        lambda_role_name: str,
        project_prefix: str,
        endpoint_name: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.vpc_id = ssm.StringParameter.value_for_string_parameter(
            self, "/telco-churn/network/vpc-id"
        )
        self.private_subnet_1 = ssm.StringParameter.value_for_string_parameter(
            self, "/telco-churn/network/private-subnet-1-id"
        )
        self.private_subnet_2 = ssm.StringParameter.value_for_string_parameter(
            self, "/telco-churn/network/private-subnet-2-id"
        )

        self.lambda_security_group = ssm.StringParameter.value_for_string_parameter(
            self, "/telco-churn/network/lambda-security-group-id"
        )
        self.vpc = ec2.Vpc.from_vpc_attributes(
            self,
            "VPC",
            vpc_id=self.vpc_id,
            availability_zones=[f"{Aws.REGION}a", f"{Aws.REGION}b"],
            private_subnet_ids=[self.private_subnet_1, self.private_subnet_2]
        )
        self.lambda_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "LambdaSecurityGroup",
            security_group_id=self.lambda_security_group
        )
        self.lambda_role = iam.Role(
            self,
            "PredictionLambdaRole",
            role_name=lambda_role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                f"{project_prefix}-lambda-logs-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=[
                                f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:*"
                            ]
                        )
                    ]
                ),
                f"{project_prefix}-lambda-sagemaker-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "sagemaker:InvokeEndpoint"
                            ],
                            resources=[
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:endpoint/{endpoint_name}"
                            ]
                        )
                    ]
                ),
                f"{project_prefix}-lambda-network-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ec2:CreateNetworkInterface",
                                "ec2:DescribeNetworkInterfaces",
                                "ec2:DeleteNetworkInterface",
                                "ec2:AssignPrivateIpAddresses",
                                "ec2:UnassignPrivateIpAddresses"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

        self.predict_lambda = _lambda.Function(
            self,
            "PredictLambda",
            function_name=f"{project_prefix}-predict-lambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("./cdk_infra/resources"),
            role=self.lambda_role,
            timeout=Duration.seconds(60),
            vpc=self.vpc,
            security_groups=[self.lambda_security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            environment={
                "ENDPOINT_NAME": endpoint_name
            }
        )

        self.predict_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "sagemaker:InvokeEndpoint"
                ],
                resources=[
                    f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:endpoint/{endpoint_name}"
                ]
            )
        )

        # ssm.StringParameter(
        #     self,
        #     "PredictLambdaArn",
        #     parameter_name="/telco-churn/lambda/predict/arn",
        #     string_value=self.predict_lambda.function_arn
        # )