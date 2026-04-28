import streamlit as st
import requests
import re
from dotenv import load_dotenv
import os

# ------------------------------
# 🔐 LOAD TOKEN (SAFE)
# ------------------------------
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {}
if GITHUB_TOKEN:
    HEADERS = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

# ------------------------------
# 🔍 DETECTION FUNCTIONS
# ------------------------------

def detect_division_by_zero(line):
    return "/" in line and "len(" in line

def detect_index_error(line):
    return "range(len(" in line and "+ 1" in line

def detect_modify_during_iteration(line):
    return ".remove(" in line or ".append(" in line

def detect_dangerous_exec(line):
    return "exec(" in line or "eval(" in line


def detect_hardcoded_credentials(line):
    line_lower = line.lower()

    keywords = ["password", "passwd", "secret", "token", "api_key", "apikey"]

    if not any(k in line_lower for k in keywords):
        return False

    if "=" not in line:
        return False

    parts = line.split("=", 1)
    key = parts[0].strip()
    value = parts[1].strip()

    if key.isupper():
        return False

    if not re.match(r'["\'].*["\']', value):
        return False

    safe_words = ["none", "null", "true", "false", "example", "test", "dummy"]
    if any(safe in value.lower() for safe in safe_words):
        return False

    if len(value) < 8:
        return False

    return True


# ------------------------------
# 📂 FETCH FILES FROM GITHUB
# ------------------------------

def get_python_files(repo_url):
    try:
        parts = repo_url.replace("https://github.com/", "").split("/")
        owner, repo = parts[0], parts[1]

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

        files = []

        def fetch_dir(url):
            res = requests.get(url, headers=HEADERS)

            if res.status_code != 200:
                st.error("⚠️ GitHub API Error (check token or repo)")
                return

            for item in res.json():
                if item["type"] == "file" and item["name"].endswith(".py"):
                    files.append(item["download_url"])
                elif item["type"] == "dir":
                    fetch_dir(item["url"])

        fetch_dir(api_url)
        return files

    except:
        st.error("Invalid GitHub URL")
        return []


# ------------------------------
# 🧠 ANALYZE CODE
# ------------------------------

def analyze_code(code):
    issues = []
    lines = code.split("\n")

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        if line_stripped.startswith("#"):
            continue

        if detect_division_by_zero(line):
            issues.append(("LOW", i+1, "Possible division by zero"))

        if detect_index_error(line):
            issues.append(("HIGH", i+1, "Index out of bounds"))

        if detect_modify_during_iteration(line):
            issues.append(("MEDIUM", i+1, "Modifying list during iteration"))

        if detect_dangerous_exec(line):
            issues.append(("HIGH", i+1, "Dangerous function usage"))

        if detect_hardcoded_credentials(line):
            issues.append(("HIGH", i+1, "Hardcoded credentials"))

    return issues


# ------------------------------
# 🎨 UI
# ------------------------------

st.title("AI Code Review Assistant")

mode = st.radio("Choose Input Mode", ["Paste Code", "GitHub Repo"])


# ------------------------------
# 📌 PASTE MODE
# ------------------------------

if mode == "Paste Code":
    code = st.text_area("Paste your Python code here")

    if st.button("Analyze Code"):
        issues = analyze_code(code)

        st.subheader("Detected Issues")

        if not issues:
            st.success("✅ No issues found")
        else:
            for severity, line_no, msg in issues:
                st.write(f"🔹 {severity} — Line {line_no}: {msg}")


# ------------------------------
# 📌 GITHUB MODE
# ------------------------------

elif mode == "GitHub Repo":
    repo_url = st.text_input("Enter GitHub Repo URL")

    if st.button("Analyze Code"):

        files = get_python_files(repo_url)

        if not files:
            st.error("No Python files found or repo error.")
        else:
            st.success(f"Found {len(files)} Python files")

            for file_url in files:
                file_name = file_url.split("/")[-1]

                code = requests.get(file_url).text
                issues = analyze_code(code)

                with st.expander(f"{file_name} — {len(issues)} issues"):

                    if not issues:
                        st.success("✅ No issues found")
                    else:
                        for severity, line_no, msg in issues:
                            st.write(f"🔹 {severity} — Line {line_no}: {msg}")