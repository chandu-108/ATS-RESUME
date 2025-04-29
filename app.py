import io
import base64
import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import pdf2image
from pdf2image.exceptions import PDFInfoNotInstalledError
import google.generativeai as genai

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input_text, pdf_content, prompt):
    """Generate a response using Gemini AI."""
    # Use the updated Gemini model name
    model = genai.GenerativeModel(
        'models/gemini-1.5-flash',
        system_instruction=prompt
    )  # citeturn0search1

    # Single call with multimodal input: image blob then text prompt
    response = model.generate_content([
        pdf_content[0],
        input_text
    ])  # citeturn0search1

    return response.text


def input_pdf_setup(uploaded_file):
    """Process the uploaded PDF file and return a base64 JPEG part."""
    if uploaded_file is None:
        raise FileNotFoundError("No file uploaded")

    try:
        # Convert the PDF to images (requires poppler)
        images = pdf2image.convert_from_bytes(uploaded_file.read(), poppler_path=os.getenv("POPPLER_PATH"))
    except PDFInfoNotInstalledError:
        st.error("Poppler is not installed or not in PATH. Please install Poppler.")
        return None
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")
        return None

    first_page = images[0]
    buf = io.BytesIO()
    first_page.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    return [{
        "mime_type": "image/jpeg",
        "data": base64.b64encode(img_bytes).decode()
    }]


# Streamlit App Configuration
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input Fields
input_text = st.text_area("Job Description:")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file:
    st.success("PDF Uploaded Successfully")

# Buttons
submit1 = st.button("Tell Me About the Resume")
submit2 = st.button("How Can I Improve My Skills")
submit3 = st.button("Percentage Match")

# Prompts
template_review = '''
You are an experienced Technical HR with Tech Experience in the field of Data Science, Full Stack Web Development, Big Data Engineering, DEVOPS, and Data Analysis.
Your task is to review the provided resume against the job description for these profiles.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
'''

template_match = '''
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of Data Science, Full Stack Web Development, Big Data Engineering, DEVOPS, and Data Analysis, as well as deep ATS functionality.
Your task is to evaluate the resume against the provided job description. Provide the percentage of match if the resume aligns with the job description.
First, the output should display the percentage, followed by missing keywords, and lastly, final thoughts.
'''

# Handlers
if submit1:
    if not uploaded_file:
        st.warning("Please upload the resume.")
    else:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            resp = get_gemini_response(input_text, pdf_content, template_review)
            st.subheader("Evaluation:")
            st.write(resp)

elif submit2 or submit3:
    if not uploaded_file:
        st.warning("Please upload the resume.")
    else:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            prompt = template_match if submit3 else template_review
            resp = get_gemini_response(input_text, pdf_content, prompt)
            st.subheader("Response:")
            st.write(resp)
