from 00_Student_Development_Planner.Database import load_data, save_data
from datetime import datetime
import uuid

def list_students():
    data = load_data()
    return data.get("students", [])

def create_student(first_name, last_name, school_name="", grade=""):
    data = load_data()

    new_student = {
        "id": str(uuid.uuid4()),
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "school_name": school_name.strip(),
        "grade": grade.strip(),
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"
    }

    data["students"].append(new_student)
    save_data(data)

    return new_student["id"]

