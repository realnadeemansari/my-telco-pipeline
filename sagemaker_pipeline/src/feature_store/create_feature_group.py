import boto3
import sagemaker
from sagemaker.session import Session
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.feature_store.feature_definition import FeatureDefinition, FeatureTypeEnum

region = boto3.Session().region_name
sagemaker_session = Session()
role = sagemaker.get_execution_role()
bucket_name = sagemaker_session.default_bucket()

feature_group_name = "telco-churn-feature-group"

feature_definitions = [
    FeatureDefinition(feature_name="customerID", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="EventTime", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="gender", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="SeniorCitizen", feature_type=FeatureTypeEnum.INTEGRAL),
    FeatureDefinition(feature_name="Partner", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="Dependents", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="tenure", feature_type=FeatureTypeEnum.INTEGRAL),
    FeatureDefinition(feature_name="PhoneService", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="MultipleLines", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="InternetService", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="OnlineSecurity", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="OnlineBackup", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="DeviceProtection", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="TechSupport", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="StreamingTV", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="StreamingMovies", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="Contract", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="PaperlessBilling", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="PaymentMethod", feature_type=FeatureTypeEnum.STRING),
    FeatureDefinition(feature_name="MonthlyCharges", feature_type=FeatureTypeEnum.FRACTIONAL),
    FeatureDefinition(feature_name="TotalCharges", feature_type=FeatureTypeEnum.FRACTIONAL),
    FeatureDefinition(feature_name="Churn", feature_type=FeatureTypeEnum.INTEGRAL),
]

feature_group = FeatureGroup(
    name=feature_group_name,
    feature_definitions=feature_definitions,
    sagemaker_session=sagemaker_session
)

feature_group.create(
    s3_uri=f"s3://{bucket_name}/telco/feature-store",
    record_identifier_name="customerID",
    event_time_feature_name="EventTime",
    role_arn=role,
    enable_online_store=True
)

print("Feature group created")