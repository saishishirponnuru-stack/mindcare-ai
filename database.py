import sqlite3

def create_database():
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        mood TEXT,
        entry TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_journal(date,mood,entry):
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO journal(date,mood,entry) VALUES(?,?,?)",
        (date,mood,entry)
    )

    conn.commit()
    conn.close()

def get_entries():
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM journal")

    data = cursor.fetchall()

    conn.close()

    return data