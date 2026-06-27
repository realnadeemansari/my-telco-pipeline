from aws_cdk import (
    Stack,
    aws_s3 as s3,
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
            pipeline_name: str,
            repo_owner: str,
            repo_name: str,
            branch_name: str,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_output = codepipeline.Artifact("SourceArtifact")
        build_output = codepipeline.Artifact("BuildArtifact")

        self.pipeline = codepipeline.Pipeline(
            self,
            "TelcoChurnPipeline",
            pipeline_name=pipeline_name,
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
        )

        self.pipeline.add_stage(
            stage_name="Source",
            actions=[source_action],
            artifact_bucket=artifact_bucket
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
                )
            ],
        )

        ###################################################################
        # Approve Stage
        ###################################################################
        approve_action = codepipeline_actions.ManualApprovalAction(
            action_name="ManualApproval",
            additional_information="Please review evaluation metrics before proceeding.",
            # external_entity_link="
            run_order=1,
        )
        self.pipeline.add_stage(
            stage_name="Approve",
            actions=[approve_action],
            )