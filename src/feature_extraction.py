import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import pickle
import numpy as np

def load_processed_data():
    """Load preprocessed code data"""
    df = pd.read_csv("data/processed_code.csv")
    print(f"Loaded {len(df)} processed code samples")
    return df

def extract_tfidf_features(df):
    """Convert code into TF-IDF vectors"""
    print("Extracting TF-IDF features from code...")
    
    vectorizer = TfidfVectorizer(
        max_features=500,
        ngram_range=(1, 2),
        stop_words='english',
        analyzer='word',
        token_pattern=r'[a-zA-Z_][a-zA-Z0-9_]*'  # captures code tokens
    )
    
    X_tfidf = vectorizer.fit_transform(df['cleaned_code'])
    print(f"TF-IDF matrix shape: {X_tfidf.shape}")
    
    return X_tfidf, vectorizer

def extract_code_metrics(df):
    """Extract numerical code metrics"""
    print("Extracting code metrics...")
    
    metric_columns = [
        'num_lines',
        'num_functions',
        'num_loops',
        'num_conditions',
        'num_exceptions',
        'code_length',
        'changes'
    ]
    
    # Fill missing values with 0
    metrics = df[metric_columns].fillna(0)
    
    # Scale the metrics
    scaler = StandardScaler()
    X_metrics = scaler.fit_transform(metrics)
    
    return X_metrics, scaler, metric_columns

def combine_features(X_tfidf, X_metrics):
    """Combine TF-IDF and code metrics into one feature matrix"""
    print("Combining TF-IDF and code metrics...")
    X_combined = np.hstack([X_tfidf.toarray(), X_metrics])
    print(f"Combined feature matrix shape: {X_combined.shape}")
    return X_combined

def save_features(X_combined, y, vectorizer, scaler, vectorizer_columns, metric_columns):
    """Save everything needed for model training and prediction"""
    
    # Save vectorizer
    with open("models/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    # Save scaler
    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    
    # Save feature matrix
    feature_df = pd.DataFrame(X_combined)
    feature_df['is_bug'] = y.values
    feature_df.to_csv("data/features.csv", index=False)
    
    print("Vectorizer saved to models/vectorizer.pkl")
    print("Scaler saved to models/scaler.pkl")
    print("Features saved to data/features.csv")

if __name__ == "__main__":
    print("Starting feature extraction...")
    
    # Step 1: Load data
    df = load_processed_data()
    
    # Step 2: TF-IDF on code
    X_tfidf, vectorizer = extract_tfidf_features(df)
    
    # Step 3: Code metrics
    X_metrics, scaler, metric_columns = extract_code_metrics(df)
    
    # Step 4: Combine both
    X_combined = combine_features(X_tfidf, X_metrics)
    
    # Step 5: Save
    y = df['is_bug']
    save_features(
        X_combined, y,
        vectorizer, scaler,
        vectorizer.get_feature_names_out(),
        metric_columns
    )
    
    print("Feature extraction complete!")