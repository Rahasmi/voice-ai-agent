import json
import re

DOCTORS = [
    "cardiologist",
    "dermatologist",
    "neurologist",
    "orthopedic",
    "general physician",
    "dentist",
    "ent specialist",
    "gynecologist",
    "pediatrician",
]

def extract_doctor(text: str):
    text = text.lower().strip()
    for doctor in DOCTORS:
        if doctor in text:
            return doctor
    return None

def extract_date(text: str):
    text = text.lower()
    if "yesterday" in text:
        return "yesterday"
    if "today" in text:
        return "today"
    if "tomorrow" in text:
        return "tomorrow"
    if "day after tomorrow" in text:
        return "day after tomorrow"
    return None

def extract_time(text: str):
    text = text.lower()
    if "10" in text:
        return "10:00 AM"
    if "11" in text:
        return "11:00 AM"
    if "2" in text and ("pm" in text or "afternoon" in text):
        return "02:00 PM"
    return None

def understand_request(text: str):
    text = text.lower().strip()
    data = {}

    doctor = extract_doctor(text)
    date = extract_date(text)
    time = extract_time(text)

    if doctor:
        data["doctor"] = doctor
    if date:
        data["date"] = date
    if time:
        data["time"] = time

    if "hello" in text or "hi" in text or "hey" in text or "नमस्ते" in text or "வணக்கம்" in text:
        data["intent"] = "greeting"

    elif "reschedule" in text or "move" in text:
        data["intent"] = "reschedule_appointment"
        data["patient_id"] = "Rahul"
        data.setdefault("new_date", "day after tomorrow")
        data.setdefault("new_time", "11:00 AM")

    elif "cancel" in text:
        data["intent"] = "cancel_appointment"
        data["patient_id"] = "Rahul"

    elif "check" in text or "show" in text or "list" in text:
        data["intent"] = "check_appointment"
        data["patient_id"] = "Rahul"

    elif "book" in text or "schedule" in text:
        data["intent"] = "book_appointment"
        data["patient_id"] = "Rahul"
        data.setdefault("date", "tomorrow")
        data.setdefault("time", "10:00 AM")

    else:
        if doctor:
            data["intent"] = "provide_doctor"
            data["patient_id"] = "Rahul"
        else:
            data["intent"] = "unknown"

    return json.dumps(data)