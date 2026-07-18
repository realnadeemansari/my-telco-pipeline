from aws_cdk import (
    Stack,
    Aws,
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

        # Create VPC
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

        # Create public and private subnets
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

        # Create route tables and routes
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

        # Associate subnets with route tables
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

        # Security group for Lambda functions and SageMaker endpoint
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
        self.process_train_security_group = ec2.CfnSecurityGroup(
            self,
            "ProcessTrainSecurityGroup",
            group_name=f"{project_prefix}-process-train-sg",
            group_description="Security group for processing and training",
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
                    "value": f"{project_prefix}-process-train-sg"
                }
            ]
        )
        self.codebuild_security_group = ec2.CfnSecurityGroup(
            self,
            "CodeBuildSecurityGroup",
            group_name=f"{project_prefix}-codebuild-sg",
            group_description="Security group for CodeBuild",
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
                    "value": f"{project_prefix}-codebuild-sg"
                }
            ]
        )
        self.vpc_endpoint_security_group = ec2.CfnSecurityGroup(
            self,
            "VPCEndpointSecurityGroup",
            group_name=f"{project_prefix}-vpc-endpoint-sg",
            group_description="Security group for VPC endpoints",
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
                    "value": f"{project_prefix}-vpc-endpoint-sg"
                }
            ]
        )
        self.endpoint_security_group_lambda_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "EndpointSecurityGroupLambdaIngress",
            group_id=self.endpoint_security_group.attr_group_id,
            source_security_group_id=self.lambda_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443
        )
        self.endpoint_security_group_process_train_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "EndpointSecurityGroupProcessTrainIngress",
            group_id=self.endpoint_security_group.attr_group_id,
            source_security_group_id=self.process_train_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443
        )
        self.process_train_security_group_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "ProcessTrainSecurityGroupIngress",
            group_id=self.process_train_security_group.attr_group_id,
            source_security_group_id=self.process_train_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443
        )
        self.endpoint_security_group_codebuild_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "EndpointSecurityGroupCodeBuildIngress",
            group_id=self.endpoint_security_group.attr_group_id,
            source_security_group_id=self.codebuild_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443
        )
        self.vpc_endpoint_security_group_endpoint_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "VPCEndpointSecurityGroupEndpointIngress",
            group_id=self.vpc_endpoint_security_group.attr_group_id,
            source_security_group_id=self.endpoint_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443
        )
        self.vpc_endpoint_security_group_process_train_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "VPCEndpointSecurityGroupProcessTrainIngress",
            group_id=self.vpc_endpoint_security_group.attr_group_id,
            source_security_group_id=self.process_train_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443
        )
        self.vpc_endpoint_security_group_codebuild_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "VPCEndpointSecurityGroupCodeBuildIngress",
            group_id=self.vpc_endpoint_security_group.attr_group_id,
            source_security_group_id=self.codebuild_security_group.attr_group_id,
            ip_protocol="tcp",
            from_port=443,
            to_port=443
        )

        # Create NACL
        # self.private_nacl = ec2.CfnNetworkAcl(
        #     self,
        #     "PrivateNetworkAcl",
        #     vpc_id=self.vpc.ref,
        #     tags=[
        #         {
        #             "key": "Name",
        #             "value": f"{project_prefix}-private-nacl"
        #         }
        #     ]
        # )
        # ec2.CfnSubnetNetworkAclAssociation(
        #     self,
        #     "PrivateSubnet1NaclAssociation",
        #     subnet_id=self.private_subnet_1.ref,
        #     network_acl_id=self.private_nacl.ref
        # )
        # ec2.CfnSubnetNetworkAclAssociation(
        #     self,
        #     "PrivateSubnet2NaclAssociation",
        #     subnet_id=self.private_subnet_2.ref,
        #     network_acl_id=self.private_nacl.ref
        # )

        # ec2.CfnNetworkAclEntry(
        #     self,
        #     "PrivateInboundEphemeral",
        #     network_acl_id=self.private_nacl.ref,
        #     rule_number=100,
        #     protocol=6,
        #     rule_action="allow",
        #     egress=False,
        #     cidr_block="0.0.0.0/0",
        #     port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
        #         from_=1024,
        #         to=65535
        #     )
        # )
        # ec2.CfnNetworkAclEntry(
        #     self,
        #     "PrivateOutbound443",
        #     network_acl_id=self.private_nacl.ref,
        #     rule_number=100,
        #     protocol=6,
        #     rule_action="allow",
        #     egress=True,
        #     cidr_block="0.0.0.0/0",
        #     port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
        #         from_=443,
        #         to=443
        #     )
        # )
        # ec2.CfnNetworkAclEntry(
        #     self,
        #     "PrivateOutboundEphemeral",
        #     network_acl_id=self.private_nacl.ref,
        #     rule_number=110,
        #     protocol=6,
        #     rule_action="allow",
        #     egress=True,
        #     cidr_block="0.0.0.0/0",
        #     port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(
        #         from_=1024,
        #         to=65535
        #     )
        # )

        # Create NAT
        # self.nat_eip = ec2.CfnEIP(
        #     self,
        #     "NatElasticIP",
        #     domain="vpc",
        #     tags=[
        #         {
        #             "key": "Name",
        #             "value": f"{project_prefix}-nat-eip"
        #         }
        #     ]
        # )
        # self.nat_gateway = ec2.CfnNatGateway(
        #     self,
        #     "NatGateway",
        #     allocation_id=self.nat_eip.attr_allocation_id,
        #     subnet_id=self.public_subnet_1.ref,
        #     tags=[
        #         {
        #             "key": "Name",
        #             "value": f"{project_prefix}-nat-gateway"
        #         }
        #     ]
        # )
        # self.nat_gateway.add_dependency(self.vpc_gateway_attachment)
        # ec2.CfnRoute(
        #     self,
        #     "PrivateDefaultRoute",
        #     route_table_id=self.private_route_table.ref,
        #     destination_cidr_block="0.0.0.0/0",
        #     nat_gateway_id=self.nat_gateway.ref
        # )

        # Create VPC endpoints for S3, ECR, and CloudWatch Logs
        self.s3_gateway_endpoint = ec2.CfnVPCEndpoint(
            self,
            "S3GatewayEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.s3",
            route_table_ids=[self.private_route_table.ref],
            vpc_endpoint_type="Gateway"
        )
        self.ecr_api_endpoint = ec2.CfnVPCEndpoint(
            self,
            "ECRApiEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.ecr.api",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.ecr_dkr_endpoint = ec2.CfnVPCEndpoint(
            self,
            "ECRDKREndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.ecr.dkr",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.logs_endpoint = ec2.CfnVPCEndpoint(
            self,
            "LogsEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.logs",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.sts_endpoint = ec2.CfnVPCEndpoint(
            self,
            "STSEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.sts",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.sagemaker_runtime_endpoint = ec2.CfnVPCEndpoint(
            self,
            "SageMakerRuntimeEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.sagemaker.runtime",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.ssm_endpoint = ec2.CfnVPCEndpoint(
            self,
            "SSMEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.ssm",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.stepfunctions_endpoint = ec2.CfnVPCEndpoint(
            self,
            "StepFunctionsEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.states",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.cloudformation_endpoint = ec2.CfnVPCEndpoint(
            self,
            "CloudFormationEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.cloudformation",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        self.sagemaker_api_endpoint = ec2.CfnVPCEndpoint(
            self,
            "SageMakerApiEndpoint",
            vpc_id=self.vpc.ref,
            service_name=f"com.amazonaws.{Aws.REGION}.sagemaker.api",
            vpc_endpoint_type="Interface",
            subnet_ids=[self.private_subnet_1.ref, self.private_subnet_2.ref],
            security_group_ids=[self.vpc_endpoint_security_group.attr_group_id],
            private_dns_enabled=True
        )
        # Outputs for VPC, subnets, route tables, and security groups
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

        CfnOutput(
            self,
            "VPCEndpointSecurityGroupIdOutput",
            value=self.vpc_endpoint_security_group.ref,
            description="The ID of the VPC endpoint security group"
        )
        CfnOutput(
            self,
            "ECRDKREndpointIdOutput",
            value=self.ecr_dkr_endpoint.ref,
            description="The ID of the ECR DKR VPC endpoint"
        )
        CfnOutput(
            self,
            "LogsEndpointIdOutput",
            value=self.logs_endpoint.ref,
            description="The ID of the CloudWatch Logs VPC endpoint"
        )
        CfnOutput(
            self,
            "STSEndpointIdOutput",
            value=self.sts_endpoint.ref,
            description="The ID of the STS VPC endpoint"
        )
        CfnOutput(
            self,
            "SageMakerRuntimeEndpointIdOutput",
            value=self.sagemaker_runtime_endpoint.ref,
            description="The ID of the SageMaker Runtime VPC endpoint"
        )
        CfnOutput(
            self,
            "S3GatewayEndpointIdOutput",
            value=self.s3_gateway_endpoint.ref,
            description="The ID of the S3 Gateway VPC endpoint"
        )
        CfnOutput(
            self,
            "ProcessTrainSecurityGroupIdOutput",
            value=self.process_train_security_group.ref,
            description="The ID of the processing and training security group"
        )
        # CfnOutput(
        #     self,
        #     "PrivateNaclIdOutput",
        #     value=self.private_nacl.ref,
        #     description="The ID of the private network ACL"
        # )
        CfnOutput(
            self,
            "CodeBuildSecurityGroupIdOutput",
            value=self.codebuild_security_group.ref,
            description="The ID of the CodeBuild security group"
        )
        CfnOutput(
            self,
            "ECRApiInterfaceEndpointOutput",
            value=self.ecr_api_endpoint.ref,
            description="The ID of ECR Interface Endpoint"
        )
        CfnOutput(
            self,
            "SagemakerApiInterfaceEndpointOutput",
            value=self.sagemaker_api_endpoint.ref,
            description="The ID of Sagemaker Interface Endpoint"
        )
        CfnOutput(
            self,
            "SSMInterfaceEndpointOutput",
            value=self.ssm_endpoint.ref,
            description="The ID of SSM Interface Endpoint"
        )
        CfnOutput(
            self,
            "StepFunctionsInterfaceEndpointOutput",
            value=self.stepfunctions_endpoint.ref,
            description="The ID of Step Functions Interface Endpoint"
        )
        CfnOutput(
            self,
            "CloudFormationInterfaceEndpointOutput",
            value=self.cloudformation_endpoint.ref,
            description="The ID of Cloud formation Interface Endpoint"
        )

        # Store VPC, subnets, route tables, and security groups in SSM Parameter Store
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

        ssm.StringParameter(
            self,
            "ProcessTrainSecurityGroupIdParameter",
            parameter_name="/telco-churn/network/process-train-security-group-id",
            string_value=self.process_train_security_group.ref
        )
        ssm.StringParameter(
            self,
            "VPCEndpointSecurityGroupIdParameter",
            parameter_name="/telco-churn/network/vpc-endpoint-security-group-id",
            string_value=self.vpc_endpoint_security_group.ref
        )
        ssm.StringParameter(
            self,
            "S3EndpointIdParameter",
            parameter_name="/telco-churn/network/s3-gateway-endpoint-id",
            string_value=self.s3_gateway_endpoint.ref
        )
        ssm.StringParameter(
            self,
            "LogsEndpointIdParameter",
            parameter_name="/telco-churn/network/logs-endpoint-id",
            string_value=self.logs_endpoint.ref
        )
        ssm.StringParameter(
            self,
            "STSEndpointIdParameter",
            parameter_name="/telco-churn/network/sts-endpoint-id",
            string_value=self.sts_endpoint.ref
        )
        # ssm.StringParameter(
        #     self,
        #     "PrivateNetworkAclParameter",
        #     parameter_name="/telco-churn/network/private-network-acl-id",
        #     string_value=self.private_nacl.ref
        # )
        ssm.StringParameter(
            self,
            "CodeBuildSecurityGroupIdParameter",
            parameter_name="/telco-churn/network/codebuild-security-group-id",
            string_value=self.codebuild_security_group.ref
        )
        ssm.StringParameter(
            self,
            "ECRApiEndpointParameter",
            parameter_name="/telco-churn/network/ecr-api-endpoint",
            string_value=self.ecr_api_endpoint.ref
        )
        ssm.StringParameter(
            self,
            "SagemakerApiEndpointParameter",
            parameter_name="/telco-churn/network/sagemaker-api-endpoint",
            string_value=self.sagemaker_api_endpoint.ref
        )
        ssm.StringParameter(
            self,
            "SSMEndpointParameter",
            parameter_name="/telco-churn/network/ssm-endpoint",
            string_value=self.ssm_endpoint.ref
        )
        ssm.StringParameter(
            self,
            "StepFunctionsEndpointParameter",
            parameter_name="/telco-churn/network/stepfunctions-endpoint",
            string_value=self.stepfunctions_endpoint.ref
        )
        ssm.StringParameter(
            self,
            "CloudFormationEndpointParameter",
            parameter_name="/telco-churn/network/cloudformation-endpoint",
            string_value=self.cloudformation_endpoint.ref
        )
        