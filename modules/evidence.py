import os
import shutil
from pypdf import PdfReader
import streamlit as st

EVIDENCE_DIR = "evidence"

if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)

def save_uploaded_file(uploaded_file):
    try:
        if uploaded_file is None:
            return None
            
        file_path = os.path.join(EVIDENCE_DIR, uploaded_file.name)
        
        # Save securely
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def extract_text(file_path):
    """
    Extracts text from PDF, TXT, or MD files.
    Returns: String (text content) or None
    """
    if not os.path.exists(file_path):
        return None
        
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    try:
        if ext == '.pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext in ['.txt', '.md', '.py', '.json']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        else:
            return f"Unsupported file format: {ext}"
            
        return text
    except Exception as e:
        return f"Error reading file: {e}"

def list_evidence_files():
    """Returns list of filenames in evidence directory"""
    if not os.path.exists(EVIDENCE_DIR):
        return []
    return [f for f in os.listdir(EVIDENCE_DIR) if os.path.isfile(os.path.join(EVIDENCE_DIR, f))]

def delete_evidence(filename):
    path = os.path.join(EVIDENCE_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
