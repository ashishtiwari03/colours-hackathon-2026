import streamlit as st
from utils.mistral_client import ask

st.set_page_config(page_title="Hackathon App", layout="wide")

st.title("COLOURS Hackathon App")

tab1, tab2 = st.tabs(["Problem", "AI Demo"])

with tab1:
    st.write("Problem will be defined on hackathon day.")

with tab2:
    st.subheader("Solution Generator")

    problem = st.text_area("Describe the problem")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Generate Idea"):
            prompt = f"""
            Based on this problem: {problem}
            Suggest a simple, practical workplace solution.
            Keep it realistic and implementable.
            """
            st.write(ask(prompt, fallback="Idea unavailable"))

    with col2:
        if st.button("Generate Pitch"):
            prompt = f"""
            Create a 1-minute startup pitch for this solution:
            {problem}
            Include problem, solution, and impact.
            """
            st.write(ask(prompt, fallback="Pitch unavailable"))

    with col3:
        if st.button("Business Case"):
            prompt = f"""
            Explain the business value and ROI for solving this:
            {problem}
            Include numbers and cost-saving logic.
            """
            st.write(ask(prompt, fallback="Business unavailable"))

    col1, col2, col3, col4 = st.columns(4)

with col4:
    if st.button("Full Solution"):
        if not problem:
            st.warning("Please enter a problem first")
        else:
            prompt = f"""
            Problem: {problem}

            Create a solution that:
            - Detects burnout early using work patterns
            - Is privacy-safe (no personal data)
            - Is easy for companies to implement

            Provide:
            1. Solution name
            2. How it works (3 steps)
            3. Business value
            4. Why it's better than existing tools
            """

            st.success("Full Solution:")
            st.write(ask(prompt, fallback="Solution unavailable"))