import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="clinic_ai",
        user="postgres",
        password="7730897312",
        port="5433"
    )

def run_reminder_for_latest():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT patient_id, doctor, date, time
        FROM appointments
        WHERE status='booked'
        ORDER BY id DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return "No booked appointments found for reminder."

    patient_id, doctor, date, time = row

    return f"Hello {patient_id}, this is a reminder for your appointment with {doctor} on {date} at {time}."