import requests
import pandas as pd
import os
import time
import base64
from dotenv import load_dotenv

# Load token
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}

def get_bug_fix_commits(repo_name, max_commits=50):
    """Fetch commits that are bug fixes"""
    url = f"https://api.github.com/repos/{repo_name}/commits?per_page=100"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching commits for {repo_name}")
        return []
    
    commits = response.json()
    bug_commits = []
    
    bug_keywords = ['fix', 'bug', 'error', 'issue', 'crash', 'resolve', 'patch']
    
    for commit in commits:
        message = commit['commit']['message'].lower()
        is_bug = any(keyword in message for keyword in bug_keywords)
        bug_commits.append({
            "repo": repo_name,
            "sha": commit['sha'],
            "message": commit['commit']['message'],
            "is_bug": 1 if is_bug else 0
        })
    
    print(f"Found {len(bug_commits)} commits in {repo_name}")
    return bug_commits[:max_commits]

def get_code_from_commit(repo_name, sha):
    """Get actual code files changed in a commit"""
    url = f"https://api.github.com/repos/{repo_name}/commits/{sha}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return []
    
    data = response.json()
    files = data.get('files', [])
    code_files = []
    
    for file in files:
        filename = file.get('filename', '')
        
        # Only get Python files
        if not filename.endswith('.py'):
            continue
        
        patch = file.get('patch', '')  # actual code changes
        
        if patch:
            code_files.append({
                "filename": filename,
                "code": patch,
                "changes": file.get('changes', 0),
                "additions": file.get('additions', 0),
                "deletions": file.get('deletions', 0)
            })
    
    return code_files

def collect_data(repos_list, max_commits=30):
    """Main data collection function"""
    all_data = []
    
    for repo_name in repos_list:
        print(f"\nProcessing repo: {repo_name}")
        
        # Get bug fix commits
        commits = get_bug_fix_commits(repo_name, max_commits)
        
        for commit in commits:
            # Get code files for each commit
            code_files = get_code_from_commit(repo_name, commit['sha'])
            time.sleep(0.5)  # avoid rate limiting
            
            for code_file in code_files:
                all_data.append({
                    "repo": repo_name,
                    "sha": commit['sha'],
                    "commit_message": commit['message'],
                    "filename": code_file['filename'],
                    "code": code_file['code'],
                    "changes": code_file['changes'],
                    "is_bug": commit['is_bug']
                })
    
    return all_data

if __name__ == "__main__":
    print("Starting data collection...")
    
    # Popular Python repos with good bug history
    repos = [
        "psf/requests",
        "pallets/flask",
        "django/django",
        "numpy/numpy",
        "pandas-dev/pandas"
    ]
    
    # Collect data
    all_data = collect_data(repos, max_commits=30)
    
    if not all_data:
        print("No data collected!")
    else:
        # Save to CSV
        df = pd.DataFrame(all_data)
        df.to_csv("data/code_data.csv", index=False)
        print(f"\nCollected {len(all_data)} code file samples")
        print(f"Bug samples: {df['is_bug'].sum()}")
        print(f"Non-bug samples: {len(df) - df['is_bug'].sum()}")
        print("Saved to data/code_data.csv")
        print("\nData collection complete!")