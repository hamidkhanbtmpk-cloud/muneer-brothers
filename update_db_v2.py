import sqlite3
import os

db_path = os.path.join('instance', 'muneer_brothers.db')

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS office 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           office_type TEXT NOT NULL, 
                           address TEXT NOT NULL)''')
        conn.commit()
        conn.close()
        print("Mubarak ho! Office table create ho gaya.")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Error: Database file nahi mili.")