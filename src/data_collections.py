import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Explicitly point to .env in root folder
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv("GITHUB_TOKEN")

print("Token loaded:", TOKEN)

HEADERS = {"Authorization": f"token {TOKEN}"}

def get_repos(language="python", min_stars=50, max_repos=10):
    """Fetch popular Python repos from GitHub"""
    repos = []
    url = f"https://api.github.com/search/repositories?q=language:{language}+stars:>{min_stars}&sort=stars&per_page=10"
    
    response = requests.get(url, headers=HEADERS)
    print("Status code:", response.status_code)
    print("Response:", response.json())  # debug line
    
    data = response.json()
    
    if "items" not in data:
        print("Error: 'items' not in response. Check token or API limit.")
        return []
    
    for repo in data["items"][:max_repos]:
        repos.append({
            "name": repo["full_name"],
            "stars": repo["stargazers_count"],
            "url": repo["html_url"]
        })
    
    print(f"Fetched {len(repos)} repositories")
    return repos

def get_commits(repo_name, max_commits=50):
    """Fetch commit history for a repo"""
    commits = []
    url = f"https://api.github.com/repos/{repo_name}/commits?per_page=50"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching commits for {repo_name}: {response.status_code}")
        return []
    
    data = response.json()
    
    for commit in data[:max_commits]:
        commits.append({
            "repo": repo_name,
            "message": commit["commit"]["message"],
            "date": commit["commit"]["author"]["date"],
            "author": commit["commit"]["author"]["name"]
        })
    
    time.sleep(1)  # avoid hitting API rate limit
    print(f"Fetched {len(commits)} commits from {repo_name}")
    return commits

def save_data(repos, all_commits):
    """Save collected data to CSV files"""
    pd.DataFrame(repos).to_csv("data/repos.csv", index=False)
    pd.DataFrame(all_commits).to_csv("data/commits.csv", index=False)
    print("Data saved to data/repos.csv and data/commits.csv")

if __name__ == "__main__":
    print("Starting data collection...")
    
    # Step 1: Get repos
    repos = get_repos()
    
    if not repos:
        print("No repos fetched. Exiting.")
        exit()
    
    # Step 2: Get commits for each repo
    all_commits = []
    for repo in repos:
        commits = get_commits(repo["name"])
        all_commits.extend(commits)
    
    # Step 3: Save to CSV
    save_data(repos, all_commits)
    
    print("Data collection complete!")