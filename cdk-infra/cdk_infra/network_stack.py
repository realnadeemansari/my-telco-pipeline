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
                {
                    "key": "Name",
                    "value": f"{project_prefix}-public-subnet-1"
                }
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
                {
                    "key": "Name",
                    "value": f"{project_prefix}-public-subnet-2"
                }
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
                {
                    "key": "Name",
                    "value": f"{project_prefix}-private-subnet-1"
                }
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
                {
                    "key": "Name",
                    "value": f"{project_prefix}-private-subnet-2"
                }
            ]
        )
        self.public_route_table = ec2.CfnRouteTable(
            self,
            "PublicRouteTable",
            vpc_id=self.vpc.ref,
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-public-rt"
                }
            ]
        )
        self.private_route_table = ec2.CfnRouteTable(
            self,
            "PrivateRouteTable",
            vpc_id=self.vpc.ref,
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-private-rt"
                }
            ]
        )
        self.public_default_route = ec2.CfnRoute(
            self,
            "PublicDefaultRoute",
            route_table_id=self.public_route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.internet_gateway.ref
        )
        self.public_default_route.add_dependency(self.vpc_gateway_attachment)
        ec2.CfnSubnetRouteTableAssociation(
            self,
            "PublicSubnet1RouteTableAssociation",
            subnet_id=self.public_subnet_1.ref,
            route_table_id=self.public_route_table.ref
        )
        ec2.CfnSubnetRouteTableAssociation(
            self,
            "PublicSubnet2RouteTableAssociation",
            subnet_id=self.public_subnet_2.ref,
            route_table_id=self.public_route_table.ref
        )
        ec2.CfnSubnetRouteTableAssociation(
            self,
            "PrivateSubnet1RouteTableAssociation",
            subnet_id=self.private_subnet_1.ref,
            route_table_id=self.private_route_table.ref
        )
        ec2.CfnSubnetRouteTableAssociation(
            self,
            "PrivateSubnet2RouteTableAssociation",
            subnet_id=self.private_subnet_2.ref,
            route_table_id=self.private_route_table.ref
        )
        self.lambda_security_group = ec2.CfnSecurityGroup(
            self,
            "LambdaSecurityGroup",
            group_name=f"{project_prefix}-lambda-sg",
            group_description="Security group for Lambda functions",
            vpc_id=self.vpc.ref,
            security_group_egress=[
                ec2.CfnSecurityGroup.EgressProperty(
                    ip_protocol="-1",
                    cidr_ip="0.0.0.0/0"
                )
            ],
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-lambda-sg"
                }
            ]
        )
        self.endpoint_security_group = ec2.CfnSecurityGroup(
            self,
            "EndpointSecurityGroup",
            group_name=f"{project_prefix}-endpoint-sg",
            group_description="Security group for SageMaker endpoint",
            vpc_id=self.vpc.ref,
            security_group_egress=[
                ec2.CfnSecurityGroup.EgressProperty(
                    ip_protocol="-1",
                    cidr_ip="0.0.0.0/0"
                )
            ],
            tags=[
                {
                    "key": "Name",
                    "value": f"{project_prefix}-endpoint-sg"
                }
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
        CfnOutput(
            self,
            "PublicRouteTableIdOutput",
            value=self.public_route_table.ref,
            description="The ID of the public route table"
        )
        CfnOutput(
            self,
            "PrivateRouteTableIdOutput",
            value=self.private_route_table.ref,
            description="The ID of the private route table"
        )
        CfnOutput(
            self,
            "LambdaSecurityGroupIdOutput",
            value=self.lambda_security_group.ref,
            description="The ID of the Lambda security group"
        )
        CfnOutput(
            self,
            "EndpointSecurityGroupIdOutput",
            value=self.endpoint_security_group.ref,
            description="The ID of the SageMaker endpoint security group"
        )
        ssm.StringParameter(
            self,
            "VpcIdParameter",
            parameter_name="/telco-churn/network/vpc-id",
            string_value=self.vpc.ref
        )
        ssm.StringParameter(
            self,
            "PublicSubnet1IdParameter",
            parameter_name="/telco-churn/network/public-subnet-1-id",
            string_value=self.public_subnet_1.ref
        )
        ssm.StringParameter(
            self,
            "PublicSubnet2IdParameter",
            parameter_name="/telco-churn/network/public-subnet-2-id",
            string_value=self.public_subnet_2.ref
        )
        ssm.StringParameter(
            self,
            "PrivateSubnet1IdParameter",
            parameter_name="/telco-churn/network/private-subnet-1-id",
            string_value=self.private_subnet_1.ref
        )
        ssm.StringParameter(
            self,
            "PrivateSubnet2IdParameter",
            parameter_name="/telco-churn/network/private-subnet-2-id",
            string_value=self.private_subnet_2.ref
        ) 
        ssm.StringParameter(
            self,
            "PublicRouteTableIdParameter",
            parameter_name="/telco-churn/network/public-route-table-id",
            string_value=self.public_route_table.ref
        )
        ssm.StringParameter(
            self,
            "PrivateRouteTableIdParameter",
            parameter_name="/telco-churn/network/private-route-table-id",
            string_value=self.private_route_table.ref
        )
        ssm.StringParameter(
            self,
            "LambdaSecurityGroupIdParameter",
            parameter_name="/telco-churn/network/lambda-security-group-id",
            string_value=self.lambda_security_group.ref
        )
        ssm.StringParameter(
            self,
            "EndpointSecurityGroupIdParameter",
            parameter_name="/telco-churn/network/endpoint-security-group-id",
            string_value=self.endpoint_security_group.ref
        )