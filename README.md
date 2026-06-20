# 🧠 MergeMind

**Autonomous PR review agent** — detects bugs, security issues, and style problems in every pull request, automatically, in under 60 seconds.

[![MergeMind Review](https://github.com/Ashu07017/mergemind/actions/workflows/pr-review.yml/badge.svg)](https://github.com/Ashu07017/mergemind/actions/workflows/pr-review.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%2F%20Llama%203.3-orange)](https://groq.com/)
[![Streamlit](https://img.shields.io/badge/dashboard-streamlit-ff4b4b)](https://mergemind-j4kcecbmas2psfzojpcr4j.streamlit.app/)

🔗 **[Live Dashboard](https://mergemind-j4kcecbmas2psfzojpcr4j.streamlit.app/)** · 📦 **[Example PR Review](https://github.com/Ashu07017/mergemind/pull/2)**

---

## What it does

The moment a pull request is opened on a repo with MergeMind installed, it wakes up automatically:

1. **Fetches** the code diff via the GitHub REST API
2. **Splits** large multi-file diffs into per-file chunks (so nothing gets truncated or missed)
3. **Reviews** each chunk using an LLM (Groq + Llama 3.3 70B) for bugs, security vulnerabilities, and style issues
4. **Posts** a structured, severity-tagged markdown comment directly on the PR
5. **Logs** every review for analytics on a live dashboard

No human has to trigger it. No behavior change required from the team — just drop in one workflow file.

![MergeMind review comment posted automatically on a GitHub PR](docs/mergemind-dashboard.png)
*MergeMind reviewing [Streamlit-Dashboard](https://github.com/Ashu07017/mergemind/pull/3) — Correctly recognizes and credits safe parameterized queries while still identifying medium- and low-severity issues.*

![MergeMind catching hardcoded secrets and eval() usage](docs/review-data-handler.png)
*MergeMind reviewing [PR #4](https://github.com/Ashu07017/mergemind/pull/4) — flags a hardcoded API key and unsafe `eval()` call*

![MergeMind reviewing JavaScript for SQL injection and XSS](docs/review-frontend.png)
*MergeMind reviewing [PR #5](https://github.com/Ashu07017/mergemind/pull/5) — works across languages, here catching SQL injection and XSS patterns in JavaScript*

---

## Architecture

```
PR opened/updated
       │
       ▼
GitHub Actions (pr-review.yml)
       │
       ▼
diff_fetcher.py ──► fetches raw diff via GitHub REST API
       │
       ▼
split into per-file chunks (handles large PRs without truncation)
       │
       ▼
review_pipeline.py ──► Groq API (Llama 3.3 70B) ──► structured JSON
       │
       ▼
comment_poster.py ──► formats markdown ──► posts to PR
       │
       ▼
logger.py ──► reviews.json
       │
       ▼
app.py ──► Streamlit dashboard (metrics, history, severity charts)
```

![Architecture diagram of MergeMind's pipeline](diagram-placeholder.png)
*Add a screenshot of the architecture diagram here*

---

## Install in your repo (2 minutes)

Anyone — a solo developer, a team lead, a manager rolling this out for their team — can add MergeMind to any GitHub repo with no server, no installation, and no dependency on this repo staying online.

1. **Copy one file** — grab [`.github/workflows/pr-review.yml`](.github/workflows/pr-review.yml) from this repo and add it to the same path (`.github/workflows/pr-review.yml`) in your own repo
2. **Get a free Groq API key** — sign up at [console.groq.com](https://console.groq.com) → API Keys → Create API Key (no credit card required)
3. **Add the key as a GitHub secret** — in your repo go to **Settings → Secrets and variables → Actions → New repository secret** → name it `GROQ_API_KEY` → paste the key → Add secret
4. **Open any pull request** — MergeMind reviews it automatically within ~60 seconds, no manual trigger needed

That's it. Every PR opened from then on — by any contributor on the repo — gets reviewed automatically.

### Optional configuration

Set these as repo **Variables** (Settings → Secrets and variables → Actions → Variables tab), not secrets — they're not sensitive:

| Variable | Options | Default |
|---|---|---|
| `STRICTNESS` | `strict`, `standard`, `lenient` | `standard` |
| `REVIEW_LANGUAGE` | any language name, or `any` | `any` |

- **`strict`** flags even minor style inconsistencies — good for teams enforcing strict code quality
- **`lenient`** only flags critical bugs and serious security issues — good for fast-moving prototyping repos

---

## Tech stack

Python 3.11 · GitHub Actions · Groq API (Llama 3.3 70B) · GitHub REST API · Streamlit Cloud

---

## Project structure

```
mergemind/
├── .github/workflows/pr-review.yml   # Triggers on PR events
├── src/
│   ├── diff_fetcher.py               # Fetches + chunks PR diffs
│   ├── review_pipeline.py            # LLM review pipeline (Groq)
│   ├── comment_poster.py             # Formats + posts PR comments
│   └── logger.py                     # Logs review metrics
├── app.py                            # Streamlit dashboard
├── main.py                           # Entry point
└── requirements.txt
```

---

## Local development

```bash
git clone https://github.com/Ashu07017/mergemind
cd mergemind
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # fill in GROQ_API_KEY, GITHUB_TOKEN, etc.
python main.py
```

---

## Roadmap

- [ ] Persist `reviews.json` across Actions runs for live dashboard data
- [ ] Inline line-level PR comments (GitHub Reviews API)
- [ ] Slack notification on high-severity findings
- [ ] Parallelized chunk reviews for faster multi-file PRs

---

## Author

**Ashok Chaturvedi** — [GitHub](https://github.com/Ashu07017) · [LinkedIn](https://www.linkedin.com/in/ashok-chaturvedi-6745a6288)