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
defaults = {
    "role": None,                    # None | admin | guest
    "selected_class_id": None,
    "edit_mode": False,
    "show_filters": False,
    "confirm": None,                 # ("class"/"student", id)
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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

def fetch_classes():
    sql = "SELECT * FROM files WHERE 1=1"
    vals = []
    for k, v in st.session_state.filters.items():
        if v != GEEN:
            sql += f" AND {k}=?"
            vals.append(v)
    return q(sql, vals)

def get_distinct(col):
    return [r[0] for r in q(f"SELECT DISTINCT {col} FROM files WHERE {col} IS NOT NULL")]

# ======================================================
# LOGIN (ONCE PER RUN)
# ======================================================
def login_screen():
    st.title("LTL Development Planner")

    login_type = st.radio("Login as", ["Guest", "Admin"])

    if login_type == "Admin":
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
    login_screen()
    st.stop()

# ======================================================
# TOP BAR (PROFILE)
# ======================================================
top = st.columns([6,1])
top[0].markdown("## 📊 LTL Development Planner")

with top[1]:
    with st.popover(f"👤 {st.session_state.role.capitalize()}"):
        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()

st.divider()

# ======================================================
# DASHBOARD LAYOUT
# ======================================================
left, right = st.columns([3,5])

# ======================================================
# LEFT PANEL — CLASSES
# ======================================================
with left:
    header = st.columns([1,1,1])
    header[0].markdown("### Classes")

    if header[1].button("🔍"):
        st.session_state.show_filters = not st.session_state.show_filters

    if st.session_state.role == "admin":
        if header[2].button("➕"):
            st.session_state.selected_class_id = None
            st.session_state.edit_mode = True

    # -------- FILTERS --------
    if st.session_state.show_filters:
        with st.container(border=True):
            st.selectbox("Instansie", [GEEN]+get_distinct("instansie"), key="f_inst")
            st.selectbox("Graad", [GEEN]+[str(i) for i in range(1,13)], key="f_graad")
            st.selectbox("Groep", [GEEN]+list(range(1,21)), key="f_groep")
            st.selectbox("Vak", [GEEN]+get_distinct("vak"), key="f_vak")
            st.selectbox("Aanlyn", [GEEN]+get_distinct("aanlyn"), key="f_aanlyn")
            st.selectbox("Dag", [GEEN,"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], key="f_dag")

            if st.button("Apply filters"):
                st.session_state.filters = {
                    "instansie": st.session_state.f_inst,
                    "graad": st.session_state.f_graad,
                    "groep": st.session_state.f_groep,
                    "vak": st.session_state.f_vak,
                    "aanlyn": st.session_state.f_aanlyn,
                    "tyd": GEEN,
                    "dag": st.session_state.f_dag,
                }
                st.session_state.show_filters = False
                st.rerun()

    # -------- CLASS CARDS --------
    for c in fetch_classes():
        with st.container(border=True):
            if st.button(c[1], key=f"open_{c[0]}"):
                st.session_state.selected_class_id = c[0]
                st.session_state.edit_mode = False

            st.caption(
                f"{c[2]} • Graad {c[3]} • Groep {c[4]} • {c[5]} • {c[6]} • {c[7]} {c[8]}"
            )

            if st.session_state.role == "admin":
                if st.button("🗑 Delete", key=f"del_{c[0]}"):
                    st.session_state.confirm = ("class", c[0])

# ======================================================
# RIGHT PANEL — CLASS DASHBOARD
# ======================================================
with right:
    cid = st.session_state.selected_class_id

    if cid is None:
        st.info("Select a class to view students")
    else:
        data = q("SELECT * FROM files WHERE id=?", (cid,))[0]

        top = st.columns([6,1,1])
        top[0].markdown(f"### {data[1]}")

        if st.session_state.role == "admin":
            if top[1].button("✏️"):
                st.session_state.edit_mode = not st.session_state.edit_mode

        if top[2].button("❌"):
            st.session_state.selected_class_id = None
            st.session_state.edit_mode = False
            st.rerun()

        # -------- EDIT PANEL --------
        if st.session_state.role == "admin" and st.session_state.edit_mode:
            with st.expander("Edit Class", expanded=True):
                name = st.text_input("Name", data[1])
                inst = st.text_input("Instansie", data[2])
                graad = st.text_input("Graad", data[3])
                groep = st.number_input("Groep", 1, 99, value=data[4])
                vak = st.text_input("Vak", data[5])
                aan = st.selectbox("Aanlyn", ["Aanlyn","In Persoon"], index=0 if data[6]=="Aanlyn" else 1)
                tyd = st.text_input("Tyd", data[7])
                dag = st.text_input("Dag", data[8])

                if st.button("💾 Save"):
                    q(
                        """UPDATE files SET
                        name=?, instansie=?, graad=?, groep=?,
                        vak=?, aanlyn=?, tyd=?, dag=?
                        WHERE id=?""",
                        (name,inst,graad,groep,vak,aan,tyd,dag,cid)
                    )
                    st.session_state.edit_mode = False
                    st.rerun()

        # -------- STUDENTS --------
        st.divider()
        s_head = st.columns([6,1])
        s_head[0].markdown("### Students")

        if st.session_state.role == "admin" and st.session_state.edit_mode:
            if s_head[1].button("➕"):
                st.session_state.confirm = ("add_student", cid)

        for s in q("SELECT id,name FROM students WHERE class_id=?", (cid,)):
            row = st.columns([6,1])
            row[0].write(s[1])
            if st.session_state.role == "admin" and st.session_state.edit_mode:
                if row[1].button("🗑", key=f"sdel_{s[0]}"):
                    st.session_state.confirm = ("student", s[0])

# ======================================================
# CONFIRMATION MODALS
# ======================================================
if st.session_state.confirm:
    t, val = st.session_state.confirm
    with st.container(border=True):
        if t == "add_student":
            st.warning("Add student")
            name = st.text_input("Student name")
            if st.button("Add"):
                q("INSERT INTO students (class_id,name) VALUES (?,?)", (val,name))
                st.session_state.confirm = None
                st.rerun()
            if st.button("Cancel"):
                st.session_state.confirm = None
                st.rerun()
        else:
            st.warning(f"Delete this {t}?")
            c1, c2 = st.columns(2)
            if c1.button("Yes"):
                if t == "class":
                    q("DELETE FROM files WHERE id=?", (val,))
                else:
                    q("DELETE FROM students WHERE id=?", (val,))
                st.session_state.confirm = None
                st.rerun()
            if c2.button("Cancel"):
                st.session_state.confirm = None
                st.rerun()
