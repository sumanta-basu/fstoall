import streamlit as st
import docx
import pdfplumber
import openai
import os

# Set your Azure OpenAI credentials
openai.api_type = "azure"
openai.api_base = "https://mleu-gpt.openai.azure.com/"
openai.api_version = "2024-05-01-preview"
#API KEY Needed
DEPLOYMENT_NAME = "gpt-4o"  # Replace with your actual deployment name

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return '\n'.join([page.extract_text() for page in pdf.pages if page.extract_text()])

def extract_technical_summary(text):
    keywords = ['interface', 'field', 'logic', 'table', 'mapping', 'structure', 'function', 'module', 'data', 'report', 'transaction', 'RFC', 'BAPI']
    return '\n'.join([line.strip() for line in text.split('\n') if any(k in line.lower() for k in keywords)])

def generate_code_with_azure(summary):
    prompt = f"Generate ABAP code based on the following functional summary:\n\n{summary}"
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    return response['choices'][0]['message']['content']

def generate_utp_with_azure(summary):
    prompt = f"Based on the following technical summary, generate a detailed Unit Test Plan with step-by-step test cases:\n\n{summary}"
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    return response['choices'][0]['message']['content']

def generate_ts_with_azure(summary):
    prompt = f"Based on the following functional summary, generate a detailed Technical Specification document:\n\n{summary}"
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    return response['choices'][0]['message']['content']

def main():
    st.set_page_config(page_title="SAP FS Technical Summary", layout="wide")
    st.title("📄 SAP Functional Specification Technical Summary Extractor and Code Generation")

    uploaded_file = st.file_uploader("Upload a SAP Functional Specification (.docx or .pdf)", type=["docx", "pdf"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".docx"):
            text = extract_text_from_docx(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        else:
            st.error("Unsupported file type.")
            return

        summary = extract_technical_summary(text)

        st.subheader("📌 Extracted Technical Summary")
        if summary.strip():
            st.text_area("Summary", summary, height=300)

            col1, col2, col3 = st.columns(3)
            with col1:
                generate_code_btn = st.button("Generate Code")
            with col2:
                generate_utp_btn = st.button("Generate UTP")
            with col3:
                generate_ts_btn = st.button("Generate TS")

            if generate_code_btn:
                with st.spinner("Generating code using Azure OpenAI..."):
                    try:
                        generated_code = generate_code_with_azure(summary)
                        st.subheader("🧠 Generated Code")
                        st.text_area("Generated Code", generated_code, height=700)
                        st.download_button("Download Code", generated_code, file_name="generated_abap_code.abap")
                    except Exception as e:
                        st.error(f"Error generating code: {e}")

            elif generate_utp_btn:
                with st.spinner("Generating Unit Test Plan..."):
                    try:
                        utp = generate_utp_with_azure(summary)
                        st.subheader("🧪 Unit Test Plan")
                        st.text_area("UTP", utp, height=500)
                    except Exception as e:
                        st.error(f"Error generating UTP: {e}")

            elif generate_ts_btn:
                with st.spinner("Generating Technical Specification..."):
                    try:
                        ts = generate_ts_with_azure(summary)
                        st.subheader("📘 Technical Specification")
                        st.text_area("TS", ts, height=500)
                    except Exception as e:
                        st.error(f"Error generating TS: {e}")
        else:
            st.info("No technical content found based on the keywords.")

if __name__ == "__main__":
    main()
