import streamlit as st
import google.generativeai as genai
from config.config import GOOGLE_API_KEY
from qa_generator import generate_qa
from extract_text import extract_text
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re

# Configure Google API Key
genai.configure(api_key=GOOGLE_API_KEY)

def format_qa_text(qa_text):
    """
    Formats the Q&A output for plain text display.
    """
    if not qa_text.strip():
        return "⚠️ No Q&A content available."

    formatted_text = ""
    qa_pairs = re.split(r"(Question \d+:)", qa_text)

    for i in range(1, len(qa_pairs), 2):
        question = qa_pairs[i].strip()
        answer = qa_pairs[i + 1].strip()

        # ✅ Just plain text output, no HTML
        formatted_text += f"{question} {answer}\n\n"

    return formatted_text

def save_pdf(qa_text):
    """
    Generates a PDF with properly formatted questions and answers.
    """
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    y_position = 750  # Start position for text
    qa_pairs = re.split(r"(Question \d+:)", qa_text)

    for i in range(1, len(qa_pairs), 2):
        question = qa_pairs[i].strip()
        answer = qa_pairs[i + 1].strip()

        c.setFont("Helvetica", 12)  # Normal font for everything
        c.drawString(30, y_position, f"{question} {answer}")

        y_position -= 30  # Adjust spacing
        if y_position < 100:  # Create a new page if space runs out
            c.showPage()
            y_position = 750

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def run():
    st.title("📚 Q&A Generator")
    st.markdown("Upload a document, select a difficulty level, and generate AI-powered questions and answers.")

    uploaded_file = st.file_uploader("📂 Upload a PDF or PPT", type=["pdf", "pptx"])
    difficulty = st.selectbox("🎯 Select Difficulty Level", ["Easy", "Medium", "Hard"])
    generate_btn = st.button("🚀 Generate Q&A")

    if uploaded_file and difficulty and generate_btn:
        file_path = f"resources/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        extracted_text = extract_text(file_path)

        if extracted_text.strip():  
            qa_text = generate_qa(extracted_text, difficulty)  
            formatted_qa = format_qa_text(qa_text)

            st.text_area("Generated Questions & Answers", value=formatted_qa, height=400)

            pdf_buffer = save_pdf(qa_text)
            st.download_button(label="📥 Download Q&A as PDF", data=pdf_buffer, file_name="generated_qna.pdf", mime="application/pdf")
        else:
            st.error("⚠️ Failed to extract text from the uploaded file.")

if __name__ == "__main__":
    run()
