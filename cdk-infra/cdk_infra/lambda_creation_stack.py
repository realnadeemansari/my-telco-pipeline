from aws_cdk import (
    Stack,
    Aws,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_ssm as ssm,
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