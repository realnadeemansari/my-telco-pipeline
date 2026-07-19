# Telco Customer Churn — Pipeline & Infra

**Overview**
- This repository contains a CDK-based infrastructure project (`cdk-infra/`) and a SageMaker pipeline (`sagemaker_pipeline/`) to train, package, and deploy a scikit-learn churn model.

**Contents**
- `cdk-infra/`: AWS CDK app that provisions S3, IAM, CodeBuild, CodePipeline and (optionally) a Network stack.
- `sagemaker_pipeline/`: SageMaker training, preprocessing, feature-store, monitoring helpers and Step Functions workflow.
- `mlruns/`, `models/`: local artifacts and experiment outputs (gitignored normally).

**Prerequisites**
- Python 3.11, AWS CLI configured with appropriate permissions
- Node.js + AWS CDK (for `cdk-infra`) — see `cdk-infra/requirements.txt` and `cdk-infra/README.md`
- AWS account with SageMaker, S3, IAM

**Quick setup**
1. Create and activate a virtualenv for CDK:

```bash
cd cdk-infra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install SageMaker pipeline deps (local dev):

```bash
cd sagemaker_pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**CDK: synth / diff / deploy**
- Synthesize and review changes:

```bash
cd cdk-infra
cdk synth
cdk diff
```

- Deploy to your account (example):

```bash
cdk deploy --all --require-approval never
```

The CDK app (`app.py`) creates multiple stacks. The `NetworkStack` (VPC, subnets, SGs) is separate so you can reuse networking across stacks.

**SageMaker pipeline (training → package → register → deploy)**
- The pipeline is defined in `sagemaker_pipeline/src/pipeline/run_pipeline.py` and uses Step Functions tasks to:
	- run a processing job to prepare data,
	- run a training job using `SKLearn` (script mode with `train.py`),
	- create a ModelPackage (with `InferenceSpecification`) and store its ARN in SSM.

- Important: model serving requires `inference.py` to be discoverable by the SageMaker serving container. Two valid approaches:
	1. Ship a `code.tar.gz` that contains `inference.py` at the archive root and set `SAGEMAKER_PROGRAM=inference.py` and `SAGEMAKER_SUBMIT_DIRECTORY` to that S3 URI in the model package `Environment`.
	2. Produce a combined `model.tar.gz` that contains both `model.joblib` and `inference.py` at the archive root, and point `SAGEMAKER_SUBMIT_DIRECTORY` to the model tarball.

Example (Step Functions model package parameters):

```json
"Environment": {
	"SAGEMAKER_PROGRAM": "inference.py",
	"SAGEMAKER_SUBMIT_DIRECTORY.$": "$.ModelArtifacts.S3ModelArtifacts"
}
```

Note: The `$.ModelArtifacts.S3ModelArtifacts` JSONPath must resolve to an actual S3 `s3://...` URI at runtime. If it resolves to the model tar but the tar doesn't include `inference.py` at root, the container will raise `ModuleNotFoundError: No module named 'inference'`.

**Model deployment (boto3)**
- The `sagemaker_pipeline/src/pipeline/deploy_model.py` script reads the registered `ModelPackageArn` from SSM and creates a SageMaker Model with:

```py
sm.create_model(ModelName=..., ExecutionRoleArn=..., ModelPackageName=<MODEL_PACKAGE_ARN>)
```

- Important: when using `ModelPackageName` you cannot override the model package `Environment` in `create_model()` — the package must already contain the correct `SAGEMAKER_PROGRAM` and `SAGEMAKER_SUBMIT_DIRECTORY`.

**Testing & CI**
- CDK unit tests: `cdk-infra/tests/` (uses `pytest`).
- Local python syntax check:

```bash
python -m compileall -q cdk-infra sagemaker_pipeline
```

**Common troubleshooting**
- Error: `Object of type ExecutionInput is not JSON serializable`
	- Do not pass `ExecutionInput` (StepFunctions objects) inside estimator `hyperparameters` — use job_name in the TrainingStep instead.
- Error: `AttributeError: 'NoneType' object has no attribute 'startswith'`
	- Indicates `SAGEMAKER_PROGRAM` or `SAGEMAKER_SUBMIT_DIRECTORY` are missing or literal tokens; ensure model package `Environment` is correct and uses `.$` for JSONPath when building with Step Functions.
- Error: `ModuleNotFoundError: No module named 'inference'`
	- Ensure `inference.py` is at the root of the code archive referenced by `SAGEMAKER_SUBMIT_DIRECTORY`.

**Next improvements (suggested)**
- Add a `Makefile` or CLI wrapper to synth/deploy/sm-pipeline run workflows.
- Add a packaging helper that builds `code.tar.gz` with `inference.py` and uploads it to S3 (used by the Step Functions register step).
- Add unit tests for SageMaker pipeline helpers and an integration test using a small dataset.

**Contact / further help**
- Tell me if you want me to scaffold a `code.tar.gz` creator and update the Step Functions `createModelPackage` call to point to that uploaded code bundle, and I’ll implement it.
