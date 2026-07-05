import os
import json
import boto3

runtime = boto3.client("sagemaker-runtime")

ENDPOINT_NAME = os.environ["ENDPOINT_NAME"]


def lambda_handler(event, context):

    payload = json.dumps(event)

    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=payload
    )

    prediction = json.loads(
        response["Body"].read().decode("utf-8")
    )

    return {
        "statusCode": 200,
        "body": prediction
    }