from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker import Session
import sagemaker
import boto3
from stepfunctions import steps
from datetime import datetime

session = Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()
region = boto3.Session().region_name
bucket_prefix = "telco-pipeline"
current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def create_preprocessing_step():
    sklearn_processor = SKLearnProcessor(
        framework_version="1.2-1",
        instance_type="ml.m5.xlarge",
        instance_count=1,
        role=role,
        py_version="py3"
    )
    
    processor_args = sklearn_processor.run(
        code="preprocessing.py",
        inputs=[
            ProcessingInput(
                input_name="data",
                source=f"s3://{bucket}/telco/data",
                destination="/opt/ml/processing/input"
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
        ]
    )
    preprocessing_step = steps.ProcessingStep(
        state_id="PreprocessingStep",
        processor=sklearn_processor,
        job_name="telco-preprocessing-" + current_time,
        inputs=processor_args["ProcessingInputs"],
        outputs=processor_args["ProcessingOutputConfig"]["Outputs"],
        container_entrypoint=processor_args["AppSpecification"]["ContainerEntrypoint"],
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
        source_dir="src/pipeline",
        framework_version="1.2-1",
        instance_type="ml.m5.large",
        role=role,
        py_version="py3",
        output_path=f"s3://{bucket}/{bucket_prefix}/model"
    )
    
    training_step = steps.TrainingStep(
        state_id="TrainingStep",
        estimator=sklearn_estimator,
        job_name="telco-training-" + current_time,
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
            "ModelPackageGroupdName": "telco-churn-model-package",
            "ModelPackageDescription": "Model package for telco churn prediction",
            "ModelApprovalStatus": "PendingManualApproval",
            "InferenceSpecification": {
                "Containers": [
                    {
                        "Image": image_uri,
                        "ModelDataUrl.$": "$.TrainingResults.ModelArtifacts.S3ModelArtifacts",
                        "Environment": {
                            "SAGEMAKER_PROGRAM": "inference.py",
                            "SAGEMAKER_SUBMIT_DIRECTORY": "$.TrainingResults.ModelArtifacts.S3ModelArtifacts",
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
    
    return training_step, register_model_step



