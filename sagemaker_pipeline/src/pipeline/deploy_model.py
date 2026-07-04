import boto3

sm_client = boto3.client("sagemaker")
ssm_client = boto3.client("ssm")

MODEL_PACKAGE_GROUP_NAME = ssm_client.get_parameter(Name="/telco-churn/sagemaker/model-package/group-name")["Parameter"]["Value"]
ENDPOINT_NAME = ssm_client.get_parameter(Name="/telco-churn/sagemaker/endpoint/name")["Parameter"]["Value"]
ROLE_ARN = ssm_client.get_parameter(Name="/telco-churn/sagemaker/exec-role-name")["Parameter"]["Value"]
MODEL_PACKAGE_ARN = ssm_client.get_parameter(Name="/telco-churn/sagemaker/model-package-arn/latest")["Parameter"]["Value"]

model_name = ENDPOINT_NAME + "-model"
endpoint_config = ENDPOINT_NAME + "-config"

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

try:
    sm_client.create_model(
        ModelName=model_name,
        ExecutionRoleArn=ROLE_ARN,
        Containers=[
            {
                "Image": container["Image"],
                "ModelPackageName": MODEL_PACKAGE_ARN
            }
        ]
    )
except sm_client.exceptions.ClientError:
    print("Model already exists.")

try:
    sm_client.create_endpoint_config(
        EndpointConfigName=endpoint_config,
        ProductionVariants=[
            {
                "VariantName": "Primary",
                "ModelName": model_name,
                "InitialInstanceCount": 1,
                "InstanceType": "ml.m5.large"
            }
        ]
    )
except sm_client.exceptions.ClientError:
    print("Endpoint config already exists.")

try:
    sm_client.describe_endpoint(
        EndpointName=ENDPOINT_NAME,
    )
    print("Updating endpoint...")
    sm_client.update_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=endpoint_config
    )
except sm_client.exceptions.ClientError:
    print("Creating endpoint...")
    sm_client.create_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=endpoint_config
    )

    print("Deployment started.")

    