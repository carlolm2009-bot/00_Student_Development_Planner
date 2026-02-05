import streamlit as st
import pandas as pd
from services.students import list_students, add_student

def render():
    st.title("LTL Pathfinder (Basic)")

    st.subheader("Add Student")
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
            st.success("Saved!")
            st.rerun()

    st.divider()
    st.subheader("Students")

    students = list_students()
    if not students:
        st.info("No students yet.")
        return

    df = pd.DataFrame(students)
    # nice ordering (optional)
    cols = ["id", "first_name", "last_name", "school", "grade", "created_at"]
    df = df[[c for c in cols if c in df.columns]]
    st.dataframe(df, use_container_width=True, hide_index=True)
