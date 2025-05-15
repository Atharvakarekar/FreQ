# streamlit_app.py
import streamlit as st
import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from flask_to_streamlit_utils import analyze_questions

st.set_page_config(page_title="Question Analyzer", layout="wide")
st.title("📄 Academic Question Analyzer & File Exporter")

# Session reset on reload
if 'results' not in st.session_state:
    st.session_state.results = None

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
            st.session_state.results = results
            st.success("Analysis complete. Questions grouped and frequencies calculated.")
        else:
            st.error("No valid questions found in uploaded files.")

# Load Results from session only
results = st.session_state.get('results')
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

    # Export options
    if st.button("Download Questions as CSV"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV", csv, "questions.csv", "text/csv")

    if st.button("Download Questions as Excel"):
        excel_path = os.path.join(tempfile.gettempdir(), "questions.xlsx")
        df.to_excel(excel_path, index=False)
        with open(excel_path, "rb") as f:
            st.download_button("📥 Excel", f.read(), "questions.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("Download Questions as TXT"):
        txt = '\n'.join(df['question'])
        st.download_button("📥 TXT", txt, "questions.txt")

    if st.button("Download Questions as JSON"):
        json_str = df.to_json(orient='records', indent=2)
        st.download_button("📥 JSON", json_str, "questions.json", "application/json")

    if st.button("Download Questions as PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Question Analysis Report", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        for idx, row in df.iterrows():
            pdf.multi_cell(0, 10, f"{idx + 1}. {row['question']}\nFrequency: {row['frequency']}\n")
            pdf.ln(2)
        pdf_path = os.path.join(tempfile.gettempdir(), "questions.pdf")
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 PDF", f.read(), "questions.pdf", "application/pdf")
