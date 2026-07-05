from aws_cdk import (
    Stack,
    aws_ssm as ssm,
)
from constructs import Construct

class SSMStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project_prefix, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        

        # Create SSM parameters
        self.workspace_bucket = ssm.StringParameter(
            self, "WorkspaceBucketNameParameter",
            parameter_name="/telco-churn/s3/workspace-bucket-name",
            string_value=f"{project_prefix}-s3-workspace"
        )
        self.pipeline_bucket = ssm.StringParameter(
            self, "PipelineBucketNameParameter",
            parameter_name="/telco-churn/s3/pipeline-bucket-name",
            string_value=f"{project_prefix}-s3-pipeline"
        )
        self.bucket_prefix = ssm.StringParameter(
            self, "BucketPrefixParameter",
            parameter_name="/telco-churn/s3/bucket-prefix",
            string_value="telco-pipeline"
        )
        self.project_prefix = ssm.StringParameter(
            self, "ProjectPrefixParameter",
            parameter_name="/telco-churn/pipeline/project-prefix",
            string_value=f"{project_prefix}"
        )
        self.s3_auto_delete_role_name = ssm.StringParameter(
            self, "BucketAutoDeleteS3RoleParameter",
            parameter_name="/telco-churn/s3/iam/auto-delete/role-name",
            string_value=f"{project_prefix}-s3-auto-delete-role"
        )
        self.pipeline_name = ssm.StringParameter(
            self, "PipelineNameParameter",
            parameter_name="/telco-churn/pipeline/pipeline-name",
            string_value=f"{project_prefix}-pipeline"
        )
        self.pipeline_iam_role_name = ssm.StringParameter(
            self, "PipelineIamRoleParameter",
            parameter_name="/telco-churn/pipeline/iam/role-name",
            string_value=f"{project_prefix}-pipeline-role"
        )
        self.build_project_name = ssm.StringParameter(
            self, "BuildProjectNameParameter",
            parameter_name="/telco-churn/build/project-name",
            string_value=f"{project_prefix}-build"
        )
        self.build_iam_role_name = ssm.StringParameter(
            self, "BuildIamRoleParameter",
            parameter_name="/telco-churn/build/iam/role-name",
            string_value=f"{project_prefix}-codebuild-role"
        )
        self.model_package_group_name = ssm.StringParameter(
            self, "ModelPackageGroupNameParameter",
            parameter_name="/telco-churn/sagemaker/model-package/group-name",
            string_value=f"{project_prefix}-model-package"
        )
        self.endpoint_name = ssm.StringParameter(
            self, "EndpointNameParameter",
            parameter_name="/telco-churn/sagemaker/endpoint/name",
            string_value=f"{project_prefix}"
        )
        self.sfn_state_machine_name = ssm.StringParameter(
            self, "SfnStateMachineNameParameter",
            parameter_name="/telco-churn/step-function/state-machine/workflow-name",
            string_value=f"{project_prefix}-sfn-state-machine-workflow"
        )
        self.sfn_state_machine_role_name = ssm.StringParameter(
            self, "SfnStateMachineRoleNameParameter",
            parameter_name="/telco-churn/step-function/state-machine/role-name",
            string_value=f"{project_prefix}-sfn-state-machine-role"
        )
        self.sagemaker_exec_role_name = ssm.StringParameter(
            self, "SagemakerExecRoleNameParameter",
            parameter_name="/telco-churn/sagemaker/exec-role-name",
            string_value=f"{project_prefix}-sagemaker-exec-role"
        )
        self.lambda_role_name = ssm.StringParameter(
            self, "LambdaRoleNameParameter",
            parameter_name="/telco-churn/lambda/role-name",
            string_value=f"{project_prefix}-lambda-role"
        )
        self.github_owner = ssm.StringParameter(
            self, "GitHubOwnerParameter",
            parameter_name="/telco-churn/github/owner",
            string_value="realnadeemansari"
        )
        self.github_repo = ssm.StringParameter(
            self, "GitHubRepoParameter",
            parameter_name="/telco-churn/github/repo",
            string_value="my-telco-pipeline"
        )
        self.github_branch = ssm.StringParameter(
            self, "GitHubBranchParameter",
            parameter_name="/telco-churn/github/branch",
            string_value="main"
        )

