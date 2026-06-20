import os
import json
import re
from groq import Groq

def run_review_pipeline(diff: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    strictness = os.environ.get("STRICTNESS", "standard")
    language = os.environ.get("REVIEW_LANGUAGE", "any")

    strictness_note = {
        "strict": "Flag even minor issues and style inconsistencies.",
        "standard": "Focus on bugs, security issues, and significant style problems.",
        "lenient": "Only flag critical bugs and serious security vulnerabilities.",
    }.get(strictness, "Focus on bugs, security issues, and significant style problems.")

    lang_note = f"The codebase is primarily {language}." if language != "any" else "The codebase may use any language."

    system_prompt = """You are MergeMind, an expert code reviewer. You analyze code diffs and return structured JSON feedback.
You are precise, concise, and constructive. You never hallucinate line numbers.
You always respond with valid JSON only — no markdown fences, no preamble, no text outside the JSON object."""

    user_prompt = f"""Review this pull request diff and return a JSON object exactly matching this schema:

{{
  "summary": "<2-3 sentence overview of what this PR does and overall quality>",
  "bugs": [
    {{
      "severity": "high|medium|low",
      "file": "<filename or unknown>",
      "line": "<line number or N/A>",
      "description": "<what the bug is>",
      "suggestion": "<how to fix it>"
    }}
  ],
  "security": [
    {{
      "severity": "high|medium|low",
      "file": "<filename or unknown>",
      "line": "<line number or N/A>",
      "description": "<what the vulnerability is>",
      "suggestion": "<how to fix it>"
    }}
  ],
  "style": [
    {{
      "severity": "medium|low",
      "file": "<filename or unknown>",
      "line": "<line number or N/A>",
      "description": "<style or best practice issue>",
      "suggestion": "<improvement>"
    }}
  ],
  "positive": [
    "<one specific thing done well>"
  ],
  "overall_score": "<integer 1-10>"
}}

Rules:
- Return ONLY the JSON object. No markdown, no prose outside JSON.
- If a category has no findings, return an empty list [].
- Maximum 4 items per category.
- {lang_note}
- {strictness_note}

DIFF TO REVIEW:
{diff}"""

    try:
        print("[MergeMind] Calling Groq API...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        raw_text = response.choices[0].message.content.strip()

        # Strip markdown fences if model wraps output anyway
        raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text)

        print(f"[MergeMind] Raw response (first 300 chars): {raw_text[:300]}")

        review = json.loads(raw_text)
        print(f"[MergeMind] Parsed successfully. Score: {review.get('overall_score')}")
        return review

    except json.JSONDecodeError as e:
        print(f"[MergeMind] JSON parse error: {e}")
        return _fallback_review(f"JSON parse failed: {e}")
    except Exception as e:
        print(f"[MergeMind] Pipeline error: {e}")
        return _fallback_review(str(e))


def _fallback_review(reason: str) -> dict:
    return {
        "summary": f"MergeMind encountered an error during review: {reason}",
        "bugs": [],
        "security": [],
        "style": [],
        "positive": [],
        "overall_score": "N/A",
    }