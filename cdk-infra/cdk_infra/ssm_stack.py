from aws_cdk import (
    Stack,
    aws_ssm as ssm,
)
from constructs import Construct
from datetime import datetime

def get_current_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

class SSMStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SSM parameters
        self.workspace_bucket = ssm.StringParameter(
            self, "WorkspaceBucketNameParameter",
            parameter_name="/telco-churn/s3/workspace-bucket-name",
            string_value="telco-customer-churn-workspace-" + get_current_timestamp()
        )
        self.pipeline_bucket = ssm.StringParameter(
            self, "PipelineBucketNameParameter",
            parameter_name="/telco-churn/s3/pipeline-bucket-name",
            string_value="telco-customer-churn-pipeline-" + get_current_timestamp()
        )
        self.bucket_prefix = ssm.StringParameter(
            self, "BucketPrefixParameter",
            parameter_name="/telco-churn/s3/bucket-prefix",
            string_value="telco-pipeline"
        )
        self.region = ssm.StringParameter(
            self, "RegionParameter",
            parameter_name="/telco-churn/region",
            string_value="us-east-1"
        )
        self.project_prefix = ssm.StringParameter(
            self, "ProjectPrefixParameter",
            parameter_name="/telco-churn/project-prefix",
            string_value="telco-churn"
        )
        self.pipeline_name = ssm.StringParameter(
            self, "PipelineNameParameter",
            parameter_name="/telco-churn/pipeline-name",
            string_value="TelcoChurnPipeline"
        )
        self.model_package_group_name = ssm.StringParameter(
            self, "ModelPackageGroupNameParameter",
            parameter_name="/telco-churn/model-package-group-name",
            string_value="telco-churn-model-package"
        )
        self.github_owner = ssm.StringParameter(
            self, "GitHubOwnerParameter",
            parameter_name="/telco-churn/github-owner",
            string_value="realnadeemansari"
        )
        self.github_repo = ssm.StringParameter(
            self, "GitHubRepoParameter",
            parameter_name="/telco-churn/github-repo",
            string_value="my-telco-pipeline"
        )
        self.github_branch = ssm.StringParameter(
            self, "GitHubBranchParameter",
            parameter_name="/telco-churn/github-branch",
            string_value="main"
        )

