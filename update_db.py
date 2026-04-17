import sqlite3
import os

db_path = os.path.join('instance', 'muneer_brothers.db')

if not os.path.exists(db_path):
    print(f"Error: Database file '{db_path}' nahi mili.")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE employee ADD COLUMN serial_no INTEGER DEFAULT 0")
        conn.commit()
        conn.close()
        print("Database updated.")
    except sqlite3.OperationalError:
        print("Column 'serial_no' pehle se maujood hai.")
    except Exception as e:
        print(f"Error: {e}")