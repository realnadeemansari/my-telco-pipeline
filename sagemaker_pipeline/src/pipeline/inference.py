import os
import json
# import joblib
import pandas as pd
import subprocess
import sys
from sklearn.externals import joblib


def model_fn(model_dir):
    # subprocess.check_call([
    #     sys.executable,
    #     "-m",
    #     "pip",
    #     "install",
    #     "joblib"
    # ])
    model_path = os.path.join(model_dir, "model.joblib")
    model = joblib.load(model_path)
    return model


def input_fn(request_body, content_type):
    if content_type == "application/json":
        data = json.loads(request_body)
        return pd.DataFrame(data)

    raise ValueError(f"Unsupported content type: {content_type}")


def predict_fn(input_data, model):
    prediction = model.predict(input_data)
    return prediction


def output_fn(prediction, accept):
    return json.dumps(prediction.tolist())