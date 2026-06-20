import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="MergeMind Dashboard", page_icon="🧠", layout="wide")
st.title("🧠 MergeMind Review Dashboard")
st.caption("Autonomous PR review analytics powered by Groq + Llama 3.3")

LOG_FILE = "reviews.json"

@st.cache_data(ttl=60)
def load_reviews():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

reviews = load_reviews()

if not reviews:
    st.info("No reviews logged yet.")
    st.stop()

df = pd.DataFrame(reviews)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["overall_score"] = pd.to_numeric(df["overall_score"], errors="coerce")
df = df.sort_values("timestamp", ascending=False)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Reviews", len(df))
col2.metric("Avg Response Time", f"{df['elapsed_seconds'].mean():.1f}s")
col3.metric("Avg Score", f"{df['overall_score'].mean():.1f}/10")
col4.metric("High Severity Issues", int(df["high_severity_count"].sum()))

st.divider()
st.subheader("Recent Reviews")
st.dataframe(
    df[["timestamp", "repo", "pr_number", "overall_score", "bug_count", "security_count"]],
    use_container_width=True, hide_index=True
)