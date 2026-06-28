from aws_cdk import (
    Stack,
    aws_iam as iam,
    CfnOutput,
    Aws
)
from constructs import Construct

class IAMStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            build_project_name: str,
            build_iam_role_name,
            s3_auto_delete_role_name,
            pipeline_bucket,
            workspace_bucket,
            project_prefix,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
                                f"arn:aws:s3:::{pipeline_bucket}/*"
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
                f"{project_prefix}-codebuild-sagemaker-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sagemaker:CreateTrainingJob",
                                "sagemaker:DescribeTrainingJob",
                                "sagemaker:StopTrainingJob",
                                "sagemaker:CreateProcessingJob",
                                "sagemaker:DescribeProcessingJob",
                                "sagemaker:StopProcessingJob",
                                "sagemaker:CreateModel",
                                "sagemaker:DeleteModel",
                                "sagemaker:DescribeModel",
                                "sagemaker:CreateModelPackage",
                                "sagemaker:DescribeModelPackage",
                                "sagemaker:UpdateModelPackage",
                                "sagemaker:DeleteModelPackage",
                                "sagemaker:CreateModelPackageGroup",
                                "sagemaker:DescribeModelPackageGroup",
                                "sagemaker:DeleteModelPackageGroup",
                                "sagemaker:CreateEndpointConfig",
                                "sagemaker:DeleteEndpointConfig",
                                "sagemaker:CreateEndpoint",
                                "sagemaker:UpdateEndpoint",
                                "sagemaker:DeleteEndpoint",
                                "sagemaker:DescribeEndpoint",
                            ],
                            resources=[
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:training-job/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:processing-job/{project_prefix}*",
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
                                "sagemaker:ListTrainingJobs",
                                "sagemaker:ListProcessingJobs",
                                "sagemaker:ListModels",
                                "sagemaker:ListModelPackages",
                                "sagemaker:ListModelPackageGroups",
                                "sagemaker:ListEndpoints",
                                "sagemaker:ListEndpointConfigs",
                            ],
                            resources=["*"]   # List APIs don't support resource-level scoping in IAM
                        )
                    ]
                )
            }
        )
        self.s3_auto_delete_role = iam.Role(
            self,
            "S3AutoDeleteRole",
            role_name=s3_auto_delete_role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "sbx-tsp-telco-s3-auto-delete-logs-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=["arn:aws:logs:*:*:*"]
                        )
                    ]
                ),
                "sbx-tsp-telco-s3-auto-delete-s3-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:DeleteObject*",
                                "s3:GetBucket*",
                                "s3:List*",
                                "s3:PutBucketPolicy"
                            ],
                            resources=[
                                f"arn:aws:s3:::{pipeline_bucket}",
                                f"arn:aws:s3:::{pipeline_bucket}/*",
                                f"arn:aws:s3:::{workspace_bucket}",
                                f"arn:aws:s3:::{workspace_bucket}/*"
                            ]
                        )
                    ]
                )
            }
        )