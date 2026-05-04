import requests

def get_repo_info(repo_url):
    parts = repo_url.replace("https://github.com/", "").split("/")
    return parts[0], parts[1]


def get_python_files(repo_url):
    owner, repo = get_repo_info(repo_url)

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()

    return [
        file["path"]
        for file in data["tree"]
        if file["path"].endswith(".py")
    ]


def get_file_content(repo_url, path):
    owner, repo = get_repo_info(repo_url)

    url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
    response = requests.get(url)

    if response.status_code != 200:
        return ""

    return response.text