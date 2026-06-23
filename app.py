"""
app.py — MergeMind Review Dashboard
Reads reviews.json committed by GitHub Actions after each PR review.
Schema matches logger.py exactly.
"""

import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

LOG_FILE = "reviews.json"

SEVERITY_COLORS = {
    "high":   "#E53935",
    "medium": "#FB8C00",
    "low":    "#43A047",
}

st.set_page_config(
    page_title="MergeMind Dashboard",
    page_icon="🧠",
    layout="wide",
)


@st.cache_data(ttl=60)
def load_reviews() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def build_dataframe(reviews: list) -> pd.DataFrame:
    rows = []
    for r in reviews:
        total = (
            r.get("bug_count", 0)
            + r.get("security_count", 0)
            + r.get("style_count", 0)
        )
        rows.append({
            "PR #":           r.get("pr_number", "—"),
            "Repo":           r.get("repo", "—"),
            "SHA":            r.get("sha", "—"),
            "Timestamp":      r.get("timestamp", "—"),
            "Runtime (s)":    round(r.get("elapsed_seconds", 0), 2),
            "Score":          r.get("overall_score", "—"),
            "Bugs":           r.get("bug_count", 0),
            "Security":       r.get("security_count", 0),
            "Style":          r.get("style_count", 0),
            "High Severity":  r.get("high_severity_count", 0),
            "Total Issues":   total,
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)
        df = df.sort_values("Timestamp", ascending=False)
    return df


# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🧠 MergeMind Review Dashboard")
st.caption("Autonomous PR review analytics powered by Groq + Llama 3.3 70B")
st.divider()

reviews = load_reviews()

if not reviews:
    st.info(
        "No reviews logged yet. Open a Pull Request in a repo where MergeMind "
        "is installed — the first review will appear here automatically."
    )
    st.stop()

df = build_dataframe(reviews)

# ── METRICS ───────────────────────────────────────────────────────────────────
total_reviews = len(df)
total_issues  = int(df["Total Issues"].sum())
total_high    = int(df["High Severity"].sum())
avg_runtime   = round(df["Runtime (s)"].mean(), 2)
avg_score     = round(
    df["Score"].apply(lambda x: x if isinstance(x, (int, float)) else None)
    .dropna().mean(), 1
) if not df.empty else "—"
unique_repos  = df["Repo"].nunique()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Reviews",      total_reviews)
c2.metric("Total Issues Found", total_issues)
c3.metric("High Severity",      total_high)
c4.metric("Avg Runtime",        f"{avg_runtime}s")
c5.metric("Avg Review Score",   avg_score)
c6.metric("Repos Covered",      unique_repos)

st.divider()

# ── CHARTS ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

# Donut — issue type breakdown
with col_left:
    st.subheader("📊 Issue Type Breakdown")
    bugs     = int(df["Bugs"].sum())
    security = int(df["Security"].sum())
    style    = int(df["Style"].sum())

    if bugs + security + style == 0:
        st.info("No issues detected across all reviews.")
    else:
        fig, ax = plt.subplots(figsize=(4, 4))
        fig.patch.set_facecolor("#0E1117")
        ax.set_facecolor("#0E1117")
        sizes  = [bugs, security, style]
        labels = ["Bugs", "Security", "Style"]
        colors = ["#E53935", "#FB8C00", "#43A047"]
        ax.pie(
            sizes, labels=labels, colors=colors,
            autopct="%1.0f%%", startangle=90,
            wedgeprops=dict(width=0.5),
            textprops=dict(color="white"),
        )
        ax.set_title("Bug / Security / Style", color="white", pad=12)
        plt.tight_layout()
        st.pyplot(fig)

# Line — reviews over time
with col_right:
    st.subheader("📈 Reviews Over Time")
    valid_ts = df.dropna(subset=["Timestamp"])
    if not valid_ts.empty:
        timeline = (
            valid_ts.set_index("Timestamp")
            .resample("D")["PR #"]
            .count()
            .reset_index()
        )
        timeline.columns = ["Date", "Reviews"]
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor("#0E1117")
        ax2.set_facecolor("#0E1117")
        ax2.plot(timeline["Date"], timeline["Reviews"],
                 color="#4FC3F7", linewidth=2, marker="o", markersize=5)
        ax2.fill_between(timeline["Date"], timeline["Reviews"],
                         alpha=0.15, color="#4FC3F7")
        ax2.set_title("PR Reviews per Day", color="white", pad=10)
        ax2.tick_params(colors="white")
        ax2.set_ylabel("Reviews", color="white")
        for spine in ax2.spines.values():
            spine.set_edgecolor("#333")
        ax2.grid(alpha=0.15, color="white")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.info("Not enough data to plot timeline yet.")

st.divider()

# Bar — runtime per review
st.subheader("⚡ Response Time per Review")
show = df.head(15).copy()
labels   = [f"PR #{row['PR #']}" for _, row in show.iterrows()]
runtimes = show["Runtime (s)"].tolist()

fig3, ax3 = plt.subplots(figsize=(10, 3))
fig3.patch.set_facecolor("#0E1117")
ax3.set_facecolor("#0E1117")
ax3.bar(labels, runtimes, color="#FF7043", alpha=0.85)
ax3.axhline(y=avg_runtime, color="#FFF176", linestyle="--",
            linewidth=1.2, label=f"Avg {avg_runtime}s")
ax3.set_ylabel("Seconds", color="white")
ax3.tick_params(colors="white")
for spine in ax3.spines.values():
    spine.set_edgecolor("#333")
ax3.grid(alpha=0.1, axis="y", color="white")
ax3.legend(facecolor="#0E1117", labelcolor="white")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
st.pyplot(fig3)

st.divider()

# ── FULL LOG TABLE ─────────────────────────────────────────────────────────────
st.subheader("📋 Full Review Log")

display_cols = [
    "PR #", "Repo", "SHA", "Timestamp",
    "Runtime (s)", "Score", "Bugs", "Security", "Style",
    "High Severity", "Total Issues",
]
available = [c for c in display_cols if c in df.columns]

st.dataframe(
    df[available].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

# ── PER-REVIEW SUMMARY EXPANDER ───────────────────────────────────────────────
st.divider()
st.subheader("🔍 Review Summaries")

for review in reviews:
    pr_num   = review.get("pr_number", "?")
    repo     = review.get("repo", "unknown")
    ts       = review.get("timestamp", "")[:10]
    score    = review.get("overall_score", "—")
    summary  = review.get("summary", "No summary available.")
    bugs     = review.get("bug_count", 0)
    security = review.get("security_count", 0)
    style    = review.get("style_count", 0)
    high     = review.get("high_severity_count", 0)
    elapsed  = round(review.get("elapsed_seconds", 0), 2)

    with st.expander(
        f"PR #{pr_num} — {repo} — Score: {score} — {ts}"
    ):
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        col_a.metric("Score",    score)
        col_b.metric("Bugs",     bugs)
        col_c.metric("Security", security)
        col_d.metric("Style",    style)
        col_e.metric("Runtime",  f"{elapsed}s")

        st.markdown("**Summary:**")
        st.write(summary)

        if high > 0:
            st.error(f"⚠️ {high} high-severity issue(s) detected — review before merging.")
        else:
            st.success("✅ No high-severity issues detected.")

st.divider()
st.caption(
    "MergeMind | Powered by Groq + Llama 3.3 70B | "
    "github.com/Ashu07017/mergemind"
)