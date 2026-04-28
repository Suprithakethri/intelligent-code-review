import streamlit as st
import requests
import re
import os
import html
from dotenv import load_dotenv

# -----------------------------
# 🔐 LOAD ENV
# -----------------------------
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else None
}

# -----------------------------
# 🧠 DETECTION FUNCTIONS
# -----------------------------
def detect_division_by_zero(line):
    return "/" in line and "len(" in line

def detect_index_error(line):
    return "range(len(" in line and "+ 1" in line

def detect_modify_during_iteration(line):
    return ".remove(" in line or ".append(" in line

def detect_dangerous_exec(line):
    return "exec(" in line or "eval(" in line

def detect_hardcoded_credentials(line):
    keywords = ["password", "passwd", "secret", "token", "api_key", "apikey"]
    line_lower = line.lower()
    return any(k in line_lower for k in keywords) and "=" in line


# -----------------------------
# 🔍 ANALYZE CODE
# -----------------------------
def analyze_code(code):
    issues = []
    lines = code.split("\n")

    for i, line in enumerate(lines, start=1):

        if detect_division_by_zero(line):
            issues.append(("LOW", i, "Possible division by zero"))

        if detect_index_error(line):
            issues.append(("MEDIUM", i, "Possible index out of range"))

        if detect_modify_during_iteration(line):
            issues.append(("MEDIUM", i, "Modifying list during iteration"))

        if detect_dangerous_exec(line):
            issues.append(("HIGH", i, "Use of eval/exec is dangerous"))

        if detect_hardcoded_credentials(line):
            issues.append(("HIGH", i, "Hardcoded credentials"))

    return issues


# -----------------------------
# 🎨 DISPLAY ISSUES (FIXED HTML)
# -----------------------------
def show_issues(issues, code=None):

    lines = code.split("\n") if code else []

    if not issues:
        st.success("✅ No issues found")
        return

    st.subheader("Detected Issues")
    st.caption(f"{len(issues)} issues detected")

    for severity, line_no, msg in issues:

        if severity == "HIGH":
            color = "#ff4d4d"
            bg = "#2a0a0a"
            badge = "🔴 HIGH"

        elif severity == "MEDIUM":
            color = "#f7b731"
            bg = "#2a1f0a"
            badge = "🟠 MEDIUM"

        else:
            color = "#4dabf7"
            bg = "#0a1a2a"
            badge = "🔵 LOW"

        clean_msg = html.escape(msg)
        code_line = html.escape(lines[line_no - 1]) if code and line_no <= len(lines) else ""

        # 🚨 NO INDENTATION HERE (THIS FIXES YOUR BUG)
        html_block = f"""<div style="background-color:{bg}; border-radius:10px; padding:12px; margin-bottom:12px; border-left:4px solid {color};">

<div style="font-weight:600; color:{color}; margin-bottom:6px;">
{badge} — Line {line_no}
</div>

<div style="color:#ddd; font-size:14px; margin-bottom:8px;">
{clean_msg}
</div>

<div style="background-color:#111; padding:8px; border-radius:6px; font-family:monospace; font-size:13px; color:#e6e6e6; overflow-x:auto;">
{code_line}
</div>

</div>"""

        st.markdown(html_block, unsafe_allow_html=True)


# -----------------------------
# 🌐 FETCH GITHUB FILES
# -----------------------------
def get_python_files(repo_url):
    repo_name = repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_name}/contents"

    response = requests.get(api_url, headers=HEADERS)

    if response.status_code != 200:
        return []

    files = response.json()
    py_files = []

    for file in files:
        if file["type"] == "file" and file["name"].endswith(".py"):
            py_files.append(file["download_url"])

    return py_files


# -----------------------------
# 🎯 UI
# -----------------------------
st.set_page_config(page_title="AI Code Review", layout="wide")

st.title("AI Code Review Assistant")

mode = st.radio("Choose Input Mode", ["Paste Code", "GitHub Repo"])


# -----------------------------
# 📌 PASTE MODE
# -----------------------------
if mode == "Paste Code":

    code = st.text_area(
        "Paste your Python code here",
        height=300
    )

    if st.button("Analyze Code"):
        issues = analyze_code(code)
        show_issues(issues, code)


# -----------------------------
# 📌 GITHUB MODE
# -----------------------------
else:

    repo_url = st.text_input("Enter GitHub Repo URL")

    if st.button("Analyze Code"):

        files = get_python_files(repo_url)

        if not files:
            st.warning("No Python files found")
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
                        show_issues(issues, code)