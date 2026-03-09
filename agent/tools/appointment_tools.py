import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="clinic_ai",
        user="postgres",
        password="7730897312",
        port="5433"
    )

def suggest_alternatives(requested_time: str):
    all_slots = ["10:00 AM", "11:00 AM", "02:00 PM", "04:00 PM"]
    return [slot for slot in all_slots if slot != requested_time][:2]

def book_appointment(data):
    conn = get_connection()
    cursor = conn.cursor()

    patient_id = data.get("patient_id", "Rahul")
    doctor = data.get("doctor", "general physician")
    date = data.get("date", "tomorrow")
    time = data.get("time", "10:00 AM")

    if date == "yesterday":
        cursor.close()
        conn.close()
        return {
            "status": "error",
            "code": "past_time",
            "message": "Past date not allowed"
        }

    cursor.execute(
        """
        SELECT id FROM appointments
        WHERE doctor=%s AND date=%s AND time=%s AND status='booked'
        """,
        (doctor, date, time)
    )
    existing = cursor.fetchone()

    if existing:
        alternatives = suggest_alternatives(time)
        cursor.close()
        conn.close()
        return {
            "status": "error",
            "code": "slot_conflict",
            "doctor": doctor,
            "date": date,
            "time": time,
            "alternatives": alternatives
        }

    cursor.execute(
        """
        INSERT INTO appointments (patient_id, doctor, date, time, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (patient_id, doctor, date, time, "booked")
    )
    conn.commit()

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "code": "booked",
        "patient_id": patient_id,
        "doctor": doctor,
        "date": date,
        "time": time
    }

def check_appointment(data):
    conn = get_connection()
    cursor = conn.cursor()

    patient_id = data.get("patient_id", "Rahul")

    cursor.execute(
        """
        SELECT patient_id, doctor, date, time, status
        FROM appointments
        WHERE patient_id=%s
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,)
    )
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return {
            "status": "error",
            "code": "no_appointments"
        }

    return {
        "status": "success",
        "code": "checked",
        "patient_id": row[0],
        "doctor": row[1],
        "date": row[2],
        "time": row[3],
        "appointment_status": row[4]
    }

def cancel_appointment(data):
    conn = get_connection()
    cursor = conn.cursor()

    patient_id = data.get("patient_id", "Rahul")

    cursor.execute(
        """
        SELECT id, doctor, date, time
        FROM appointments
        WHERE patient_id=%s AND status='booked'
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,)
    )
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return {
            "status": "error",
            "code": "no_appointments"
        }

    appt_id, doctor, date, time = row

    cursor.execute(
        "UPDATE appointments SET status='cancelled' WHERE id=%s",
        (appt_id,)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "code": "cancelled",
        "patient_id": patient_id,
        "doctor": doctor,
        "date": date,
        "time": time
    }

def reschedule_appointment(data):
    conn = get_connection()
    cursor = conn.cursor()

    patient_id = data.get("patient_id", "Rahul")
    new_date = data.get("new_date", "day after tomorrow")
    new_time = data.get("new_time", "11:00 AM")

    if new_date == "yesterday":
        cursor.close()
        conn.close()
        return {
            "status": "error",
            "code": "past_time"
        }

    cursor.execute(
        """
        SELECT id, doctor
        FROM appointments
        WHERE patient_id=%s AND status='booked'
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,)
    )
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return {
            "status": "error",
            "code": "no_appointments"
        }

    appt_id, doctor = row

    cursor.execute(
        """
        SELECT id FROM appointments
        WHERE doctor=%s AND date=%s AND time=%s AND status='booked' AND id<>%s
        """,
        (doctor, new_date, new_time, appt_id)
    )
    conflict = cursor.fetchone()

    if conflict:
        alternatives = suggest_alternatives(new_time)
        cursor.close()
        conn.close()
        return {
            "status": "error",
            "code": "slot_conflict",
            "doctor": doctor,
            "date": new_date,
            "time": new_time,
            "alternatives": alternatives
        }

    cursor.execute(
        """
        UPDATE appointments
        SET date=%s, time=%s, status='booked'
        WHERE id=%s
        """,
        (new_date, new_time, appt_id)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "code": "rescheduled",
        "patient_id": patient_id,
        "doctor": doctor,
        "date": new_date,
        "time": new_time
    }

def execute_tool(intent, data):
    if intent == "book_appointment":
        return book_appointment(data)
    elif intent == "check_appointment":
        return check_appointment(data)
    elif intent == "cancel_appointment":
        return cancel_appointment(data)
    elif intent == "reschedule_appointment":
        return reschedule_appointment(data)
    else:
        return {
            "status": "error",
            "code": "unknown_intent"
        }