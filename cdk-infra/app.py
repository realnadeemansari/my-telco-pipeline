#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_infra.s3_stack import S3BucketStack
from cdk_infra.codepipeline_stack import CodePipelineStack
from cdk_infra.ssm_stack import SSMStack
from cdk_infra.codebuild_stack import CodeBuildStack
from cdk_infra.stepfunction_stack import StepFunctionStack
from cdk_infra.sagemaker_exec_role_stack import SageMakerRoleStack
from cdk_infra.model_package_group_stack import ModelPackageGroupStack
from cdk_infra.lambda_creation_stack import LambdaStack
from cdk_infra.api_gateway_stack import ApiGatewayStack
from cdk_infra.network_stack import NetworkStack

app = cdk.App()
project_prefix = "sbx-tsp-telco-churn"

ssm_stack = SSMStack(
    app, 
    "SSMStack",
    stack_name=f"{project_prefix}-ssm",
    project_prefix=project_prefix
)

s3_stack = S3BucketStack(
    app, 
    "S3BucketStack", 
    stack_name=f"{project_prefix}-s3",
    workspace_name=ssm_stack.workspace_bucket.string_value, 
    pipeline_name=ssm_stack.pipeline_bucket.string_value,
)

codebuild_stack = CodeBuildStack(
    app, 
    "CodeBuildStack",
    stack_name=f"{project_prefix}-codebuild",
    pipeline_bucket=ssm_stack.pipeline_bucket.string_value,
    workspace_bucket=ssm_stack.workspace_bucket.string_value,
    project_prefix=ssm_stack.project_prefix.string_value,
    build_project_name=ssm_stack.build_project_name.string_value,
    build_iam_role_name=ssm_stack.build_iam_role_name.string_value,
    sfn_state_machine_role_name=ssm_stack.sfn_state_machine_role_name.string_value,
    sagemaker_exec_role_name=ssm_stack.sagemaker_exec_role_name.string_value
)
codepipeline_stack = CodePipelineStack(
    app,
    "CodePipelineStack",
    stack_name=f"{project_prefix}-codepipeline",
    pipeline_role_name=ssm_stack.pipeline_iam_role_name.string_value,
    build_project=codebuild_stack.build_project,
    project_prefix=ssm_stack.project_prefix.string_value,
    artifact_bucket=s3_stack.pipeline_bucket,
    workspace_bucket=ssm_stack.workspace_bucket.string_value,
    bucket_prefix=ssm_stack.bucket_prefix.string_value,
    pipeline_name=ssm_stack.pipeline_name.string_value,
    repo_owner=ssm_stack.github_owner.string_value,
    repo_name=ssm_stack.github_repo.string_value,
    branch_name=ssm_stack.github_branch.string_value
)
sagemaker_exec_role_stack = SageMakerRoleStack(
    app,
    "SageMakerExecRoleStack",
    stack_name=f"{project_prefix}-sagemaker-exec-role",
    role_name=ssm_stack.sagemaker_exec_role_name.string_value,
    workspace_bucket=ssm_stack.workspace_bucket.string_value,
    project_prefix=ssm_stack.project_prefix.string_value
)

stepfunction_stack = StepFunctionStack(
    app,
    "StepFunctionStack",
    stack_name=f"{project_prefix}-stepfunction",
    sfn_state_machine_name=ssm_stack.sfn_state_machine_name.string_value,
    sfn_state_machine_role_name=ssm_stack.sfn_state_machine_role_name.string_value,
    workspace_bucket=ssm_stack.workspace_bucket.string_value,
    project_prefix=ssm_stack.project_prefix.string_value,
    sagemaker_exec_role_arn=sagemaker_exec_role_stack.sagemaker_exec_role_arn.string_value
)
stepfunction_stack.add_dependency(sagemaker_exec_role_stack)

model_package_group_stack = ModelPackageGroupStack(
    app,
    "ModelPackageGroupStack",
    stack_name=f"{project_prefix}-model-package-group",
    model_package_group_name=ssm_stack.model_package_group_name.string_value
)

lambda_stack = LambdaStack(
    app,
    "LambdaStack",
    stack_name=f"{project_prefix}-lambda",
    lambda_role_name=ssm_stack.lambda_role_name.string_value,
    project_prefix=ssm_stack.project_prefix.string_value,
    endpoint_name=ssm_stack.endpoint_name.string_value,
)

api_stack = ApiGatewayStack(
    app,
    "ApiGatewayStack",
    stack_name=f"{project_prefix}-api-gateway",
    project_prefix=ssm_stack.project_prefix.string_value,
    predict_lambda=lambda_stack.predict_lambda,
)

api_stack.add_dependency(lambda_stack)

network_stack = NetworkStack(
    app,
    "NetworkStack",
    stack_name=f"{project_prefix}-network",
    project_prefix=ssm_stack.project_prefix.string_value,
)

app.synth()
