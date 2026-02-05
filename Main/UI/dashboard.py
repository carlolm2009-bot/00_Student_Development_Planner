import streamlit as st
import pandas as pd
from Services.students import list_students, add_student


def render():
    st.title("LTL Pathfinder")

    # -----------------------
    # SESSION STATE
    # -----------------------
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False

    # ======================
    # TOP ACTION BAR
    # ======================
    a1, a2, a3, a4, a5, a6 = st.columns([5,1,1,1,1,1])

    with a1:
        st.markdown("### ")

    with a2:
        st.button("Categories")

    with a3:
        st.button("Delete All")

    with a4:
        st.button("Admin")

    with a5:
        if st.button("Add Student", type="primary"):
            st.session_state.show_add_form = not st.session_state.show_add_form

    with a6:
        st.button("AI Guide")
        st.button("Export")

    st.divider()

    # ======================
    # FILTER BAR
    # ======================
    f1, f2, f3, f4, f5 = st.columns(5)

    f1.selectbox("Filter by class", ["All classes"])
    f2.selectbox("Filter by subject", ["All subjects"])
    f3.text_input("Search students", placeholder="Search by name...")
    f4.selectbox("Filter by grade", ["All grades"])
    f5.selectbox("Filter by school", ["All schools"])

    st.button("Clear")

    st.divider()

    # ======================
    # KPI CARDS
    # ======================
    students = list_students()
    total_students = len(students)

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Students", total_students)
    k2.metric("This Month", "0 students")
    k3.metric("Recent Notes", "0 notes")

    # ======================
    # ADD STUDENT FORM (TOGGLED)
    # ======================
    if st.session_state.show_add_form:
        with st.container(border=True):
            st.subheader("Add Student")

            c1, c2 = st.columns(2)
            first = c1.text_input("First name")
            last = c2.text_input("Last name")

            c3, c4 = st.columns(2)
            school = c3.text_input("School")
            grade = c4.text_input("Grade")

            c5, c6 = st.columns([1,1])
            if c5.button("Save", type="primary"):
                if not first.strip() or not last.strip():
                    st.error("First and last name are required.")
                else:
                    add_student(first, last, school, grade)
                    st.success("Student added!")
                    st.session_state.show_add_form = False
                    st.rerun()

            if c6.button("Cancel"):
                st.session_state.show_add_form = False
                st.rerun()

    st.divider()

    # ======================
    # STUDENTS TABLE
    # ======================
    st.subheader("Students")

    if not students:
        st.info("No students yet.")
        return

    df = pd.DataFrame(students)

    cols = ["first_name", "last_name", "school", "grade", "created_at"]
    df = df[[c for c in cols if c in df.columns]]

    st.dataframe(df, use_container_width=True, hide_index=True)
