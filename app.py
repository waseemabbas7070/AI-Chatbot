import streamlit as st
import PyPDF2
from model import generate_podcast

st.set_page_config(page_title="AI Podcast Generator", layout="centered")
st.title("AI Podcast Generator")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        with open("processed_output.txt", "w", encoding="utf-8") as f:
            f.write(text)

        st.success("PDF uploaded and text extracted successfully!")

        if st.button("Generate Podcast Episode"):
            output_file = generate_podcast()
            st.success("Podcast episode generated successfully!")
            st.audio(output_file)

    except Exception as e:
        st.error(f" Error reading PDF: {e}")