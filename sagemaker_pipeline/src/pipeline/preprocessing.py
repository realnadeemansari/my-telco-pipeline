import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def load_data():
    input_path = "/opt/ml/processing/input/WA_Fn-UseC_-Telco-Customer-Churn.csv"
    df = pd.read_csv(input_path)
    return df

def preprocess_data(df):
    df["TotalCharges"] = df["TotalCharges"].replace(" ", np.nan)
    df["TotalCharges"] = df["TotalCharges"].astype(float)
    df.dropna(inplace=True)
    df.drop("customerID", axis=1, inplace=True)
    df["Churn"] = df["Churn"].map({
        "Yes": 1,
        "No": 0
    })
    X = df.drop(["Churn"], axis=1)
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    train_features_output_path = os.path.join("/opt/ml/processing/train", "train_features.csv")
    train_labels_output_path = os.path.join("/opt/ml/processing/train", "train_labels.csv")
    test_features_output_path = os.path.join("/opt/ml/processing/test", "test_features.csv")
    test_labels_output_path = os.path.join("/opt/ml/processing/test", "test_labels.csv")

    os.makedirs("/opt/ml/processing/train", exist_ok=True)
    os.makedirs("/opt/ml/processing/test", exist_ok=True)

    pd.DataFrame(X_train).to_csv(train_features_output_path, index=False)
    pd.DataFrame(y_train).to_csv(train_labels_output_path, index=False)   
    pd.DataFrame(X_test).to_csv(test_features_output_path, index=False)
    pd.DataFrame(y_test).to_csv(test_labels_output_path, index=False)
    
    print("Preprocessing completed")
    
if __name__ == "__main__":
    df = load_data()
    preprocess_data(df)