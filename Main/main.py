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
DEFAULTS = {
    "role": None,                     # None | admin | guest
    "view": "classes",                # classes | class
    "selected_class_id": None,
    "show_filters": False,
    "edit_mode": False,
    "confirm_delete": None,
    "filters": {
        "instansie": "Geen",
        "graad": "Geen",
        "groep": "Geen",
        "vak": "Geen",
        "aanlyn": "Geen",
        "tyd": "Geen",
        "dag": "Geen",
    }
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

GEEN = "Geen"

# ======================================================
# DATABASE
# ======================================================
init_db()

def q(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_distinct(col):
    return [r[0] for r in q(
        f"SELECT DISTINCT {col} FROM files WHERE {col} IS NOT NULL AND {col} != ''"
    )]

def fetch_classes():
    sql = "SELECT * FROM files WHERE 1=1"
    vals = []

    for k, v in st.session_state.filters.items():
        if v != GEEN:
            sql += f" AND {k}=?"
            vals.append(v)

    return q(sql, vals)

# ======================================================
# LOGIN (ONLY ON FRESH RUN)
# ======================================================
def show_login():
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

if st.session_state.role is None:
    show_login()
    st.stop()

# ======================================================
# TOP BAR (PROFILE)
# ======================================================
bar = st.columns([6,1])
bar[0].empty()

with bar[1]:
    with st.popover(f"👤 {st.session_state.role.capitalize()}"):
        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()

# ======================================================
# CLASSES VIEW
# ======================================================
if st.session_state.view == "classes":

    head = st.columns([6,1,1])
    head[0].subheader("Classes")

    if head[1].button("🔍"):
        st.session_state.show_filters = not st.session_state.show_filters

    if st.session_state.role == "admin":
        if head[2].button("➕"):
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
            c[4].selectbox("Aanlyn", [GEEN,"Aanlyn","In Persoon"], key="f_aan")
            c[5].selectbox("Tyd", [GEEN]+[f"{h:02d}:00" for h in range(7,19)], key="f_tyd")
            c[6].selectbox("Dag", [GEEN,"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], key="f_dag")

            if st.button("Commit filters"):
                st.session_state.filters = {
                    "instansie": st.session_state.f_inst,
                    "graad": st.session_state.f_graad,
                    "groep": st.session_state.f_groep,
                    "vak": st.session_state.f_vak,
                    "aanlyn": st.session_state.f_aan,
                    "tyd": st.session_state.f_tyd,
                    "dag": st.session_state.f_dag,
                }
                st.session_state.show_filters = False
                st.rerun()

    # ---------- CLASS LIST ----------
    classes = fetch_classes()

    if not classes:
        st.info("No classes found")

    for c in classes:
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

# ======================================================
# CLASS VIEW
# ======================================================
if st.session_state.view == "class":

    cid = st.session_state.selected_class_id
    is_new = cid is None
    is_admin = st.session_state.role == "admin"

    data = [None]*9 if is_new else q("SELECT * FROM files WHERE id=?", (cid,))[0]

    top = st.columns([6,1,1])
    top[0].subheader("New Class" if is_new else data[1])

    if top[2].button("❌ Exit"):
        st.session_state.view = "classes"
        st.session_state.selected_class_id = None
        st.session_state.edit_mode = False
        st.rerun()

    if is_admin and not is_new:
        if top[1].button("✏️ Edit"):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()

    # ---------- EDIT MODE ----------
    if is_admin and st.session_state.edit_mode:
        st.subheader("Class Details")

        name = st.text_input("Name", data[1])
        inst = st.text_input("Instansie", data[2])
        graad = st.text_input("Graad", data[3])
        groep = st.number_input("Groep", 1, 99, value=data[4] or 1)
        vak = st.text_input("Vak", data[5])
        aan = st.selectbox("Aanlyn", ["Aanlyn","In Persoon"], index=0 if data[6]=="Aanlyn" else 1)
        tyd = st.text_input("Tyd", data[7])
        dag = st.text_input("Dag", data[8])

        if st.button("💾 Save"):
            if is_new:
                q("INSERT INTO files (name,instansie,graad,groep,vak,aanlyn,tyd,dag) VALUES (?,?,?,?,?,?,?,?)",(name,inst,graad,groep,vak,aan,tyd,dag))
            else:
                q("UPDATE files SET name=?,instansie=?,graad=?,groep=?,vak=?,aanlyn=?,tyd=?,dag=? WHERE id=?",(name,inst,graad,groep,vak,aan,tyd,dag,cid))
            st.session_state.edit_mode = False
            st.rerun()

    # ---------- STUDENTS ----------
    st.subheader("Students")

    if is_admin and st.session_state.edit_mode and not is_new:
        if st.button("➕ Add Student"):
            st.session_state.confirm_delete = ("add_student", cid)

    students = q("SELECT id,name FROM students WHERE class_id=?", (cid,))
    for s in students:
        r = st.columns([8,1])
        r[0].write(s[1])
        if is_admin and st.session_state.edit_mode:
            if r[1].button("🗑", key=f"sdel_{s[0]}"):
                st.session_state.confirm_delete = ("student", s[0])

# ======================================================
# CONFIRMATION MODAL
# ======================================================
if st.session_state.confirm_delete:
    t, val = st.session_state.confirm_delete

    with st.container(border=True):
        if t == "add_student":
            name = st.text_input("Student name")
            c1, c2 = st.columns(2)

            if c1.button("Add"):
                if not name.strip():
                    st.error("Student name cannot be empty")
                else:
                    q("INSERT INTO students (class_id, name) VALUES (?, ?)",(val, name.strip()))
                    st.session_state.confirm_delete = None
                    st.rerun()

            if c2.button("Cancel"):
                st.session_state.confirm_delete = None
                st.rerun()

        else:
            st.warning("Are you sure?")
            c1, c2 = st.columns(2)

            if c1.button("Yes"):
                if t == "class":
                    q("DELETE FROM files WHERE id=?", (val,))
                else:
                    q("DELETE FROM students WHERE id=?", (val,))
                st.session_state.confirm_delete = None
                st.rerun()

            if c2.button("Cancel"):
                st.session_state.confirm_delete = None
                st.rerun()
