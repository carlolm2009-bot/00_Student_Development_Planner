import sqlite3

DB_NAME = "ltl.db"

# ======================================================
# CONNECTION
# ======================================================
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn


# ======================================================
# INIT DATABASE
# ======================================================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ---------- CLASSES ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            instansie TEXT,
            graad TEXT,
            groep INTEGER,
            vak TEXT,
            aanlyn TEXT,
            tyd TEXT,
            dag TEXT
        )
    """)

    # ---------- STUDENTS ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (class_id)
                REFERENCES files(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
