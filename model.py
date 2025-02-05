import os
import re
import cv2
import json
import pytesseract
import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
from docx import Document

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust path as needed
# Function to clean extracted text
def clean_extracted_text(text):
    text = re.sub(r'\s*\|\s*', '', text)  # Removes unwanted separators
    text = re.sub(r'\s+', ' ', text).strip()  # Removes extra spaces
    return text

# Function to extract text from PDF files
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Avoid NoneType issues
    return clean_extracted_text(text)

# Function to extract text from Word documents
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return clean_extracted_text(text)

# Function to extract text from images using OCR
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    return clean_extracted_text(text)

# Function to extract text based on file type
def extract_text(file_path, file_type):
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type in ["docx", "doc"]:
        return extract_text_from_docx(file_path)
    elif file_type in ["png", "jpg", "jpeg"]:
        return extract_text_from_image(file_path)
    else:
        raise ValueError("Unsupported file type")

# Function to check ATS compliance
def check_ats_compliance(text):
    if len(text) < 200:
        return "Resume too short. Consider adding more content."
    if len(text.split()) < 100:
        return "Low word count detected. Expand on your experiences."
    if "table" in text.lower() or "image" in text.lower():
        return "Avoid tables and images as ATS may not parse them correctly."
    return "ATS-friendly format detected."

# Function to extract and highlight keywords
def extract_and_highlight_keywords(text):
    keywords = (
        r'\b('
        r'python|java|c\+\+|c#|javascript|typescript|html|css|sql|mysql|mongodb|django|flask|nodejs|react|angular|'
        r'aws|azure|google cloud|gcp|docker|kubernetes|tensorflow|keras|pytorch|scikit-learn|pandas|numpy|'
        r'machine learning|deep learning|artificial intelligence|data science|big data|'
        r'git|github|gitlab|bitbucket|ci/cd|jenkins|tableau|power bi|dash|data engineering|'
        r'statistics|linear regression|logistic regression|hypothesis testing|decision trees|random forest|xgboost|'
        r'security|cybersecurity|penetration testing|network security|cloud computing|microservices|'
        r'product management|scrum|kanban|jira|design patterns|api|rest|graphql|software development'
        r')\b'
    )
    
    education_keywords = r'\b(b\.tech|bachelor of technology|bca|mca|m\.tech|master of technology)\b'

    matched_keywords = [match.group() for match in re.finditer(keywords, text, re.IGNORECASE)]
    education_match = re.search(education_keywords, text, re.IGNORECASE)

    ats_friendly = check_ats_compliance(text)

    feedback = "Resume looks good" if ats_friendly == "ATS-friendly format detected." else ats_friendly
    
    # Suggested companies (for simplicity, we return a list of some sample companies)
    suggested_companies = ["Company A", "Company B", "Company C"]

    # Return all 5 values
    return "Selected" if matched_keywords and education_match else "Not Selected", matched_keywords, feedback, ats_friendly, suggested_companies
