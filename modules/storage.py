import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_FILE = "maturity.db"

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create Assessments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            project_name TEXT,
            total_score REAL,
            maturity_level TEXT
        )
    ''')
    
    # Create Responses table
    # category = NIST Function (GOVERN, MAP...)
    # question_id = CSA Control ID (AIS-01...)
    # notes = subcategory mapping
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER,
            category TEXT,
            question_id TEXT,
            score INTEGER,
            notes TEXT,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_assessment(project_name, responses, total_score, maturity_level):
    """Save a full assessment and its responses."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute('''
        INSERT INTO assessments (timestamp, project_name, total_score, maturity_level)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, project_name, total_score, maturity_level))
    
    assessment_id = c.lastrowid
    
    for r in responses:
        c.execute('''
            INSERT INTO responses (assessment_id, category, question_id, score, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (assessment_id, r['category'], r['question_id'], r['score'], r.get('notes', '')))
        
    conn.commit()
    conn.close()
    return assessment_id

def load_history():
    """Load all past assessments."""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
        
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_assessment_details(assessment_id):
    """Get detailed responses for a specific assessment."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM responses WHERE assessment_id = ?", conn, params=(assessment_id,))
    conn.close()
    return df
