def analyze_code(code):
    issues = []
    lines = code.split("\n")

    for i, line in enumerate(lines, start=1):

        if "password" in line.lower() or "api_key" in line.lower():
            issues.append(("HIGH", i, "Hardcoded credentials", line.strip()))

        if "/ 0" in line:
            issues.append(("HIGH", i, "Possible division by zero", line.strip()))

        if "range(len(" in line and "+ 1" in line:
            issues.append(("MEDIUM", i, "Possible index out of range", line.strip()))

        if "for " in line and " in " in line:
            for future_line in lines[i:]:
                if ".append(" in future_line:
                    issues.append(("MEDIUM", i, "Modifying list during iteration", line.strip()))
                    break

    return issues