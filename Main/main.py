import streamlit as st
from database import get_connection, init_db

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="LTL Development Planner",
    layout="wide"
)

# ======================================================
# SESSION STATE (ALWAYS FIRST)
# ======================================================
if "role" not in st.session_state:
    st.session_state.role = None          # None | admin | guest

if "view" not in st.session_state:
    st.session_state.view = "classes"     # classes | class

if "selected_class_id" not in st.session_state:
    st.session_state.selected_class_id = None

if "show_filters" not in st.session_state:
    st.session_state.show_filters = False

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

GEEN = "Geen"

if "filters" not in st.session_state:
    st.session_state.filters = {
        "instansie": GEEN,
        "graad": GEEN,
        "groep": GEEN,
        "vak": GEEN,
        "aanlyn": GEEN,
        "tyd": GEEN,
        "dag": GEEN,
    }

# ======================================================
# DATABASE
# ======================================================
init_db()

def q(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    res = cur.fetchall()
    conn.commit()
    conn.close()
    return res

def get_distinct(col):
    return [r[0] for r in q(f"SELECT DISTINCT {col} FROM files WHERE {col} IS NOT NULL")]

def fetch_classes():
    sql = "SELECT * FROM files WHERE 1=1"
    vals = []

    for k, v in st.session_state.filters.items():
        if v != GEEN:
            sql += f" AND {k}=?"
            vals.append(v)

    return q(sql, vals)

# ======================================================
# LOGIN
# ======================================================
def show_login():
    st.title("LTL Development Planner")

    login_type = st.radio("Login as", ["Guest", "Admin"])

    if login_type == "Admin":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "Carlo" and password == "123":
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        if st.button("Continue as Guest"):
            st.session_state.role = "guest"
            st.rerun()

# 🔒 Force login on fresh run
if st.session_state.role is None:
    show_login()
    st.stop()

# ======================================================
# TOP BAR (PROFILE)
# ======================================================
top = st.columns([6,1])
top[0].empty()

with top[1]:
    with st.popover(f"👤 {st.session_state.role.capitalize()}"):
        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()

# ======================================================
# CLASSES PAGE
# ======================================================
if st.session_state.view == "classes":

    header = st.columns([6,1,1])
    header[0].subheader("Classes")

    if header[1].button("🔍"):
        st.session_state.show_filters = not st.session_state.show_filters

    if st.session_state.role == "admin":
        if header[2].button("➕"):
            st.session_state.selected_class_id = None
            st.session_state.edit_mode = True
            st.session_state.view = "class"
            st.rerun()

    # ---------- FILTERS ----------
    if st.session_state.show_filters:
        with st.container(border=True):
            c = st.columns(7)
            c[0].selectbox("Instansie", [GEEN]+get_distinct("instansie"), key="f_inst")
            c[1].selectbox("Graad", [GEEN]+[str(i) for i in range(1,13)], key="f_graad")
            c[2].selectbox("Groep", [GEEN]+list(range(1,11)), key="f_groep")
            c[3].selectbox("Vak", [GEEN]+get_distinct("vak"), key="f_vak")
            c[4].selectbox("Aanlyn", [GEEN]+get_distinct("aanlyn"), key="f_aanlyn")
            c[5].selectbox("Tyd", [GEEN]+[f"{h:02d}:00" for h in range(7,19)], key="f_tyd")
            c[6].selectbox("Dag", [GEEN,"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], key="f_dag")

            if st.button("Apply filters"):
                st.session_state.filters = {
                    "instansie": st.session_state.f_inst,
                    "graad": st.session_state.f_graad,
                    "groep": st.session_state.f_groep,
                    "vak": st.session_state.f_vak,
                    "aanlyn": st.session_state.f_aanlyn,
                    "tyd": st.session_state.f_tyd,
                    "dag": st.session_state.f_dag,
                }
                st.session_state.show_filters = False
                st.rerun()

    # ---------- CLASS LIST ----------
    classes = fetch_classes()

    if not classes:
        st.info("No classes found")
    else:
        for c in classes:
            row = st.columns([8,1])
            if row[0].button(f"📄 {c[1]}", key=f"open_{c[0]}"):
                st.session_state.selected_class_id = c[0]
                st.session_state.edit_mode = False
                st.session_state.view = "class"
                st.rerun()

            if st.session_state.role == "admin":
                if row[1].button("🗑", key=f"del_{c[0]}"):
                    q("DELETE FROM files WHERE id=?", (c[0],))
                    st.rerun()

# ======================================================
# CLASS PAGE
# ======================================================
if st.session_state.view == "class":

    cid = st.session_state.selected_class_id
    is_new = cid is None
    editable = st.session_state.role == "admin" and st.session_state.edit_mode

    header = st.columns([6,1,1])
    header[0].subheader("New Class" if is_new else "Class Details")

    if st.session_state.role == "admin":
        if header[1].button("✏️"):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()

    if header[2].button("❌"):
        st.session_state.edit_mode = False
        st.session_state.view = "classes"
        st.rerun()

    data = [None]*9 if is_new else q("SELECT * FROM files WHERE id=?", (cid,))[0]

    name = st.text_input("Name", data[1], disabled=not editable)
    instansie = st.text_input("Instansie", data[2], disabled=not editable)
    graad = st.text_input("Graad", data[3] or "1", disabled=not editable)
    groep = st.number_input("Groep", 1, 99, value=data[4] or 1, disabled=not editable)
    vak = st.text_input("Vak", data[5], disabled=not editable)
    aanlyn = st.selectbox("Aanlyn", ["Aanlyn","In Persoon"], disabled=not editable)
    tyd = st.selectbox("Tyd", [f"{h:02d}:00" for h in range(7,19)], disabled=not editable)
    dag = st.selectbox("Dag", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], disabled=not editable)

    if editable:
        if st.button("💾 Save"):
            if is_new:
                q(
                    "INSERT INTO files (name,instansie,graad,groep,vak,aanlyn,tyd,dag) VALUES (?,?,?,?,?,?,?,?)",
                    (name,instansie,graad,groep,vak,aanlyn,tyd,dag)
                )
            else:
                q(
                    "UPDATE files SET name=?,instansie=?,graad=?,groep=?,vak=?,aanlyn=?,tyd=?,dag=? WHERE id=?",
                    (name,instansie,graad,groep,vak,aanlyn,tyd,dag,cid)
                )
            st.session_state.edit_mode = False
            st.session_state.view = "classes"
            st.rerun()

if "filters" not in st.session_state:
    st.session_state.filters = {
        "instansie": GEEN,
        "graad": GEEN,
        "groep": GEEN,
        "vak": GEEN,
        "aanlyn": GEEN,
        "tyd": GEEN,
        "dag": GEEN,
    }

init_db()

# ======================================================
# DB HELPERS
# ======================================================
def q(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    res = cur.fetchall()
    conn.commit()
    conn.close()
    return res

def fetch_classes():
    sql = "SELECT * FROM files WHERE 1=1"
    vals = []
    for k, v in st.session_state.filters.items():
        if v != GEEN:
            sql += f" AND {k}=?"
            vals.append(v)
    return q(sql, vals)

# ======================================================
# LOGIN (FORCED ON START)
# ======================================================
if st.session_state.role is None:
    st.title("LTL Development Planner")
    role = st.radio("Login as", ["Guest", "Admin"])

    if role == "Admin":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == "Carlo" and p == "123":
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        if st.button("Continue as Guest"):
            st.session_state.role = "guest"
            st.rerun()

    st.stop()

# ======================================================
# PROFILE BUTTON
# ======================================================
with st.columns([6,1])[1]:
    with st.popover(f"👤 {st.session_state.role.capitalize()}"):
        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()

# ======================================================
# CLASS PAGE
# ======================================================
if st.session_state.view == "class":

    cid = st.session_state.selected_class_id
    is_new = cid is None
    is_admin = st.session_state.role == "admin"

    data = [None]*9 if is_new else q("SELECT * FROM files WHERE id=?", (cid,))[0]

    # ---------- TOP BAR ----------
    top = st.columns([6,1,1])
    top[0].subheader("New Class" if is_new else "Class: " + (data[1] or ""))
    
    # Exit class button
    if top[2].button("❌ Exit Class"):
        st.session_state.view = "classes"
        st.session_state.selected_class_id = None
        st.session_state.edit_mode = False
        st.rerun()

    # Edit toggle button for admin (only for existing classes)
    if is_admin and not is_new:
        if top[1].button("✏️ Edit Class"):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()

    # ---------- CLASS DETAILS (EDIT MODE ONLY) ----------
    if is_admin and st.session_state.edit_mode:
        st.subheader("Class Details")
        name = st.text_input("Name", data[1])
        inst = st.text_input("Instansie", data[2])
        graad = st.text_input("Graad", data[3])
        groep = st.number_input("Groep", 1, 99, value=data[4] or 1)
        vak = st.text_input("Vak", data[5])
        aan = st.selectbox("Aanlyn", ["Aanlyn", "In Persoon"], index=0 if data[6]=="Aanlyn" else 1)
        tyd = st.text_input("Tyd", data[7])
        dag = st.text_input("Dag", data[8])

        if st.button("💾 Save"):
            if is_new:
                q(
                    "INSERT INTO files (name,instansie,graad,groep,vak,aanlyn,tyd,dag) VALUES (?,?,?,?,?,?,?,?)",
                    (name,inst,graad,groep,vak,aan,tyd,dag)
                )
            else:
                q(
                    "UPDATE files SET name=?,instansie=?,graad=?,groep=?,vak=?,aanlyn=?,tyd=?,dag=? WHERE id=?",
                    (name,inst,graad,groep,vak,aan,tyd,dag,cid)
                )
            st.session_state.edit_mode = False
            st.rerun()

    # ---------- STUDENTS ----------
    st.subheader("Students")

    # Add Student button (always at top-right in edit mode)
    if is_admin and st.session_state.edit_mode:
        add_col = st.columns([6,1])
        if add_col[1].button("➕ Add Student"):
            st.session_state.add_student_active = True

    # Student form
    if is_admin and st.session_state.edit_mode and st.session_state.get("add_student_active", False):
        with st.form("add_student_form", clear_on_submit=True):
            n = st.text_input("Student Name", key="new_student_name")
            submitted = st.form_submit_button("Add")
            if submitted and n:
                q("INSERT INTO students (class_id,name) VALUES (?,?)", (cid,n))
                st.session_state.add_student_active = False
                st.rerun()

    # List students
    students = q("SELECT id,name FROM students WHERE class_id=?", (cid,))
    for s in students:
        row = st.columns([8,1])
        row[0].write(s[1])
        if is_admin and st.session_state.edit_mode:
            if row[1].button("🗑", key=f"sdel_{s[0]}"):
                st.session_state.confirm_delete = ("student", s[0])

# ---------- DELETE CONFIRMATION ----------
if st.session_state.confirm_delete:
    t, cid = st.session_state.confirm_delete
    st.warning(f"Are you sure you want to delete this {t}?")
    c1, c2 = st.columns(2)
    if c1.button("Yes, delete", key="confirm_yes"):
        if t == "class":
            q("DELETE FROM files WHERE id=?", (cid,))
        else:
            q("DELETE FROM students WHERE id=?", (cid,))
        st.session_state.confirm_delete = None
        st.rerun()
    if c2.button("Cancel", key="confirm_no"):
        st.session_state.confirm_delete = None
        st.rerun()
