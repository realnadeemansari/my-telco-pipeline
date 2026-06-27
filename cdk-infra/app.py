#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_infra.s3_stack import S3BucketStack
from cdk_infra.codepipeline_stack import CodePipelineStack
from cdk_infra.ssm_stack import SSMStack
from cdk_infra.codebuild_stack import CodeBuildStack
import boto3

ssm_client = boto3.client("ssm")



app = cdk.App()

ssm_stack = SSMStack(
    app, 
    "SSMStack"
)
s3_stack = S3BucketStack(
    app, 
    "S3BucketStack", 
    workspace_name=ssm_stack.workspace_bucket.string_value, 
    pipeline_name=ssm_stack.pipeline_bucket.string_value
)

codebuild_stack = CodeBuildStack(
    app, 
    "CodeBuildStack"
)
codepipeline_stack = CodePipelineStack(
    app,
    "CodePipelineStack",
    build_project=codebuild_stack.build_project,
    artifact_bucket=s3_stack.pipeline_bucket,
    pipeline_name=ssm_stack.pipeline_name.string_value,
    repo_owner=ssm_stack.github_owner.string_value,
    repo_name=ssm_stack.github_repo.string_value,
    branch_name=ssm_stack.github_branch.string_value
)

app.synth()
