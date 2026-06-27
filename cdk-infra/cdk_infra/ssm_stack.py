from aws_cdk import (
    Stack,
    aws_ssm as ssm,
)
from constructs import Construct

class SSMStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SSM parameters
        self.workspace_bucket = ssm.StringParameter(
            self, "WorkspaceBucketNameParameter",
            parameter_name="/telco-churn/s3/workspace-bucket-name",
            string_value="sbx-tsp-telco-customer-churn-workspace"
        )
        self.pipeline_bucket = ssm.StringParameter(
            self, "PipelineBucketNameParameter",
            parameter_name="/telco-churn/s3/pipeline-bucket-name",
            string_value="sbx-tsp-telco-customer-churn-pipeline"
        )
        self.bucket_prefix = ssm.StringParameter(
            self, "BucketPrefixParameter",
            parameter_name="/telco-churn/s3/bucket-prefix",
            string_value="telco-pipeline"
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

