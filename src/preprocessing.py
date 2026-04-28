import pandas as pd
import re
import os

def load_data():
    """Load the collected code data"""
    df = pd.read_csv("data/code_data.csv")
    print(f"Loaded {len(df)} code file samples")
    return df

def clean_code(code):
    """Clean a code snippet"""
    if not isinstance(code, str):
        return ""
    
    # Remove diff markers (lines starting with + or -)
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.startswith('+++') or line.startswith('---'):
            continue
        if line.startswith('+') or line.startswith('-'):
            line = line[1:]  # remove the diff marker
        cleaned_lines.append(line)
    
    code = '\n'.join(cleaned_lines)
    code = re.sub(r'#.*', '', code)           # remove comments
    code = re.sub(r'\'\'\'.*?\'\'\'', '', code, flags=re.DOTALL)  # remove docstrings
    code = re.sub(r'\"\"\".*?\"\"\"', '', code, flags=re.DOTALL)  # remove docstrings
    code = re.sub(r'\s+', ' ', code)           # remove extra spaces
    code = code.strip()
    return code

def extract_code_features(code):
    """Extract basic features from code"""
    if not isinstance(code, str) or code == "":
        return {
            "num_lines": 0,
            "num_functions": 0,
            "num_loops": 0,
            "num_conditions": 0,
            "num_exceptions": 0,
            "code_length": 0
        }
    
    return {
        "num_lines": len(code.split('\n')),
        "num_functions": len(re.findall(r'\bdef\b', code)),
        "num_loops": len(re.findall(r'\bfor\b|\bwhile\b', code)),
        "num_conditions": len(re.findall(r'\bif\b|\belif\b', code)),
        "num_exceptions": len(re.findall(r'\btry\b|\bexcept\b', code)),
        "code_length": len(code)
    }

def preprocess(df):
    """Full preprocessing pipeline"""
    print("Cleaning code snippets...")
    df['cleaned_code'] = df['code'].apply(clean_code)
    
    # Remove empty code
    df = df[df['cleaned_code'] != ""]
    
    print("Extracting code features...")
    features = df['cleaned_code'].apply(extract_code_features)
    features_df = pd.DataFrame(list(features))
    
    # Combine with original dataframe
    df = pd.concat([df.reset_index(drop=True), features_df], axis=1)
    
    # Show stats
    total = len(df)
    bug_count = df['is_bug'].sum()
    print(f"Total samples: {total}")
    print(f"Bug samples: {bug_count}")
    print(f"Non-bug samples: {total - bug_count}")
    
    return df

def save_processed_data(df):
    """Save cleaned data"""
    df.to_csv("data/processed_code.csv", index=False)
    print("Saved to data/processed_code.csv")

if __name__ == "__main__":
    print("Starting preprocessing...")
    
    # Step 1: Load data
    df = load_data()
    
    # Step 2: Preprocess
    df = preprocess(df)
    
    # Step 3: Save
    save_processed_data(df)
    
    print("Preprocessing complete!")