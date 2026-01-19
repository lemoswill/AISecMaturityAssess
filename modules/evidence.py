import os
import shutil
from pypdf import PdfReader
import streamlit as st

EVIDENCE_DIR = "evidence"

if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)

import json
import datetime

def save_uploaded_file(uploaded_file, framework_tag="NIST"):
    try:
        if uploaded_file is None:
            return None
            
        file_path = os.path.join(EVIDENCE_DIR, uploaded_file.name)
        
        # Save securely
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Save Metadata sidecar
        save_metadata(uploaded_file.name, os.path.splitext(uploaded_file.name)[1].upper().replace(".", ""), framework_tag)
            
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def save_metadata(filename, doc_type, framework_tag="NIST"):
    metadata_path = os.path.join(EVIDENCE_DIR, f"{filename}.json")
    metadata = {
        "filename": filename,
        "type": doc_type,
        "upload_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "framework": framework_tag,
        "uploaded_by": "Security Audit Bot"
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

def get_metadata(filename):
    metadata_path = os.path.join(EVIDENCE_DIR, f"{filename}.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "filename": filename,
        "type": os.path.splitext(filename)[1].upper().replace(".", ""),
        "upload_date": "Historical",
        "framework": "NIST",
        "uploaded_by": "System"
    }

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
