from aws_cdk import (
    Stack,
    Aws,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_ssm as ssm,
)
from constructs import Construct

class StepFunctionStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str,
        *,
        sfn_state_machine_role_name: str,
        sfn_state_machine_name: str,
        sagemaker_exec_role_arn: str,
        project_prefix,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        ####################################################
        # Step Function Execution Role
        ####################################################

        self.sfn_state_machine_role = iam.Role(
            self,
            "SfnStateMachineWorkflowExecutionRole",
            role_name=sfn_state_machine_role_name,
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
            inline_policies={
                f"{project_prefix}-sfn-sagemaker-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
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
                                "sagemaker:AddTags",
                                "sagemaker:DeleteTags"
                            ],
                            resources=[
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:training-job/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:processing-job/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:model/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:model-package/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:model-package-group/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:endpoint-config/{project_prefix}*",
                                f"arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:endpoint/{project_prefix}*"
                            ],
                        )
                    ]
                ),
                f"{project_prefix}-sfn-common-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "iam:PassRole"
                            ],
                            resources=[
                                sagemaker_exec_role_arn
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "events:PutRule",
                                "events:PutTargets",
                                "events:DescribeRule",
                                "events:DeleteRule",
                                "events:RemoveTargets",
                            ],
                            resources=["*"]   # List APIs don't support resource-level scoping in IAM
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogDelivery",
                                "logs:GetLogDelivery",
                                "logs:UpdateLogDelivery",
                                "logs:DeleteLogDelivery",
                                "logs:ListLogDeliveries",
                                "logs:PutResourcePolicy",
                                "logs:DescribeResourcePolicies",
                                "logs:DescribeLogGroups"
                            ],
                            resources=["*"]   # List APIs don't support resource-level scoping in IAM
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ssm:GetParameter",
                                "ssm:PutParameter",
                                "ssm:GetParameters",      # for fetching multiple at once
                                "ssm:GetParametersByPath" # for fetching all under a path prefix
                            ],
                            resources=[
                                f"arn:aws:ssm:{Aws.REGION}:{Aws.ACCOUNT_ID}:parameter/telco-churn/*"
                            ]
                        )
                    ]
                ),
            }
        )
        start = sfn.Pass(
            self,
            "Start"
        )
        self.state_machine = sfn.StateMachine(
            self,
            "SfnStateMachine",
            state_machine_name=sfn_state_machine_name,
            role=self.sfn_state_machine_role,
            definition_body=sfn.DefinitionBody.from_chainable(start)
        )

        ####################################################
        # Put SSM Params
        ####################################################

        ssm.StringParameter(
            self,
            "SfnStateMachineArn",
            parameter_name="/telco-churn/step-function/state-machine/arn",
            string_value=self.state_machine.state_machine_arn,
        )
        ssm.StringParameter(
            self,
            "SfnStateMachineRoleArn",
            parameter_name="/telco-churn/step-function/state-machine/role-arn",
            string_value=self.sfn_state_machine_role.role_arn,
        )
