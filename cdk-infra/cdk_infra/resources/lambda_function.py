import os
import json
import boto3
# import urllib.request

runtime = boto3.client("sagemaker-runtime")

ENDPOINT_NAME = os.environ["ENDPOINT_NAME"]


def lambda_handler(event, context):
    print("Inside the Lambda function")
    # with urllib.request.urlopen("https://api.ipify.org") as response:
    #     ip = response.read().decode("utf-8")
    # print(f"Lambda function invoked from IP address: {ip}")

    payload = event["body"]

    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=payload
    )
    prediction = json.loads(
        response["Body"].read().decode("utf-8")
    )
    res = {
        "prediction": prediction,
        # "nat_response": f"Lambda function invoked from IP address: {ip}"
    }

    return {
        "statusCode": 200,
        "body": json.dumps(res)
    }