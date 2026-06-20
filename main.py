import os
import time
from dotenv import load_dotenv

# Load .env for local development — no effect in GitHub Actions (env vars already set there)
load_dotenv()

from src.diff_fetcher import fetch_pr_diff, split_diff_by_file
from src.review_pipeline import run_review_pipeline
from src.comment_poster import post_review_comment
from src.logger import log_review

def main():
    repo = os.environ["REPO_FULL_NAME"]
    pr_number = int(os.environ["PR_NUMBER"])
    sha = os.environ.get("PR_HEAD_SHA", "local")

    print(f"\n{'='*50}")
    print(f"  MergeMind — Reviewing PR #{pr_number} in {repo}")
    print(f"{'='*50}\n")

    start = time.time()

    # Step 1: Fetch diff
    try:
        diff = fetch_pr_diff(repo, pr_number)
    except Exception as e:
        print(f"[MergeMind] ERROR fetching diff: {e}")
        return

    if not diff or len(diff.strip()) < 10:
        print("[MergeMind] Diff is empty or trivial. Skipping review.")
        return

    # Step 2: Split into per-file chunks (handles large/multi-file PRs)
    chunks = split_diff_by_file(diff)
    print(f"[MergeMind] Diff contains {len(chunks)} file(s)")

    # Step 3: Run LLM pipeline (chunked if multiple files, single-pass otherwise)
    try:
        review = run_review_pipeline(diff, file_chunks=chunks)
    except Exception as e:
        print(f"[MergeMind] ERROR in review pipeline: {e}")
        return

    elapsed = round(time.time() - start, 2)

    # Step 4: Post comment
    try:
        post_review_comment(repo, pr_number, review)
    except Exception as e:
        print(f"[MergeMind] ERROR posting comment: {e}")
        return

    # Step 5: Log
    try:
        log_review(repo, pr_number, sha, review, elapsed)
    except Exception as e:
        print(f"[MergeMind] WARNING: logging failed (non-fatal): {e}")

    print(f"\n[MergeMind] Done in {elapsed}s ✓")

if __name__ == "__main__":
    main()