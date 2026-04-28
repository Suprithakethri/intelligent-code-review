import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def load_features():
    """Load extracted features"""
    df = pd.read_csv("data/features.csv")
    X = df.drop('is_bug', axis=1)
    y = df['is_bug']
    print(f"Loaded features: {X.shape}")
    return X, y

def train_model(X, y):
    """Train and evaluate ML models"""
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Testing set: {len(X_test)} samples")
    
    # Train Logistic Regression
    print("\nTraining Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    lr_accuracy = accuracy_score(y_test, lr_preds)
    print(f"Logistic Regression Accuracy: {lr_accuracy:.2%}")
    
    # Train Random Forest
    print("\nTraining Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_preds)
    print(f"Random Forest Accuracy: {rf_accuracy:.2%}")
    
    # Pick best model
    if rf_accuracy >= lr_accuracy:
        best_model = rf_model
        best_name = "Random Forest"
        best_preds = rf_preds
    else:
        best_model = lr_model
        best_name = "Logistic Regression"
        best_preds = lr_preds
    
    print(f"\nBest Model: {best_name}")
    print("\nClassification Report:")
    print(classification_report(y_test, best_preds,
          target_names=["Not Bug", "Bug"]))
    
    return best_model, best_name

def save_model(model, name):
    """Save the best model"""
    with open("models/bug_predictor.pkl", "wb") as f:
        pickle.dump(model, f)
    print(f"{name} saved to models/bug_predictor.pkl")

if __name__ == "__main__":
    print("Starting model training...")
    
    # Step 1: Load features
    X, y = load_features()
    
    # Step 2: Train
    best_model, best_name = train_model(X, y)
    
    # Step 3: Save
    save_model(best_model, best_name)
    
    print("\nModel training complete!")