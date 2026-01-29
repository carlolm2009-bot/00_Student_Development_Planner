import streamlit as st
import sqlite3

# ------------------ DATABASE ------------------

conn = sqlite3.connect("planner.db", check_same_thread=False)
cur = conn.cursor()

def q(sql, params=()):
    cur.execute(sql, params)
    conn.commit()
    return cur

def init_db():
    q("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade TEXT,
        subject TEXT
    )
    """)
    q("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY(class_id) REFERENCES classes(id) ON DELETE CASCADE
    )
    """)

init_db()

# ------------------ SESSION STATE ------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if "selected_class" not in st.session_state:
    st.session_state.selected_class = None

if "show_filters" not in st.session_state:
    st.session_state.show_filters = False

if "editing" not in st.session_state:
    st.session_state.editing = False

# ------------------ LOGIN ------------------

if not st.session_state.logged_in:
    st.title("Student Development Planner")

    choice = st.radio("Sign in as:", ["Guest", "Admin"])

    if choice == "Admin":
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == "123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("Wrong password")
    else:
        if st.button("Continue as Guest"):
            st.session_state.logged_in = True
            st.session_state.role = "guest"
            st.rerun()

    st.stop()

# ------------------ HEADER ------------------

h1, h2, h3 = st.columns([6, 1, 1])

h1.title("📊 Dashboard")

if h2.button("🔍", key="filter_toggle"):
    st.session_state.show_filters = not st.session_state.show_filters

if st.session_state.role == "admin":
    if h3.button("➕", key="add_class_btn"):
        q("INSERT INTO classes (name) VALUES ('New Class')")
        st.rerun()

profile = st.sidebar.button(f"👤 {st.session_state.role.capitalize()}")
if profile:
    if st.sidebar.button("Log out"):
        st.session_state.clear()
        st.rerun()

# ------------------ FILTERS ------------------

filters = {}
if st.session_state.show_filters:
    st.subheader("Filters")
    filters["grade"] = st.text_input("Grade")
    filters["subject"] = st.text_input("Subject")

    if st.button("Commit Filters"):
        st.session_state.filters = filters
        st.session_state.show_filters = False
        st.rerun()

# ------------------ CLASSES VIEW ------------------

if st.session_state.selected_class is None:
    st.subheader("Classes")

    rows = q("SELECT * FROM classes").fetchall()

    for c in rows:
        cols = st.columns([5, 1])
        if cols[0].button(f"{c[1]}  | Grade: {c[2]} | Subject: {c[3]}", key=f"class_{c[0]}"):
            st.session_state.selected_class = c[0]
            st.session_state.editing = False
            st.rerun()

        if st.session_state.role == "admin":
            if cols[1].button("🗑️", key=f"del_class_{c[0]}"):
                if st.confirm("Delete this class?"):
                    q("DELETE FROM classes WHERE id=?", (c[0],))
                    st.rerun()

    st.stop()

# ------------------ CLASS VIEW ------------------

class_id = st.session_state.selected_class
cls = q("SELECT * FROM classes WHERE id=?", (class_id,)).fetchone()

top = st.columns([6, 1, 1])

top[0].subheader(cls[1])

if top[1].button("⬅ Exit"):
    st.session_state.selected_class = None
    st.session_state.editing = False
    st.rerun()

if st.session_state.role == "admin":
    if top[2].button("✏️ Edit"):
        st.session_state.editing = not st.session_state.editing
        st.rerun()

# ------------------ EDIT PANEL (ADMIN ONLY) ------------------

if st.session_state.editing and st.session_state.role == "admin":
    st.markdown("### Edit Class")

    name = st.text_input("Name", cls[1])
    grade = st.text_input("Grade", cls[2] or "")
    subject = st.text_input("Subject", cls[3] or "")

    if st.button("Save Changes"):
        q("UPDATE classes SET name=?, grade=?, subject=? WHERE id=?",
          (name, grade, subject, class_id))
        st.session_state.editing = False
        st.rerun()

# ------------------ STUDENTS ------------------

st.markdown("### Students")

s_head = st.columns([6, 1])

students = q("SELECT * FROM students WHERE class_id=?", (class_id,)).fetchall()

for s in students:
    row = st.columns([5, 1])
    row[0].write(s[2])

    if st.session_state.role == "admin":
        if row[1].button("🗑️", key=f"del_student_{s[0]}"):
            if st.confirm("Remove this student?"):
                q("DELETE FROM students WHERE id=?", (s[0],))
                st.rerun()

# ADD STUDENT (+ BUTTON)
if st.session_state.role == "admin":
    if s_head[1].button("➕", key=f"add_student_{class_id}"):
        q("INSERT INTO students (class_id, name) VALUES (?, ?)", (class_id, "New Student"))
        st.rerun()
