from aws_cdk import (
    Stack,
    Aws,
    aws_iam as iam,
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
                                "sagemaker:DescribeEndpoint"
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
            grant_report_group_permissions=False
        )