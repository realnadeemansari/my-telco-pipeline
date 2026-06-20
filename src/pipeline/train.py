# import subprocess
# import sys
import os
import argparse
import pandas as pd
import shutil

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
# from sklearn.externals import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# subprocess.check_call([
#     sys.executable,
#     "-m",
#     "pip",
#     "install",
#     "joblib"
# ])

import joblib

if __name__ == "__main__":
    training_data_directory = "/opt/ml/input/data/train"
    testing_data_directory = "/opt/ml/input/data/test"
    train_features_data = os.path.join(training_data_directory, "train_features.csv")
    train_labels_data = os.path.join(training_data_directory, "train_labels.csv")
    test_features_data = os.path.join(testing_data_directory, "test_features.csv")
    test_labels_data = os.path.join(testing_data_directory, "test_labels.csv")
    print("Reading input data")
    
    X_train = pd.read_csv(train_features_data)
    y_train = pd.read_csv(train_labels_data)
    X_test = pd.read_csv(test_features_data)
    y_test = pd.read_csv(test_labels_data)

    categorical_cols = X_train.select_dtypes(include="object").columns
    numerical_cols = X_train.select_dtypes(exclude="object").columns

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, numerical_cols),
        ("cat", cat_pipeline, categorical_cols)
    ])

    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred)

    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Score: {f1}")
    print(f"ROC AUC: {roc_auc}")

    model_dir = "/opt/ml/model"

    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(pipeline, os.path.join(model_dir, "model.joblib"))
    code_dir = os.path.join(model_dir, "code")
    os.makedirs(code_dir, exist_ok=True)

    shutil.copy(
        "inference.py",
        os.path.join(code_dir, "inference.py")
    )

    print("Saved model and inference code")