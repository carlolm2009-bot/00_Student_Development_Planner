import uuid
from datetime import datetime
from data.store import load_data, save_data

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

