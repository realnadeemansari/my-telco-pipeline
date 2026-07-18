from aws_cdk import (
    Stack,
    Aws,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_codebuild as codebuild,
)
from constructs import Construct

class CodeBuildStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str,
            build_project_name: str,
            pipeline_bucket,
            workspace_bucket,
            project_prefix,
            build_iam_role_name,
            sfn_state_machine_role_name,
            sagemaker_exec_role_name,
            **kwargs
            ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve VPC and subnets from SSM Parameter Store
        self.vpc_id = ssm.StringParameter.value_for_string_parameter(
            self, "/telco-churn/network/vpc-id"
        )
        self.private_subnet_1 = ssm.StringParameter.value_for_string_parameter(
            self, "/telco-churn/network/private-subnet-1-id"
        )
        self.private_subnet_2 = ssm.StringParameter.value_for_string_parameter(
            self, "/telco-churn/network/private-subnet-2-id"
        )
        self.codebuild_security_group = ssm.StringParameter.value_for_string_parameter(
            self, 
            "/telco-churn/network/codebuild-security-group-id"
        )
        self.vpc = ec2.Vpc.from_vpc_attributes(
            self,
            "VPCCodeBuild",
            vpc_id=self.vpc_id,
            availability_zones=[f"{Aws.REGION}a", f"{Aws.REGION}b"],
            private_subnet_ids=[self.private_subnet_1, self.private_subnet_2]
        )
        self.private_subnet1 = ec2.Subnet.from_subnet_id(
            self,
            "PrivateSubnet1",
            self.private_subnet_1
        )

        self.private_subnet2 = ec2.Subnet.from_subnet_id(
            self,
            "PrivateSubnet2",
            self.private_subnet_2
        )
        self.codebuild_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "CodeBuildSecurityGroup",
            security_group_id=self.codebuild_security_group
        )
        self.codebuild_role = iam.Role(
            self, "TelcoCodeBuildRole",
            role_name=build_iam_role_name,
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            inline_policies={
                f"{project_prefix}-codebuild-s3-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:Abort*",
                                "s3:DeleteObject*",
                                "s3:GetBucket*",
                                "s3:GetObject*",
                                "s3:List*",
                                "s3:PutObject",
                                "s3:PutObjectLegalHold",
                                "s3:PutObjectRetention",
                                "s3:PutObjectTagging",
                                "s3:PutObjectVersionTagging"
                            ],
                            resources=[
                                f"arn:aws:s3:::{pipeline_bucket}",
                                f"arn:aws:s3:::{pipeline_bucket}/*",
                                f"arn:aws:s3:::{workspace_bucket}",
                                f"arn:aws:s3:::{workspace_bucket}/*"
                            ],
                        )
                    ]
                ),
                f"{project_prefix}-codebuild-report-group-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "codebuild:BatchPutCodeCoverages",
                                "codebuild:BatchPutTestCases",
                                "codebuild:CreateReport",
                                "codebuild:CreateReportGroup",
                                "codebuild:UpdateReport"
                            ],
                            resources=[f"arn:aws:codebuild:{Aws.REGION}:{Aws.ACCOUNT_ID}:report-group/{build_project_name}*"],
                            effect=iam.Effect.ALLOW
                        )
                    ]
                ),
                f"{project_prefix}-codebuild-logs-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=[
                                f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:/aws/codebuild/{build_project_name}:*",
                                f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:/aws/codebuild/{build_project_name}"
                            ],
                        )
                    ]
                ),
                f"{project_prefix}-codebuild-ssm-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ssm:GetParameter",
                                "ssm:GetParameters",      # for fetching multiple at once
                                "ssm:GetParametersByPath" # for fetching all under a path prefix
                            ],
                            resources=[
                                f"arn:aws:ssm:{Aws.REGION}:{Aws.ACCOUNT_ID}:parameter/telco-churn/*"
                            ]
                        )
                    ]
                ),
                f"{project_prefix}-codebuild-network-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ec2:CreateNetworkInterface",
                                "ec2:DescribeNetworkInterfaces",
                                "ec2:DeleteNetworkInterface",
                                "ec2:DescribeSubnets",
                                "ec2:DescribeSecurityGroups",
                                "ec2:DescribeVpcs",
                                "ec2:DescribeDhcpOptions",
                                "ec2:DescribeAvailabilityZones" # for fetching all under a path prefix
                            ],
                            resources=["*"]
                        )
                    ]
                ),
                f"{project_prefix}-codebuild-stepfn-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "states:DescribeStateMachine",
                                "states:StartExecution",
                                "states:DescribeExecution",
                                "states:UpdateStateMachine"
                            ],
                            resources=[
                                f"arn:aws:states:{Aws.REGION}:{Aws.ACCOUNT_ID}:stateMachine:{project_prefix}-sfn-state-machine-workflow",
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "iam:PassRole"
                            ],
                            resources=[
                                f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/{sfn_state_machine_role_name}",
                            ]
                        )
                    ]
                ),
                f"{project_prefix}-codebuild-sagemaker-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sagemaker:ListModelPackages",
                                "sagemaker:DescribeModelPackage",
                                "sagemaker:CreateModel",
                                "sagemaker:DeleteModel",
                                "sagemaker:DescribeModel",
                                "sagemaker:CreateEndpointConfig",
                                "sagemaker:DescribeEndpointConfig",
                                "sagemaker:DeleteEndpointConfig",
                                "sagemaker:CreateEndpoint",
                                "sagemaker:UpdateEndpoint",
                                "sagemaker:DescribeEndpoint",
                                "sagemaker:AddTags",
                                "sagemaker:DeleteTags"
                            ],
                            resources=[
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:model/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:model-package/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:model-package-group/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:endpoint-config/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:endpoint/{project_prefix}*"
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "iam:PassRole"
                            ],
                            resources=[
                                f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/{sagemaker_exec_role_name}",
                            ]
                        )
                    ]
                )
            }
        )

        # Define the CodeBuild project
        self.build_project = codebuild.PipelineProject(
            self, "TelcoBuildProject",
            role=self.codebuild_role,
            project_name=build_project_name,
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            grant_report_group_permissions=False,
            vpc=self.vpc,
            subnet_selection=ec2.SubnetSelection(
                subnets=[self.private_subnet1, self.private_subnet2]
            ),
            security_groups=[self.codebuild_security_group]
        )