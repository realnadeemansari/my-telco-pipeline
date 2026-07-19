import boto3
import traceback
from datetime import datetime

sm_client = boto3.client("sagemaker")
ssm_client = boto3.client("ssm")

MODEL_PACKAGE_GROUP_NAME = ssm_client.get_parameter(Name="/telco-churn/sagemaker/model-package/group-name")["Parameter"]["Value"]
ENDPOINT_NAME = ssm_client.get_parameter(Name="/telco-churn/sagemaker/endpoint/name")["Parameter"]["Value"]
ROLE_ARN = ssm_client.get_parameter(Name="/telco-churn/sagemaker/exec-role-arn")["Parameter"]["Value"]
MODEL_PACKAGE_ARN = ssm_client.get_parameter(Name="/telco-churn/sagemaker/model-package-arn/latest")["Parameter"]["Value"]
# INVOCATION_5XX_ALARM = ssm_client.get_parameter(
#     Name="/telco-churn/cloudwatch/alarm/invocation-5xx"
# )["Parameter"]["Value"]

# LATENCY_ALARM = ssm_client.get_parameter(
#     Name="/telco-churn/cloudwatch/alarm/model-latency"
# )["Parameter"]["Value"]

# network configuration
SUBNET_1_ID = ssm_client.get_parameter(Name="/telco-churn/network/private-subnet-1-id")["Parameter"]["Value"]
SUBNET_2_ID = ssm_client.get_parameter(Name="/telco-churn/network/private-subnet-2-id")["Parameter"]["Value"]
ENDPOINT_SECURITY_GROUP_ID = ssm_client.get_parameter(Name="/telco-churn/network/vpc-endpoint-security-group-id")["Parameter"]["Value"]

model_version_suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
model_name = f"{ENDPOINT_NAME}-model-{model_version_suffix}"
endpoint_config = f"{ENDPOINT_NAME}-config-{model_version_suffix}"

# packages = sm_client.list_model_packages(
#     ModelPackageGroupName=MODEL_PACKAGE_GROUP_NAME,
#     ModelApprovalStatus="Approved",
#     SortBy="CreationTime",
#     SortOrder="Descending",
#     MaxResults=1
# )

# if not packages["ModelPackageSummaryList"]:
#     raise Exception("No approved model found.")
# model_package_arn = packages["ModelPackageSummaryList"][0]["ModelPackageArn"]

describe = sm_client.describe_model_package(
    ModelPackageName=MODEL_PACKAGE_ARN
)
container = describe["InferenceSpecification"]["Containers"][0]

# deployment_config = {
#     "BlueGreenUpdatePolicy": {
#         "TrafficRoutingConfiguration": {
#             "Type": "CANARY",
#             "CanarySize": {
#                 "Type": "CAPACITY_PERCENT",
#                 "Value": 10
#             },
#             "WaitIntervalInSeconds": 300
#         },
#         "TerminationWaitInSeconds": 300,
#         "MaximumExecutionTimeoutInSeconds": 1800
#     },
#     "AutoRollbackConfiguration": {
#         "Alarms": [
#             {
#                 "AlarmName": INVOCATION_5XX_ALARM
#             },
#             {
#                 "AlarmName": LATENCY_ALARM
#             }
#         ]
#     }
# }

try:
    sm_client.create_model(
        ModelName=model_name,
        ExecutionRoleArn=ROLE_ARN,
        Containers=[
            {
                "ModelPackageName": MODEL_PACKAGE_ARN
            }
        ],
        VpcConfig={
            "SecurityGroupIds": [ENDPOINT_SECURITY_GROUP_ID],
            "Subnets": [SUBNET_1_ID, SUBNET_2_ID]
        }
    )
except sm_client.exceptions.ClientError as e:
    tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    print("Error: ", tb)
    print("Model already exists.")

try:
    sm_client.create_endpoint_config(
        EndpointConfigName=endpoint_config,
        ProductionVariants=[
            {
                "VariantName": "Primary",
                "ModelName": model_name,
                "InitialInstanceCount": 2,
                "InstanceType": "ml.m5.large"
            }
        ]
    )
except sm_client.exceptions.ClientError as e:
    tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    print("Error: ", tb)
    print("Endpoint config already exists.")

try:
    sm_client.describe_endpoint(
        EndpointName=ENDPOINT_NAME,
    )
    print("Updating endpoint...")
    sm_client.update_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=endpoint_config,
        # DeploymentConfig=deployment_config
    )
    response = sm_client.describe_endpoint(
        EndpointName=ENDPOINT_NAME
    )
    print(response["EndpointStatus"])
    print(response["EndpointConfigName"])
    print(response["LastModifiedTime"])
    print(response["FailureReason"])
except sm_client.exceptions.ClientError as e:
    tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    print("Error: ", tb)
    print("Creating endpoint...")
    sm_client.create_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=endpoint_config
    )

    print("Deployment started.")

