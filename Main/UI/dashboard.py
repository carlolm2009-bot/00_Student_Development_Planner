import streamlit as st
import pandas as pd
from Services.students import list_students, add_student, filter_students, delete_student


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

            c5, c6 = st.columns(2)
            subject = c3.text_input("Subject")
            clas = c4.text_input("Class")

            c7, c8 = st.columns([1,1])
            if c7.button("Save", type="primary"):
                if not first.strip() or not last.strip():
                    st.error("First and last name are required.")
                else:
                    add_student(first, last, school, grade, subject, clas)
                    st.success("Student added!")
                    st.session_state.show_add_form = False
                    st.rerun()

            if c8.button("Cancel"):
                st.session_state.show_add_form = False
                st.rerun()

    # ======================
    # FILTER BAR
    # ======================
    
    st.divider()

    all_students = list_students()

    classes = sorted({s.get("class", "") for s in all_students if s.get("class")})
    subjects = sorted({s.get("subject", "") for s in all_students if s.get("subject")})
    grades = sorted({s.get("grade", "") for s in all_students if s.get("grade")})
    schools = sorted({s.get("school", "") for s in all_students if s.get("school")})

    f1, f2, f3, f4, f5 = st.columns(5)

    search_query = f1.text_input("Search students", placeholder="Search by name...",key="search_query")
    school_filter = f2.selectbox("Filter by school", ["All schools"] + schools,key="school_filter")
    grade_filter = f3.selectbox("Filter by grade", ["All grades"] + grades,key="grade_filter")
    subject_filter = f4.selectbox("Filter by subject", ["All subjects"] + subjects,key="subject_filter")
    class_filter = f5.selectbox("Filter by class", ["All classes"] + classes,key="class_filter")
    
    clear = st.button("Clear")

    if clear:
        defaults = {
            "search_query": "",
            "school_filter": "All schools",
            "grade_filter": "All grades",
            "subject_filter": "All subjects",
            "class_filter": "All classes",
        }

        for key, value in defaults.items():
            st.session_state[key] = value

    st.rerun()

    # ======================
    # KPI CARDS
    # ======================
    students = filter_students(
    class_filter=class_filter,
    subject_filter=subject_filter,
    grade_filter=grade_filter,
    school_filter=school_filter,
    search_query=search_query
)

    total_students = len(students)

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Students", total_students)
    k2.metric("This Month", total_students)
    k3.metric("Recent Notes", "0 notes")

    # ======================
    # STUDENTS TABLE
    # ======================
    
    st.subheader("Students")

    if not students:
        st.info("No students found.")
    else:
        c1, c2, c3, c4, c5, c6, c7 = st.columns([3,2,2,2,2,2,1])
        c1.write("ID")
        c2.write('Name')
        c3.write("School")
        c4.write("Grade")
        c5.write("subject")
        c6.write("Class")
        c7.write("")
        for student in students:
            c1, c2, c3, c4, c5, c6, c7 = st.columns([3,2,2,2,2,2,1])

            c1.write(student.get("id"))
            c2.write(f"{student.get('first_name')} {student.get('last_name')}")
            c3.write(student.get("school", ""))
            c4.write(student.get("grade", ""))
            c5.write(student.get("subject", ""))
            c6.write(student.get("class", ""))

            if c7.button("❌", key=f"delete_{student['id']}"):
                success = delete_student(student["id"])
                if success:
                    st.success("Student deleted")
                    st.rerun()
                else:
                    st.error("Student not found")
