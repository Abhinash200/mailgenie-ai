import sqlite3

def init_db():
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_email TEXT,
            to_email TEXT,
            subject TEXT,
            body TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_email_to_db(from_email, to_email, subject, body):
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO email_history (from_email, to_email, subject, body) VALUES (?, ?, ?, ?)",
                   (from_email, to_email, subject, body))
    conn.commit()
    conn.close()

def load_email_history(from_email):
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_history WHERE from_email = ?", (from_email,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_email_by_id(email_id):
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM email_history WHERE id = ?", (email_id,))
    conn.commit()
    conn.close()
