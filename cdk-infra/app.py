#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_infra.s3_stack import S3BucketStack
from cdk_infra.codepipeline_stack import CodePipelineStack
from cdk_infra.ssm_stack import SSMStack
from cdk_infra.codebuild_stack import CodeBuildStack

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
    s3_auto_delete_role_name=ssm_stack.s3_auto_delete_role_name.string_value,
    project_prefix=ssm_stack.project_prefix.string_value,
)

codebuild_stack = CodeBuildStack(
    app, 
    "CodeBuildStack",
    stack_name=f"{project_prefix}-codebuild",
    pipeline_bucket=ssm_stack.pipeline_bucket.string_value,
    project_prefix=ssm_stack.project_prefix.string_value,
    build_project_name=ssm_stack.build_project_name.string_value,
    build_iam_role_name=ssm_stack.build_iam_role_name.string_value
)
codepipeline_stack = CodePipelineStack(
    app,
    "CodePipelineStack",
    stack_name=f"{project_prefix}-codepipeline",
    pipeline_role_name=ssm_stack.pipeline_iam_role_name.string_value,
    build_project=codebuild_stack.build_project,
    project_prefix=ssm_stack.project_prefix.string_value,
    artifact_bucket=ssm_stack.pipeline_bucket.string_value,
    pipeline_name=ssm_stack.pipeline_name.string_value,
    repo_owner=ssm_stack.github_owner.string_value,
    repo_name=ssm_stack.github_repo.string_value,
    branch_name=ssm_stack.github_branch.string_value
)

app.synth()
