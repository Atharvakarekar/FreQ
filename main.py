# streamlit_app.py
import streamlit as st
import os
import json
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from flask_to_streamlit_utils import analyze_questions, get_ans_gpt, save_analysis_results, load_analysis_results

st.set_page_config(page_title="Question Analyzer", layout="wide")
st.title("📄 Academic Question Analyzer & GPT Answer Generator")

# Upload
uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

# Analyze button
if uploaded_files and st.button("Analyze Questions"):
    temp_paths = []
    for file in uploaded_files:
        suffix = ".pdf" if file.type == "application/pdf" else ".docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            temp_paths.append(tmp.name)

    with st.spinner("Processing questions..."):
        results = analyze_questions(temp_paths)
        if results:
            save_analysis_results(results)
            st.success("Analysis complete. Questions grouped and frequencies calculated.")
        else:
            st.error("No valid questions found in uploaded files.")

# Load Results
results = load_analysis_results()
if results:
    st.subheader("📊 Analyzed Questions")
    df = pd.DataFrame(results)
    st.dataframe(df[['question', 'frequency']].sort_values(by='frequency', ascending=False))

    # Bar chart for frequencies
    st.subheader("📈 Question Frequency Chart")
    fig, ax = plt.subplots()
    top_df = df.sort_values(by='frequency', ascending=False).head(10)
    ax.barh(top_df['question'], top_df['frequency'])
    ax.invert_yaxis()
    ax.set_xlabel("Frequency")
    ax.set_title("Top 10 Questions by Frequency")
    st.pyplot(fig)

    if st.button("Generate GPT Answers"):
        with st.spinner("Generating answers using GPT..."):
            questions = [q['question'] for q in results]
            answers = get_ans_gpt(questions)
            st.session_state.answers = answers
            st.success("Answers generated.")

    if "answers" in st.session_state:
        st.subheader("🧠 GPT-Generated Answers")
        for qa in st.session_state.answers:
            st.markdown(f"**Q:** {qa['question']}")
            st.markdown(f"**A:** {qa['answer']}")
            st.markdown("---")

        # Export to CSV
        if st.button("Download Answers as CSV"):
            df = pd.DataFrame(st.session_state.answers)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "answers_report.csv", "text/csv")

        # Export to Excel
        if st.button("Download Answers as Excel"):
            df = pd.DataFrame(st.session_state.answers)
            excel_path = os.path.join(tempfile.gettempdir(), "answers_report.xlsx")
            df.to_excel(excel_path, index=False)
            with open(excel_path, "rb") as f:
                st.download_button("📥 Download Excel", f.read(), "answers_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
