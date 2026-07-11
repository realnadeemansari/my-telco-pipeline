from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput,
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

        self.internet_gateway = ec2.CfnInternetGateway(
            self,
            "InternetGateway",
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-igw"
                }
            ]
        )

        self.vpc_gateway_attachment = ec2.CfnVPCGatewayAttachment(
            self,
            "VpcGatewayAttachment",
            vpc_id=self.vpc.ref,
            internet_gateway_id=self.internet_gateway.ref
        )
        self.public_subnet_1 = ec2.CfnSubnet(
            self,
            "PublicSubnet1",
            vpc_id=self.vpc.ref,
            cidr_block="10.0.1.0/24",
            availability_zone="us-east-1a",
            map_public_ip_on_launch=True,
            tags=[
                ec2.CfnTag(
                    key="Name",
                    value=f"{project_prefix}-public-subnet-1"
                )
            ]
        )
        self.public_subnet_2 = ec2.CfnSubnet(
            self,
            "PublicSubnet2",
            vpc_id=self.vpc.ref,
            cidr_block="10.0.2.0/24",
            availability_zone="us-east-1b",
            map_public_ip_on_launch=True,
            tags=[
                ec2.CfnTag(
                    key="Name",
                    value=f"{project_prefix}-public-subnet-2"
                )
            ]
        )
        self.private_subnet_1 = ec2.CfnSubnet(
            self,
            "PrivateSubnet1",
            vpc_id=self.vpc.ref,
            cidr_block="10.0.11.0/24",
            availability_zone="us-east-1a",
            map_public_ip_on_launch=False,
            tags=[
                ec2.CfnTag(
                    key="Name",
                    value=f"{project_prefix}-private-subnet-1"
                )
            ]
        )
        self.private_subnet_2 = ec2.CfnSubnet(
            self,
            "PrivateSubnet2",
            vpc_id=self.vpc.ref,
            cidr_block="10.0.12.0/24",
            availability_zone="us-east-1b",
            map_public_ip_on_launch=False,
            tags=[
                ec2.CfnTag(
                    key="Name",
                    value=f"{project_prefix}-private-subnet-2"
                )
            ]
        )
        CfnOutput(
            self,
            "VpcIdOutput",
            value=self.vpc.ref,
            description="The ID of the VPC"
        )
        CfnOutput(
            self,
            "PublicSubnet1IdOutput",
            value=self.public_subnet_1.ref,
            description="The ID of the first public subnet"
        )
        CfnOutput(
            self,
            "PublicSubnet2IdOutput",
            value=self.public_subnet_2.ref,
            description="The ID of the second public subnet"
        )
        CfnOutput(
            self,
            "PrivateSubnet1IdOutput",
            value=self.private_subnet_1.ref,
            description="The ID of the first private subnet"
        )
        CfnOutput(
            self,
            "PrivateSubnet2IdOutput",
            value=self.private_subnet_2.ref,
            description="The ID of the second private subnet"
        )
        ssm.StringParameter(
            self,
            "VpcIdParameter",
            parameter_name="/telco-churn/network/vpc-id",
            string_value=self.vpc.ref
        )