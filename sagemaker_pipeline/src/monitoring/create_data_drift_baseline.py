import sagemaker
from sagemaker.sklearn.model import SKLearnModel
from sagemaker.model_monitor import DefaultModelMonitor
from sagemaker.model_monitor.dataset_format import DatasetFormat

sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket_name = sagemaker_session.default_bucket()

baseline_output_uri = f"s3://{bucket_name}/telco/baseline-results"
baseline_data_uri = f"s3://{bucket_name}/telco/data/train/train_features.csv"

monitor = DefaultModelMonitor(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    volume_size_in_gb=20,
    max_runtime_in_seconds=3600,
)

monitor.suggest_baseline(
    baseline_dataset=baseline_data_uri,
    dataset_format=DatasetFormat.csv(header=False),
    output_s3_uri=baseline_output_uri,
    wait=True
)

print("Data drift baseline created successfully")
