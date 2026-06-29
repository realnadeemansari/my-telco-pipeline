from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker import Session
import sagemaker
import boto3
from stepfunctions import steps
from stepfunctions.inputs import ExecutionInput
from stepfunctions.workflow import Workflow
from datetime import datetime
import os

s3_client = boto3.client("s3")
ssm_client = boto3.client("ssm")

session = Session()
region = boto3.Session().region_name
bucket = ssm_client.get_parameter(Name="/telco-churn/s3/workspace-bucket-name")["Parameter"]["Value"]
bucket_prefix = ssm_client.get_parameter(Name="/telco-churn/s3/bucket-prefix")["Parameter"]["Value"]
project_prefix = ssm_client.get_parameter(Name="/telco-churn/pipeline/project-prefix")["Parameter"]["Value"]
sfn_state_machine_workflow_arn = ssm_client.get_parameter(Name="/telco-churn/step-function/state-machine/arn")["Parameter"]["Value"]
sfn_state_machine_role_arn = ssm_client.get_parameter(Name="/telco-churn/step-function/state-machine/role-arn")["Parameter"]["Value"]
sagemaker_exec_role_arn = ssm_client.get_parameter(Name="/telco-churn/sagemaker/execution-role-arn")["Parameter"]["Value"]
working_dir = "./src"


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

execution_input = ExecutionInput(
    schema={
        "PreprocessingJobName": str,
        "TrainingJobName": str
    }
)

workflow_inputs = {
    "PreprocessingJobName": f"{project_prefix}-preprocessing-" + get_current_time(),
    "TrainingJobName": f"{project_prefix}-training-" + get_current_time()
}


def create_preprocessing_step():
    sklearn_processor = SKLearnProcessor(
        framework_version="1.2-1",
        instance_type="ml.m5.xlarge",
        instance_count=1,
        role=sagemaker_exec_role_arn,
    )
    print(os.listdir())
    s3_client.upload_file(
        Filename=os.path.join(working_dir, "pipeline/preprocessing.py"),
        Bucket=bucket,
        Key=f"{bucket_prefix}/code/preprocessing.py"
    )
    script_s3_uri = f"s3://{bucket}/{bucket_prefix}/code/preprocessing.py"

    s3_client.upload_file(
        Filename=os.path.join(working_dir, "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"),
        Bucket=bucket,
        Key=f"{bucket_prefix}/data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
    )

    data_s3_uri = f"s3://{bucket}/{bucket_prefix}/data/WA_Fn-UseC_-Telco-Customer-Churn.csv"

    preprocessing_step = steps.ProcessingStep(
        state_id="PreprocessingStep",
        processor=sklearn_processor,
        job_name=execution_input["PreprocessingJobName"],
        inputs=[
            ProcessingInput(
                input_name="data",
                source=f"s3://{bucket}/{bucket_prefix}/data",
                destination="/opt/ml/processing/input"
            ),
            ProcessingInput(
                input_name="code",
                source=script_s3_uri,
                destination="/opt/ml/processing/code"
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name="train_data",
                source="/opt/ml/processing/train",
                destination=f"s3://{bucket}/{bucket_prefix}/data/processed/train"
            ),
            ProcessingOutput(
                output_name="test_data",
                source="/opt/ml/processing/test",
                destination=f"s3://{bucket}/{bucket_prefix}/data/processed/test"
            )
        ],
        container_entrypoint=[
            "python3",
            "/opt/ml/processing/code/preprocessing.py"
        ]
    )
    preprocessing_step.add_catch(
        steps.states.Catch(
            error_equals=["States.TaskFailed"],
            next_step=steps.states.Fail(
                "Baseline failed",
                cause="Preprocessing step failed"
            )
        )
    )
    return preprocessing_step


def get_sklearn_image_uri():
    image_uri = sagemaker.image_uris.retrieve(
        framework="sklearn",
        region=region,
        version="1.2-1",
        instance_type="ml.m5.large",
        image_scope="inference"
    )
    return image_uri


def create_training_step():
    sklearn_estimator = SKLearn(
        entry_point="train.py",
        source_dir=os.path.join(working_dir, "pipeline"),
        framework_version="1.2-1",
        instance_type="ml.m5.large",
        role=sagemaker_exec_role_arn,
        output_path=f"s3://{bucket}/{bucket_prefix}/model",
        hyperparameters={
            "n_estimators": 200,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "training_job_name": workflow_inputs["TrainingJobName"],
            "workspace_bucket": bucket,
            "bucket_prefix": bucket_prefix
        }
    )

    training_step = steps.TrainingStep(
        state_id="TrainingStep",
        estimator=sklearn_estimator,
        job_name=execution_input["TrainingJobName"],
        data={
            "train": f"s3://{bucket}/{bucket_prefix}/data/processed/train",
            "test": f"s3://{bucket}/{bucket_prefix}/data/processed/test"
        }
    )
    training_step.add_catch(
        steps.states.Catch(
            error_equals=["States.TaskFailed"],
            next_step=steps.states.Fail(
                "Training failed",
                cause="Training step failed"
            )
        )
    )

    image_uri = get_sklearn_image_uri()
    register_model_step = steps.Task(
        state_id="RegisterModelStep",
        resource="arn:aws:states:::aws-sdk:sagemaker:createModelPackage",
        parameters={
            "ModelPackageGroupName": "telco-churn-model-package",
            "ModelPackageDescription": "Model package for telco churn prediction",
            "ModelApprovalStatus": "PendingManualApproval",
            "InferenceSpecification": {
                "Containers": [
                    {
                        "Image": image_uri,
                        "ModelDataUrl.$": "$.ModelArtifacts.S3ModelArtifacts",
                        "Environment": {
                            "SAGEMAKER_PROGRAM": "inference.py",
                            "SAGEMAKER_SUBMIT_DIRECTORY": "$.ModelArtifacts.S3ModelArtifacts",
                        }
                    }
                ],
                "SupportedContentTypes": ["application/json"],
                "SupportedResponseMIMETypes": ["application/json"],
                "SupportedRealtimeInferenceInstanceTypes": ["ml.m5.large"],
                "SupportedTransformInstanceTypes": ["ml.m5.large"]
            }
        },
        result_path="$.RegisterModelResult"
    )

    save_model_arn = steps.Task(
        state_id="SaveModelARN",
        resource="arn:aws:states:::aws-sdk:ssm:putParameter",
        parameters={
            "Name": "/telco-churn/model-package-arn/latest",
            "Value.$": "$.RegisterModelResult.ModelPackageArn",
            "Type": "String",
            "Overwrite": True
        },
        result_path="$.SSMResult"
    )
    return training_step, register_model_step, save_model_arn

if __name__ == "__main__":
    processing_step = create_preprocessing_step()
    training_step, model_register_step, save_model_arn = create_training_step()
    workflow_definition = steps.Chain([processing_step, training_step, model_register_step, save_model_arn])


    workflow = Workflow(
        name=f"{project_prefix}-workflow",
        definition=workflow_definition,
        role=sfn_state_machine_role_arn
    )
    workflow.attach(state_machine_arn=sfn_state_machine_workflow_arn)
    workflow.update(
        definition=workflow_definition,
        role=sfn_state_machine_role_arn
    )
    execution = workflow.execute(inputs=workflow_inputs)