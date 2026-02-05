import streamlit as st
import pandas as pd
from ltl_pathfinder.services.student_service import create_student

with st.expander("➕ Add new student"):
    c1, c2 = st.columns(2)
    first = c1.text_input("First name")
    last = c2.text_input("Last name")
    school = st.text_input("School")
    grade = st.text_input("Grade")

    if st.button("Save Student"):
        if first and last:
            create_student(first, last, school, grade)
            st.success("Saved!")
            st.rerun()  # IMPORTANT: refresh the page to reload JSON data
        else:
            st.error("First and last name are required.")

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="LTL Pathfinder", layout="wide")

# ----------------------------
# CSS (make it look like your mock)
# ----------------------------
st.markdown(
    """
<style>
/* Global */
.main { background-color: #f6f8fb; }
.block-container { padding-top: 18px; }

/* Title */
h1 { font-size: 42px; margin-bottom: 4px; }

/* Button styling */
.stButton>button {
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 600;
    border: 1px solid #d8dee8;
    background: #ffffff;
}import sqlite3

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

.primary-blue .stButton>button {
    background: #3b82f6 !important;
    border: 1px solid #3b82f6 !important;
    color: white !important;
}

.primary-blue .stButton>button:hover {
    background: #2f6fe0 !important;
    border: 1px solid #2f6fe0 !important;
}

/* Panels */
.panel {
    background: white;
    border: 1px solid #e6ebf2;
    border-radius: 14px;
    padding: 16px 16px 8px 16px;
    margin-bottom: 14px;
}

/* Stat cards */
.stat-card {
    background: white;
    border: 1px solid #e6ebf2;
    border-radius: 14px;
    padding: 16px;
    height: 105px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.stat-title { color: #4b5563; font-size: 13px; font-weight: 600; }
.stat-value { color: #111827; font-size: 30px; font-weight: 800; line-height: 1; }
.stat-sub { color: #9ca3af; font-size: 12px; }

/* Section header */
.section-title {
    font-size: 22px;
    font-weight: 800;
    margin: 4px 0 10px 0;
}

/* Table spacing */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# Fake data (replace later with your JSON/DB services)
# ----------------------------
df = pd.DataFrame(
    [
        {
            "ID": 1,
            "Name": "Emma Johnson\nPrefers: Em",
            "School": "Lincoln Elementary",
            "Grade": "Grade 5",
            "Subject": "Computer Science Level 3.1",
            "Class": "Mon 2:00 - Computer Science L3.1",
            "Last updated": "2024-01-15",
        },
        {
            "ID": 2,
            "Name": "Lucas Martinez",
            "School": "Riverside Middle School",
            "Grade": "Grade 7",
            "Subject": "Computer Science Level 1",
            "Class": "Tue 4:00 - Computer Science L1",
            "Last updated": "2024-01-14",
        },
        {
            "ID": 3,
            "Name": "Sophia Chen\nPrefers: Sophie",
            "School": "Lincoln Elementary",
            "Grade": "Grade 4",
            "Subject": "Python Level 1",
            "Class": "Wed 2:00 - Python L1",
            "Last updated": "2024-01-12",
        },
    ]
)

# ----------------------------
# Top bar: Title + buttons
# ----------------------------
top = st.columns([5, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2], gap="small")
with top[0]:
    st.markdown("# LTL Pathfinder")

with top[1]:
    st.button("Categories")
with top[2]:
    st.button("Delete All")
with top[3]:
    st.button("Admin")

# Primary blue buttons (wrap in a div class)
with top[4]:
    st.markdown('<div class="primary-blue">', unsafe_allow_html=True)
    st.button("Add Student")
    st.markdown("</div>", unsafe_allow_html=True)

with top[5]:
    st.markdown('<div class="primary-blue">', unsafe_allow_html=True)
    st.button("AI Guide")
    st.markdown("</div>", unsafe_allow_html=True)

with top[6]:
    st.markdown('<div class="primary-blue">', unsafe_allow_html=True)
    st.button("Export")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Filters panel
# ----------------------------
st.markdown('<div class="panel">', unsafe_allow_html=True)

r1 = st.columns([2, 2, 1], gap="large")
with r1[0]:
    st.caption("Filter by class")
    class_filter = st.selectbox("", ["All classes", "Mon 2:00 - CS L3.1", "Tue 4:00 - CS L1", "Wed 2:00 - Python L1"], label_visibility="collapsed")
with r1[1]:
    st.caption("Filter by subject")
    subject_filter = st.selectbox("", ["All subjects", "Computer Science Level 3.1", "Computer Science Level 1", "Python Level 1"], label_visibility="collapsed")
with r1[2]:
    st.caption(" ")
    st.button("Clear")

r2 = st.columns([2, 2, 2], gap="large")
with r2[0]:
    st.caption("Search students")
    q = st.text_input("", placeholder="Search by name...", label_visibility="collapsed")
with r2[1]:
    st.caption("Filter by grade")
    grade_filter = st.selectbox("", ["All grades", "Grade 4", "Grade 5", "Grade 7"], label_visibility="collapsed")
with r2[2]:
    st.caption("Filter by school")
    school_filter = st.selectbox("", ["All schools", "Lincoln Elementary", "Riverside Middle School"], label_visibility="collapsed")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Stat cards row
# ----------------------------
stats = st.columns(3, gap="large")

with stats[0]:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-title">Total Students</div>
            <div class="stat-value">3</div>
            <div class="stat-sub">Current total</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with stats[1]:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-title">This Month</div>
            <div class="stat-value">0</div>
            <div class="stat-sub">Active students this month</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with stats[2]:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-title">Recent Notes</div>
            <div class="stat-value">0</div>
            <div class="stat-sub">Total notes for this student</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ----------------------------
# Students section header + action buttons
# ----------------------------
hdr = st.columns([4, 1.2, 1.2, 1.2, 1.2], gap="small")
with hdr[0]:
    st.markdown('<div class="section-title">Students</div>', unsafe_allow_html=True)

for i, label in enumerate(["Add Note", "Add Journey", "Survey", "Report"], start=1):
    with hdr[i]:
        st.markdown('<div class="primary-blue">', unsafe_allow_html=True)
        st.button(label)
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Apply filters (basic demo)
# ----------------------------
filtered = df.copy()

if q.strip():
    filtered = filtered[filtered["Name"].str.contains(q, case=False, na=False)]

if class_filter != "All classes":
    filtered = filtered[filtered["Class"] == class_filter]

if subject_filter != "All subjects":
    filtered = filtered[filtered["Subject"] == subject_filter]

if grade_filter != "All grades":
    filtered = filtered[filtered["Grade"] == grade_filter]

if school_filter != "All schools":
    filtered = filtered[filtered["School"] == school_filter]

# ----------------------------
# Students table
# ----------------------------
st.dataframe(filtered, use_container_width=True, hide_index=True)

