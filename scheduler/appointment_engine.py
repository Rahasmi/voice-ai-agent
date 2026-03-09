from database.postgres_client import db

def book_appointment(doctor,date,time):

    if db.slot_exists(doctor,date,time):
        return {"message":"Slot unavailable"}

    db.insert(doctor,date,time)

    return {"message":"Appointment booked"}

def cancel_appointment(doctor,date,time):

    db.delete(doctor,date,time)

    return {"message":"Appointment cancelled"}