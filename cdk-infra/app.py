#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_infra.s3_stack import S3BucketStack


app = cdk.App()
S3BucketStack(app, "S3BucketStack") 

app.synth()
