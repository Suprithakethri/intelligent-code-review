from flask import Flask, render_template, request
from analyzer import analyze_code
from github_utils import get_python_files, get_file_content

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    file_count = None

    code_input = ""
    repo_url = ""
    selected_mode = "code"

    if request.method == "POST":
        selected_mode = request.form.get("mode")

        # -------- MANUAL --------
        if selected_mode == "code":
            code_input = request.form.get("code_input", "")

            issues = analyze_code(code_input)

            results = [{
                "file": "Manual Input",
                "issues": issues,
                "issue_count": len(issues)
            }]

            file_count = 1

        # -------- GITHUB --------
        elif selected_mode == "repo":
            repo_url = request.form.get("repo_url", "")

            files = get_python_files(repo_url)
            file_count = len(files)

            for file in files:
                code = get_file_content(repo_url, file)
                issues = analyze_code(code)

                results.append({
                    "file": file,
                    "issues": issues,
                    "issue_count": len(issues)
                })

    return render_template(
        "index.html",
        results=results,
        file_count=file_count,
        code_input=code_input,
        repo_url=repo_url,
        selected_mode=selected_mode
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)