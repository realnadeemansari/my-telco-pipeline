from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct

class NetworkStack(Stack):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            *,
            project_prefix: str,
            **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.CfnVPC(
            self,
            "Vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_support=True,
            enable_dns_hostnames=True,
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-vpc"
                }
            ]
        )
        ssm.StringParameter(
            self,
            "VpcIdParameter",
            parameter_name="/telco-churn/network/vpc-id",
            string_value=self.vpc.ref
        )