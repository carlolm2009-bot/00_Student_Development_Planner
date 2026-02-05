import streamlit as st
import pandas as pd
from Services.students import list_students, add_student

def render():
    st.title("LTL Pathfinder")

    # ======================
    # TOP ACTION BAR
    # ======================
    a1, a2, a3, a4 = st.columns([6, 1, 1, 1])

    with a1:
        st.markdown("### Dashboard")

    with a2:
        st.button("Add Student")

    with a3:
        st.button("AI Guide")

    with a4:
        st.button("Export")

    st.divider()

    # ======================
    # FILTER BAR
    # ======================
    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:
        st.selectbox("Filter by class", ["All", "Class A", "Class B"])

    with f2:
        st.selectbox("Filter by subject", ["All", "Python", "Scratch", "Robotics"])

    with f3:
        st.selectbox("Filter by grade", ["All", "Grade 4", "Grade 5", "Grade 6"])

    with f4:
        st.selectbox("Filter by school", ["All", "Lincoln Elementary", "Sunrise School"])

    with f5:
        st.button("Clear")

    st.divider()

    # ======================
    # KPI CARDS
    # ======================
    students = list_students()
    total_students = len(students)

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Total Students", total_students)

    with k2:
        st.metric("This Month", 0)

    with k3:
        st.metric("Recent Notes", 0)

    st.divider()

    # ======================
    # ADD STUDENT (FORM)
    # ======================
    with st.expander("➕ Add New Student"):
        c1, c2 = st.columns(2)
        first = c1.text_input("First name")
        last = c2.text_input("Last name")

        c3, c4 = st.columns(2)
        school = c3.text_input("School")
        grade = c4.text_input("Grade")

        if st.button("Save Student", type="primary"):
            if not first.strip() or not last.strip():
                st.error("First and last name are required.")
            else:
                add_student(first, last, school, grade)
                st.success("Student added!")
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
