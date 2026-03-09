def call_patient(patient, message):
    print(f"Calling {patient}: {message}")

def appointment_reminder(patient):

    message = "Reminder: you have appointment tomorrow"

    call_patient(patient, message)