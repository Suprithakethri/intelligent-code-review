import pickle
import os
import re
from dotenv import load_dotenv

# Load saved model and vectorizer
def load_model():
    """Load the trained model and vectorizer"""
    with open("models/bug_predictor.pkl", "rb") as f:
        model = pickle.load(f)
    
    with open("models/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    
    print("✅ Model and vectorizer loaded!")
    return model, vectorizer

def clean_text(text):
    """Clean input text same way as preprocessing"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def predict(commit_message, model, vectorizer):
    """Predict if a commit message is bug-related"""
    
    # Clean the message
    cleaned = clean_text(commit_message)
    
    # Convert to TF-IDF vector
    vector = vectorizer.transform([cleaned])
    
    # Predict
    prediction = model.predict(vector)[0]
    probability = model.predict_proba(vector)[0]
    
    bug_prob = round(probability[1] * 100, 2)
    not_bug_prob = round(probability[0] * 100, 2)
    
    return {
        "message": commit_message,
        "cleaned": cleaned,
        "prediction": "BUG" if prediction == 1 else "NOT BUG",
        "bug_probability": f"{bug_prob}%",
        "not_bug_probability": f"{not_bug_prob}%"
    }

def print_result(result):
    """Print prediction result nicely"""
    print("\n" + "="*50)
    print(f"Message: {result['message']}")
    print(f"Prediction: {result['prediction']}")
    print(f"Bug Probability: {result['bug_probability']}")
    print(f"Not Bug Probability: {result['not_bug_probability']}")
    print("="*50)

if __name__ == "__main__":
    print("Loading prediction model...")
    
    # Load model
    model, vectorizer = load_model()
    
    # Test with some example messages
    test_messages = [
        "fix null pointer exception in login module",
        "add new feature for user dashboard",
        "bug in payment processing causing crash",
        "update README documentation",
        "resolve issue with database connection error"
    ]
    
    print("\nRunning predictions on test messages...\n")
    
    for message in test_messages:
        result = predict(message, model, vectorizer)
        print_result(result)
    
    print("\n Prediction script working!")