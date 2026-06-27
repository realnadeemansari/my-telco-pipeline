#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_infra.s3_stack import S3BucketStack
import boto3

ssm_client = boto3.client("ssm")

workspace_bucket_name = ssm_client.get_parameter(Name="/telco-churn/s3/workspace-bucket-name")["Parameter"]["Value"]
pipeline_bucket_name = ssm_client.get_parameter(Name="/telco-churn/s3/pipeline-bucket-name")["Parameter"]["Value"]
pipeline_name = ssm_client.get_parameter(Name="/telco-churn/pipeline-name")["Parameter"]["Value"]
github_owner = ssm_client.get_parameter(Name="/telco-churn/github-owner")["Parameter"]["Value"]
github_repo = ssm_client.get_parameter(Name="/telco-churn/github-repo")["Parameter"]["Value"]
github_branch = ssm_client.get_parameter(Name="/telco-churn/github-branch")["Parameter"]["Value"]


app = cdk.App()
S3BucketStack(app, "S3BucketStack", workspace_name=workspace_bucket_name, pipeline_name=pipeline_bucket_name)

app.synth()
