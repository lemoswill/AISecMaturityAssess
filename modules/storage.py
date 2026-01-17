import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_FILE = "maturity.db"

def init_db():
    """Initialize the SQLite database and handle schema updates."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create Assessments table with new columns if creating from scratch
    c.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            project_name TEXT,
            total_score REAL,
            maturity_level TEXT,
            scope TEXT DEFAULT 'org',
            project_type TEXT DEFAULT 'none'
        )
    ''')
    
    # Check for existing columns to handle migration for existing DBs
    c.execute("PRAGMA table_info(assessments)")
    columns = [info[1] for info in c.fetchall()]
    
    if 'scope' not in columns:
        print("Migrating DB: Adding 'scope' column")
        try:
            c.execute("ALTER TABLE assessments ADD COLUMN scope TEXT DEFAULT 'org'")
        except Exception as e:
            print(f"Migration error (scope): {e}")

    if 'project_type' not in columns:
        print("Migrating DB: Adding 'project_type' column")
        try:
            c.execute("ALTER TABLE assessments ADD COLUMN project_type TEXT DEFAULT 'none'")
        except Exception as e:
             print(f"Migration error (project_type): {e}")
            
    # Create Responses table
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

def save_assessment(project_name, responses, total_score, maturity_level, scope="org", project_type="none"):
    """Save a full assessment and its responses."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute('''
        INSERT INTO assessments (timestamp, project_name, total_score, maturity_level, scope, project_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        timestamp, 
        project_name, 
        total_score, 
        maturity_level, 
        scope, 
        project_type
    ))
    
    assessment_id = c.lastrowid
    
    for r in responses:
        # Notes might contain relevant metadata, keeping as is
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
    try:
        df = pd.read_sql_query("SELECT * FROM assessments ORDER BY timestamp DESC", conn)
    except Exception as e:
        print(f"Error loading history: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def get_assessment_details(assessment_id):
    """Get detailed responses for a specific assessment."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM responses WHERE assessment_id = ?", conn, params=(assessment_id,))
    conn.close()
    return df

def delete_assessment(assessment_id):
    """Delete an assessment and its associated responses."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM responses WHERE assessment_id = ?", (assessment_id,))
        c.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting assessment: {e}")
        return False
    finally:
        conn.close()

def delete_assessments_by_name(name_substring):
    """Delete all assessments whose project name contains the substring."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM assessments WHERE project_name LIKE ?", (f"%{name_substring}%",))
        ids = [row[0] for row in c.fetchall()]
        for aid in ids:
            delete_assessment(aid)
        return len(ids)
    except Exception as e:
        print(f"Error deleting assessments by name: {e}")
        return 0
    finally:
        conn.close()
