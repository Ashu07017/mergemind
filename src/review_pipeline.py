import os
import json
import re
from groq import Groq

MAX_CHUNK_CHARS = 6000  # safe size per file-chunk sent to the LLM

def _get_strictness_note(strictness: str) -> str:
    return {
        "strict": "Flag even minor issues and style inconsistencies.",
        "standard": "Focus on bugs, security issues, and significant style problems.",
        "lenient": "Only flag critical bugs and serious security vulnerabilities.",
    }.get(strictness, "Focus on bugs, security issues, and significant style problems.")


def _build_prompt(diff_chunk: str, strictness: str, language: str) -> tuple[str, str]:
    strictness_note = _get_strictness_note(strictness)
    lang_note = f"The codebase is primarily {language}." if language != "any" else "The codebase may use any language."

    system_prompt = """You are MergeMind, an expert code reviewer. You analyze code diffs and return structured JSON feedback.
You are precise, concise, and constructive. You never hallucinate line numbers.
You always respond with valid JSON only — no markdown fences, no preamble, no text outside the JSON object."""

    user_prompt = f"""Review this pull request diff chunk and return a JSON object exactly matching this schema:

{{
  "summary": "<1-2 sentence overview of what this file change does>",
  "bugs": [
    {{"severity": "high|medium|low", "file": "<filename or unknown>", "line": "<line number or N/A>", "description": "<what the bug is>", "suggestion": "<how to fix it>"}}
  ],
  "security": [
    {{"severity": "high|medium|low", "file": "<filename or unknown>", "line": "<line number or N/A>", "description": "<what the vulnerability is>", "suggestion": "<how to fix it>"}}
  ],
  "style": [
    {{"severity": "medium|low", "file": "<filename or unknown>", "line": "<line number or N/A>", "description": "<style or best practice issue>", "suggestion": "<improvement>"}}
  ],
  "positive": ["<one specific thing done well>"],
  "overall_score": "<integer 1-10>"
}}

Rules:
- Return ONLY the JSON object. No markdown, no prose outside JSON.
- If a category has no findings, return an empty list [].
- Maximum 3 items per category for this chunk.
- {lang_note}
- {strictness_note}

DIFF CHUNK TO REVIEW:
{diff_chunk}"""

    return system_prompt, user_prompt


def _call_groq(client: Groq, system_prompt: str, user_prompt: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    raw_text = response.choices[0].message.content.strip()
    raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
    raw_text = re.sub(r"\n?```$", "", raw_text)
    return json.loads(raw_text)


def _merge_reviews(chunk_reviews: list[dict]) -> dict:
    """Combines multiple per-file reviews into one final review."""
    merged = {
        "summary": "",
        "bugs": [],
        "security": [],
        "style": [],
        "positive": [],
        "overall_score": "N/A",
    }

    summaries = []
    scores = []

    for review in chunk_reviews:
        if review.get("summary"):
            summaries.append(review["summary"])
        merged["bugs"].extend(review.get("bugs", []))
        merged["security"].extend(review.get("security", []))
        merged["style"].extend(review.get("style", []))
        merged["positive"].extend(review.get("positive", []))
        try:
            scores.append(int(review.get("overall_score", 5)))
        except (ValueError, TypeError):
            pass

    merged["summary"] = " ".join(summaries[:5])
    merged["overall_score"] = round(sum(scores) / len(scores)) if scores else "N/A"

    merged["bugs"] = merged["bugs"][:6]
    merged["security"] = merged["security"][:6]
    merged["style"] = merged["style"][:6]
    merged["positive"] = merged["positive"][:4]

    return merged


def run_review_pipeline(diff: str, file_chunks: list[dict] = None) -> dict:
    """
    Runs the review pipeline. If file_chunks is provided (from split_diff_by_file),
    reviews each file separately and merges results — better for large PRs.
    Falls back to single-pass review on the full diff if no chunks given.
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    strictness = os.environ.get("STRICTNESS", "standard")
    language = os.environ.get("REVIEW_LANGUAGE", "any")

    try:
        if file_chunks and len(file_chunks) > 1:
            print(f"[MergeMind] Reviewing {len(file_chunks)} file chunks separately...")
            chunk_reviews = []

            for chunk in file_chunks:
                content = chunk["content"]
                if len(content) > MAX_CHUNK_CHARS:
                    content = content[:MAX_CHUNK_CHARS] + "\n[chunk truncated]"

                print(f"[MergeMind]  -> reviewing {chunk['filename']}")
                system_prompt, user_prompt = _build_prompt(content, strictness, language)
                chunk_review = _call_groq(client, system_prompt, user_prompt)
                chunk_reviews.append(chunk_review)

            return _merge_reviews(chunk_reviews)

        else:
            print("[MergeMind] Calling Groq API (single-pass review)...")
            system_prompt, user_prompt = _build_prompt(diff, strictness, language)
            return _call_groq(client, system_prompt, user_prompt)

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