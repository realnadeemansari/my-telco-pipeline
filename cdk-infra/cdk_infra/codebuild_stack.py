from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
)
from constructs import Construct

class CodeBuildStack(Stack):
    def __init__(
            self, 
            scope: Construct, 
            construct_id: str,
            **kwargs
            ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the CodeBuild project
        self.build_project = codebuild.Project(
            self, "TelcoBuildProject",
            source=codebuild.Source.code_pipeline(
                build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml")
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
            ),
        )