# Phase 4 — Streamlit UI
# Entry point for the sales rep copilot web app

import os
import streamlit as st
from dotenv import load_dotenv
from rag_pipeline import ask

load_dotenv()

st.set_page_config(page_title="Sales Rep Copilot", page_icon="💼", layout="centered")
st.title("💼 Sales Rep Copilot")
st.caption("Ask a question about your B2B customers. Answers are grounded in real transaction data.")

with st.sidebar:
    st.header("Settings")
    top_n = st.slider("Profiles to retrieve", min_value=3, max_value=20, value=10)
    show_profiles = st.toggle("Show retrieved profiles", value=False)

question = st.text_area(
    "Your question",
    placeholder="e.g. Summarize customer PIERRE FABRE | Which customers haven't ordered recently?",
    height=100,
)

if st.button("Ask", type="primary", disabled=not question.strip()):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY not set. Add it to your .env file.")
    else:
        with st.spinner("Retrieving profiles and generating answer..."):
            result = ask(question.strip(), top_n=top_n, api_key=api_key)

        st.subheader("Answer")
        st.markdown(result["answer"])

        if show_profiles:
            st.subheader(f"Retrieved Profiles ({len(result['profiles'])})")
            for i, p in enumerate(result["profiles"]):
                with st.expander(f"Profile {i + 1} — {p['metadata'].get('cus_name', '')}"):
                    st.text(p["text"])
                    st.caption(f"Similarity distance: {p['distance']:.4f}")
