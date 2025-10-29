import os
import pandas as pd
import numpy as np
from typing import List
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


DATA_URL = "https://raw.githubusercontent.com/hadt222/CSCE_5380/refs/heads/main/heart-3.csv"
DEFAULT_OUTPUT_PATH = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "heart_pipeline.joblib"))


def load_data() -> pd.DataFrame:
    """Load and clean the heart disease dataset following the notebook approach."""
    data_path = os.getenv("DATA_PATH", DATA_URL)
    df = pd.read_csv(data_path)
    
    # Basic cleaning
    df = df.drop_duplicates()
    df.columns = [c.strip() for c in df.columns]  # normalize column names
    
    # Rename thalch -> thalach for consistency with API
    if "thalch" in df.columns and "thalach" not in df.columns:
        df = df.rename(columns={"thalch": "thalach"})
    
    return df


def get_feature_columns() -> List[str]:
    """Get the feature columns expected by the API."""
    return [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal",
    ]


def train_and_save_model() -> str:
    """Train and save the heart disease prediction model following the notebook approach."""
    df = load_data()
    
    # Binary target: presence of disease (num > 0)
    if "num" not in df.columns:
        raise RuntimeError("Dataset missing target column 'num'")
    
    y = (df['num'] > 0).astype(int)
    
    # Drop leakage/ID columns from features
    X = df.drop(columns=['num', 'target', 'id', 'dataset'], errors='ignore')
    
    # Separate numeric and categorical columns
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]
    
    print(f"Numeric columns: {num_cols}")
    print(f"Categorical columns: {cat_cols}")
    
    # Preprocessing pipelines
    numeric_pipe = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_pipe = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('ohe', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Column transformer
    preprocess = ColumnTransformer(
        transformers=[
            ('num', numeric_pipe, num_cols),
            ('cat', categorical_pipe, cat_cols)
        ],
        remainder='drop'
    )
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # Create the full pipeline with Random Forest (best model from notebook)
    pipeline = Pipeline(steps=[
        ('preprocess', preprocess),
        ('clf', RandomForestClassifier(n_estimators=200, random_state=42))
    ])
    
    # Train the model
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Disease', 'Disease']))
    
    # Persist the model
    os.makedirs(os.path.dirname(DEFAULT_OUTPUT_PATH), exist_ok=True)
    joblib.dump(pipeline, DEFAULT_OUTPUT_PATH)
    print(f"\nModel saved to: {DEFAULT_OUTPUT_PATH}")
    
    return DEFAULT_OUTPUT_PATH


if __name__ == "__main__":
    train_and_save_model()



