from aws_cdk import (
    Stack,
    aws_sagemaker as sagemaker,
)
from constructs import Construct

class ModelPackageGroupStack(Stack):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            *,
            model_package_group_name: str,
            **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.model_package_group = sagemaker.CfnModelPackageGroup(
            self,
            "ModelPackageGroup",
            model_package_group_name=model_package_group_name,
            model_package_group_description="Model package group for Telco Churn Pipeline"
        )