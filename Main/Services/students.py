import uuid
from datetime import datetime
from DataBase.Database import load_data, save_data

def list_students():
    data = load_data()
    return data["students"]

def add_student(first_name, last_name, school="", grade=""):
    data = load_data()

    student = {
        "id": str(uuid.uuid4()),
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "school": school.strip(),
        "grade": grade.strip(),
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }

    data["students"].append(student)
    save_data(data)

    return student["id"]

def delete_student(student_id):
    data = load_data()
    students = data.get("students", [])

    updated_students = [s for s in students if s.get("id") != student_id]

    # If nothing changed, student didn't exist
    if len(updated_students) == len(students):
        return False

    # Reassign IDs so they stay sequential
    for index, student in enumerate(updated_students, start=1):
        student["id"] = index

    data["students"] = updated_students
    save_data(data)

    return True

def filter_students(
    class_filter=None,
    subject_filter=None,
    grade_filter=None,
    school_filter=None,
    search_query=None
):
    students = list_students()

    filtered = []

    for student in students:

        # Filter by class
        if class_filter and class_filter != "All classes":
            if student.get("class") != class_filter:
                continue

        # Filter by subject
        if subject_filter and subject_filter != "All subjects":
            if student.get("subject") != subject_filter:
                continue

        # Filter by grade
        if grade_filter and grade_filter != "All grades":
            if student.get("grade") != grade_filter:
                continue

        # Filter by school
        if school_filter and school_filter != "All schools":
            if student.get("school") != school_filter:
                continue

        # Search filter
        if search_query:
            if search_query.lower() != student.get('first_name').lower() and search_query.lower() != student.get('last_name').lower():
                continue

        filtered.append(student)

    return filtered
