import os
import requests

def fetch_pr_diff(repo: str, pr_number: int) -> str:
    """
    Fetches the raw unified diff for a GitHub PR.
    Truncates to 12,000 chars to stay within LLM context limits.
    """
    token = os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.diff",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 404:
        raise ValueError(f"PR #{pr_number} not found in {repo}. Check REPO_FULL_NAME and PR_NUMBER in .env")
    if response.status_code == 401:
        raise ValueError("GitHub token is invalid or expired. Check GITHUB_TOKEN in .env")

    response.raise_for_status()

    diff = response.text

    MAX_CHARS = 12000
    if len(diff) > MAX_CHARS:
        diff = diff[:MAX_CHARS] + "\n\n[DIFF TRUNCATED — showing first 12,000 chars]"
        print(f"[MergeMind] Warning: diff truncated to {MAX_CHARS} chars")

    print(f"[MergeMind] Fetched diff: {len(diff)} chars")
    return diff


def split_diff_by_file(diff: str) -> list[dict]:
    """
    Splits a unified diff into per-file chunks.
    Returns a list of dicts: [{"filename": "auth.py", "content": "diff --git ..."}]
    """
    if not diff or not diff.strip():
        return []

    chunks = []
    current_filename = None
    current_lines = []

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            if current_filename and current_lines:
                chunks.append({
                    "filename": current_filename,
                    "content": "\n".join(current_lines)
                })
            parts = line.split(" b/")
            current_filename = parts[-1] if len(parts) > 1 else "unknown_file"
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_filename and current_lines:
        chunks.append({
            "filename": current_filename,
            "content": "\n".join(current_lines)
        })

    return chunks