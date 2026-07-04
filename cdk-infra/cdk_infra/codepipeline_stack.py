from aws_cdk import (
    Stack,
    Aws,
    aws_s3 as s3,
    aws_iam as iam,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    SecretValue,
)
from constructs import Construct

class CodePipelineStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            *, 
            build_project: codebuild.IProject,
            artifact_bucket: s3.IBucket,
            workspace_bucket: str,
            bucket_prefix: str,
            pipeline_role_name: str,
            project_prefix,
            pipeline_name: str,
            repo_owner: str,
            repo_name: str,
            branch_name: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.pipeline_role = iam.Role(
            self,
            "TelcoCodePipelineRole",
            role_name=pipeline_role_name,
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
            inline_policies={
                f"{project_prefix}-codepipeline-s3-policy": iam.PolicyDocument(
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
                                f"arn:aws:s3:::{artifact_bucket.bucket_name}",
                                f"arn:aws:s3:::{artifact_bucket.bucket_name}/*"
                            ],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["sts:AssumeRole"],
                            resources=[f"arn:aws:codebuild:{Aws.REGION}:{Aws.ACCOUNT_ID}:role/{pipeline_role_name}"],
                        )
                    ]
                ),
                f"{project_prefix}-codepipeline-codebuild-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "codebuild:BatchGetBuilds",
                                "codebuild:StartBuild",
                                "codebuild:StopBuild"
                            ],
                            resources=[
                                f"arn:aws:codebuild:{Aws.REGION}:{Aws.ACCOUNT_ID}:project/{build_project.project_name}"
                            ]
                        )
                    ]
                ),
            }
        )

        source_output = codepipeline.Artifact("SourceArtifact")
        build_output = codepipeline.Artifact("BuildArtifact")

        self.pipeline = codepipeline.Pipeline(
            self,
            "TelcoChurnPipeline",
            role=self.pipeline_role,
            pipeline_name=pipeline_name,
            artifact_bucket=artifact_bucket,
        )

        ###################################################################
        # Source Stage
        ###################################################################
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub",
            owner=repo_owner,
            repo=repo_name,
            branch=branch_name,
            oauth_token=SecretValue.secrets_manager("github-token"),
            output=source_output,
            trigger=codepipeline_actions.GitHubTrigger.NONE
        )

        self.pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )
        
        ###################################################################
        # Build Stage
        ###################################################################
        self.pipeline.add_stage(
            stage_name="Build",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Build",
                    project=build_project,
                    input=source_output,
                    outputs=[build_output],
                    role=self.pipeline_role,
                    environment_variables={
                        "PIPELINE_STAGE": codebuild.BuildEnvironmentVariable(value="TRAIN")
                    }
                )
            ],
        )

        ###################################################################
        # Approve Stage
        ###################################################################
        self.evaluation_key = "evaluation.json"
        self.external_entity_link = f"https://s3.console.aws.amazon.com/s3/object/{workspace_bucket}?prefix={bucket_prefix}/output/evaluation/latest/{self.evaluation_key}"

        approve_action = codepipeline_actions.ManualApprovalAction(
            action_name="ManualApproval",
            additional_information="Please review evaluation metrics before proceeding.",
            external_entity_link=self.external_entity_link,
            run_order=1,
            role=self.pipeline_role
        )
        self.pipeline.add_stage(
            stage_name="Approve",
            actions=[approve_action],
            )
        
        ###################################################################
        # Deploy Stage
        ###################################################################

        self.pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="DeployLatestApprovedModel",
                    project=build_project,
                    input=source_output,
                    role=self.pipeline_role,
                    environment_variables={
                        "PIPELINE_STAGE": codebuild.BuildEnvironmentVariable(
                            value="DEPLOY"
                        )
                    }
                )
            ]
        )