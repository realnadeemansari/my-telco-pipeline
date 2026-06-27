import os
import pandas as pd
import numpy as np
import boto3
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.session import Session
import kagglehub

path = kagglehub.dataset_download(
    "blastchar/telco-customer-churn"
)

df = pd.read_csv(
    os.path.join(
        path,
        "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    )
)

df["TotalCharges"] = df["TotalCharges"].replace(" ", np.nan)
df["TotalCharges"] = df["TotalCharges"].astype(float)

df.dropna(inplace=True)

df["Churn"] = df["Churn"].map({
    "Yes": 1,
    "No": 0
})

df["EventTime"] = pd.Timestamp.now().strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)

feature_group_name = "telco-churn-feature-group"

feature_group = FeatureGroup(
    name=feature_group_name,
    sagemaker_session=Session()
)

feature_group.ingest(
    data_frame=df,
    max_workers=3,
    wait=True
)

print("Feature ingestion completed")