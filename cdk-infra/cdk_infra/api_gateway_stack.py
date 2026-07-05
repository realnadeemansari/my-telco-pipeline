from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
)
from constructs import Construct


class ApiGatewayStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        predict_lambda: _lambda.IFunction,
        project_prefix: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        api = apigateway.RestApi(
            self,
            "PredictionApi",
            rest_api_name=f"{project_prefix}-prediction-api"
        )

        predict = api.root.add_resource("predict")

        predict.add_method(
            "POST",
            apigateway.LambdaIntegration(predict_lambda)
        )