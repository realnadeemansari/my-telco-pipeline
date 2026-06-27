import os
import boto3
import pandas as pd
import kagglehub
from sagemaker.session import Session

sagemaker_session = Session()
bucket_name = sagemaker_session.default_bucket()
s3_key = "telco/data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
path = kagglehub.dataset_download("blastchar/telco-customer-churn")
file_path = os.path.join(
    path,
    "WA_Fn-UseC_-Telco-Customer-Churn.csv"
)
s3 = boto3.client("s3")
s3.upload_file(
    file_path,
    bucket_name,
    s3_key
)

print("uploaded")