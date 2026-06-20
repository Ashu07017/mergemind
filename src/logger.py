import json
import os
from datetime import datetime, timezone

LOG_FILE = "reviews.json"

def log_review(repo: str, pr_number: int, sha: str, review: dict, elapsed: float):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": repo,
        "pr_number": pr_number,
        "sha": sha[:7] if len(sha) >= 7 else sha,
        "elapsed_seconds": elapsed,
        "overall_score": review.get("overall_score"),
        "bug_count": len(review.get("bugs", [])),
        "security_count": len(review.get("security", [])),
        "style_count": len(review.get("style", [])),
        "high_severity_count": sum(
            1 for cat in ["bugs", "security"]
            for item in review.get(cat, [])
            if item.get("severity") == "high"
        ),
        "summary": review.get("summary", ""),
    }

    existing = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    existing.append(record)

    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"[MergeMind] Logged review record #{len(existing)}")