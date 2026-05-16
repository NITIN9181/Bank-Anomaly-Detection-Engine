import sqlite3
import os

def migrate():
    """Add Explainability 2.0 columns to the anomalies table."""
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../anomalies.db'))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    columns_to_add = [
        "explanation_confidence FLOAT DEFAULT 0.0",
        "feature_contributions TEXT",
        "recommended_actions TEXT",
        "analyst_feedback TEXT",
        "feedback_score INTEGER DEFAULT 0",
        "action_taken TEXT",
        "explanation_generated_at TIMESTAMP"
    ]
    
    for col in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE anomalies ADD COLUMN {col}")
            print(f"Added column: {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column already exists: {col}")
            else:
                print(f"Error adding {col}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
