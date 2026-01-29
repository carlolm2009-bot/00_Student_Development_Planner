import streamlit as st
from database import get_connection, init_db

st.set_page_config("LTL Development Planner", layout="wide")

# ======================================================
# SESSION STATE
# ======================================================
if "role" not in st.session_state:
    st.session_state.role = None

if "view" not in st.session_state:
    st.session_state.view = "classes"

if "selected_class_id" not in st.session_state:
    st.session_state.selected_class_id = None

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None

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
# CLASSES PAGE
# ======================================================
if st.session_state.view == "classes":

    header = st.columns([6,1])
    header[0].subheader("Classes")

    if st.session_state.role == "admin":
        if header[1].button("➕"):
            st.session_state.selected_class_id = None
            st.session_state.edit_mode = True
            st.session_state.view = "class"
            st.rerun()

    for c in fetch_classes():
        with st.container(border=True):
            cols = st.columns([8,1])

            meta = (
                f"Instansie: {c[2]} | Graad: {c[3]} | Groep: {c[4]} | "
                f"Vak: {c[5]} | {c[6]} | {c[7]} | {c[8]}"
            )

            if cols[0].button(f"📄 {c[1]}\n\n{meta}", key=f"open_{c[0]}"):
                st.session_state.selected_class_id = c[0]
                st.session_state.edit_mode = False
                st.session_state.view = "class"
                st.rerun()

            if st.session_state.role == "admin":
                if cols[1].button("🗑", key=f"del_{c[0]}"):
                    st.session_state.confirm_delete = ("class", c[0])

    # ---- DELETE CONFIRM ----
    if st.session_state.confirm_delete:
        t, cid = st.session_state.confirm_delete
        st.warning("Are you sure you want to delete this class?")
        c1, c2 = st.columns(2)
        if c1.button("Yes, delete"):
            q("DELETE FROM files WHERE id=?", (cid,))
            st.session_state.confirm_delete = None
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_delete = None
            st.rerun()

# ======================================================
# CLASS PAGE
# ======================================================
if st.session_state.view == "class":

    cid = st.session_state.selected_class_id
    is_new = cid is None
    is_admin = st.session_state.role == "admin"

    data = [None]*9 if is_new else q("SELECT * FROM files WHERE id=?", (cid,))[0]

    # ---------- EDIT BUTTON ----------
    if is_admin and not is_new:
        if st.button("✏️ Edit class"):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()

    # ---------- EDIT FORM ----------
    if is_admin and st.session_state.edit_mode:
        st.subheader("Class details")

        name = st.text_input("Name", data[1])
        inst = st.text_input("Instansie", data[2])
        graad = st.text_input("Graad", data[3])
        groep = st.number_input("Groep", 1, 99, value=data[4] or 1)
        vak = st.text_input("Vak", data[5])
        aan = st.selectbox("Aanlyn", ["Aanlyn", "In Persoon"])
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
            st.session_state.view = "classes"
            st.rerun()

    # ---------- STUDENTS ----------
    if not is_new:
        st.subheader("Students")

        students = q("SELECT id,name FROM students WHERE class_id=?", (cid,))
        for s in students:
            row = st.columns([8,1])
            row[0].write(s[1])

            if is_admin and st.session_state.edit_mode:
                if row[1].button("🗑", key=f"sdel_{s[0]}"):
                    st.session_state.confirm_delete = ("student", s[0])

        if is_admin and st.session_state.edit_mode:
            with st.form("add_student"):
                n = st.text_input("Student name")
                if st.form_submit_button("Add"):
                    q("INSERT INTO students (class_id,name) VALUES (?,?)", (cid,n))
                    st.rerun()
