from voice.tts import speak
import json
import time
from langdetect import detect
from agent.reasoning.agent import understand_request
from agent.tools.appointment_tools import execute_tool
import psycopg2

conn = psycopg2.connect(
    dbname="clinic_ai",
    user="postgres",
    password="7730897312",
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

session_memory = {}

def get_saved_language(patient_id: str):
    cursor.execute(
        "SELECT preferred_language FROM patient_profiles WHERE patient_id=%s",
        (patient_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def save_language(patient_id: str, language: str):
    cursor.execute(
        """
        INSERT INTO patient_profiles (patient_id, preferred_language, updated_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (patient_id)
        DO UPDATE SET preferred_language=EXCLUDED.preferred_language, updated_at=CURRENT_TIMESTAMP
        """,
        (patient_id, language)
    )
    conn.commit()

def log_conversation(user_message: str, agent_response: str, language: str):
    cursor.execute(
        """
        INSERT INTO conversation_logs (user_message, agent_response, language)
        VALUES (%s, %s, %s)
        """,
        (user_message, agent_response, language)
    )
    conn.commit()

def log_latency(user_message: str, language: str, stt_ms: int, reasoning_ms: int, tool_ms: int, tts_ms: int, total_ms: int):
    cursor.execute(
        """
        INSERT INTO latency_logs (user_message, detected_language, stt_ms, reasoning_ms, tool_ms, tts_ms, total_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_message, language, stt_ms, reasoning_ms, tool_ms, tts_ms, total_ms)
    )
    conn.commit()

def localize_response(result, language: str):
    code = result.get("code")

    if language == "hi":
        if code == "booked":
            return f"{result['doctor']} के साथ आपकी अपॉइंटमेंट {result['date']} को {result['time']} पर बुक हो गई है।"
        if code == "checked":
            return f"आपकी नवीनतम अपॉइंटमेंट {result['doctor']} के साथ {result['date']} को {result['time']} पर है। स्थिति {result['appointment_status']} है।"
        if code == "cancelled":
            return f"{result['doctor']} के साथ आपकी अपॉइंटमेंट रद्द कर दी गई है।"
        if code == "rescheduled":
            return f"आपकी अपॉइंटमेंट {result['date']} को {result['time']} पर पुनर्निर्धारित कर दी गई है।"
        if code == "slot_conflict":
            alts = ", ".join(result["alternatives"])
            return f"यह स्लॉट उपलब्ध नहीं है। उपलब्ध विकल्प हैं: {alts}"
        if code == "past_time":
            return "पिछली तारीख या समय के लिए अपॉइंटमेंट बुक नहीं की जा सकती।"
        if code == "no_appointments":
            return "कोई अपॉइंटमेंट नहीं मिली।"
        if code == "unknown_intent":
            return "माफ़ कीजिए, मैं समझ नहीं पाया।"
        return "ठीक है।"

    if language == "ta":
        if code == "booked":
            return f"{result['doctor']} உடன் உங்கள் நேரம் {result['date']} அன்று {result['time']}க்கு பதிவு செய்யப்பட்டது."
        if code == "checked":
            return f"உங்கள் சமீபத்திய நேரம் {result['doctor']} உடன் {result['date']} அன்று {result['time']}க்கு உள்ளது. நிலை {result['appointment_status']}."
        if code == "cancelled":
            return f"{result['doctor']} உடன் உங்கள் நேரம் ரத்து செய்யப்பட்டது."
        if code == "rescheduled":
            return f"உங்கள் நேரம் {result['date']} அன்று {result['time']}க்கு மாற்றப்பட்டது."
        if code == "slot_conflict":
            alts = ", ".join(result["alternatives"])
            return f"அந்த நேரம் கிடைக்கவில்லை. கிடைக்கும் நேரங்கள்: {alts}"
        if code == "past_time":
            return "கடந்த நேரத்திற்கு நேரம் பதிவு செய்ய முடியாது."
        if code == "no_appointments":
            return "எந்த நேரமும் கிடைக்கவில்லை."
        if code == "unknown_intent":
            return "மன்னிக்கவும், எனக்கு புரியவில்லை."
        return "சரி."

    # default English
    if code == "booked":
        return f"Your appointment with {result['doctor']} is booked for {result['date']} at {result['time']}."
    if code == "checked":
        return f"Your latest appointment is with {result['doctor']} on {result['date']} at {result['time']}. Status is {result['appointment_status']}."
    if code == "cancelled":
        return f"Your appointment with {result['doctor']} has been cancelled."
    if code == "rescheduled":
        return f"Your appointment has been rescheduled to {result['date']} at {result['time']}."
    if code == "slot_conflict":
        alts = ", ".join(result["alternatives"])
        return f"That slot is unavailable. Available alternatives are {alts}."
    if code == "past_time":
        return "You cannot book an appointment in the past."
    if code == "no_appointments":
        return "No appointments found."
    if code == "unknown_intent":
        return "Sorry, I did not understand."
    return "Okay."

def process_request(text: str):
    total_start = time.perf_counter()

    try:
        user_id = "Rahul"

        stt_start = time.perf_counter()
        # text already received, no actual STT here
        stt_ms = int((time.perf_counter() - stt_start) * 1000)

        try:
            detected_language = detect(text)
        except Exception:
            detected_language = get_saved_language(user_id) or "en"

        if detected_language not in ["en", "hi", "ta"]:
            detected_language = get_saved_language(user_id) or "en"

        save_language(user_id, detected_language)

        print("Detected language:", detected_language)

        reasoning_start = time.perf_counter()
        result = understand_request(text)
        print("AI RESULT:", result)
        data = json.loads(result)
        intent = data.get("intent")
        reasoning_ms = int((time.perf_counter() - reasoning_start) * 1000)

        pending = session_memory.get(user_id)

        if intent == "greeting":
            if detected_language == "hi":
                response = "नमस्ते! मैं आपकी अपॉइंटमेंट बुक, चेक, कैंसल या रिस्केड्यूल करने में मदद कर सकता हूँ।"
            elif detected_language == "ta":
                response = "வணக்கம்! நான் உங்கள் நேரத்தை பதிவு செய்ய, பார்க்க, ரத்து செய்ய, மாற்ற உதவுவேன்."
            else:
                response = "Hello! I can help you book, check, cancel, or reschedule appointments."

            tts_start = time.perf_counter()
            speak(response)
            tts_ms = int((time.perf_counter() - tts_start) * 1000)
            total_ms = int((time.perf_counter() - total_start) * 1000)

            log_conversation(text, response, detected_language)
            log_latency(text, detected_language, stt_ms, reasoning_ms, 0, tts_ms, total_ms)
            return response

        if pending == "awaiting_doctor":
            data["intent"] = "book_appointment"
            data["patient_id"] = user_id
            data.setdefault("date", "tomorrow")
            data.setdefault("time", "10:00 AM")
            intent = "book_appointment"
            session_memory[user_id] = None

        elif intent == "book_appointment" and not data.get("doctor"):
            session_memory[user_id] = "awaiting_doctor"
            if detected_language == "hi":
                response = "आप किस डॉक्टर के साथ अपॉइंटमेंट बुक करना चाहते हैं? उदाहरण: कार्डियोलॉजिस्ट।"
            elif detected_language == "ta":
                response = "நீங்கள் எந்த மருத்துவருடன் நேரம் பதிவு செய்ய விரும்புகிறீர்கள்? உதாரணம்: கார்டியாலஜிஸ்ட்."
            else:
                response = "Which doctor would you like to book? For example, cardiologist."

            tts_start = time.perf_counter()
            speak(response)
            tts_ms = int((time.perf_counter() - tts_start) * 1000)
            total_ms = int((time.perf_counter() - total_start) * 1000)

            log_conversation(text, response, detected_language)
            log_latency(text, detected_language, stt_ms, reasoning_ms, 0, tts_ms, total_ms)
            return response

        if intent == "provide_doctor" and pending != "awaiting_doctor":
            if detected_language == "hi":
                response = "कृपया बताइए कि आप क्या करना चाहते हैं, जैसे अपॉइंटमेंट बुक करना।"
            elif detected_language == "ta":
                response = "தயவுசெய்து நீங்கள் என்ன செய்ய விரும்புகிறீர்கள் என்று சொல்லுங்கள், உதாரணமாக நேரம் பதிவு செய்ய."
            else:
                response = "Please tell me what you want to do, for example book an appointment."

            tts_start = time.perf_counter()
            speak(response)
            tts_ms = int((time.perf_counter() - tts_start) * 1000)
            total_ms = int((time.perf_counter() - total_start) * 1000)

            log_conversation(text, response, detected_language)
            log_latency(text, detected_language, stt_ms, reasoning_ms, 0, tts_ms, total_ms)
            return response

        if intent == "unknown" or intent is None:
            if detected_language == "hi":
                response = "माफ़ कीजिए, मैं समझ नहीं पाया। आप कह सकते हैं: अपॉइंटमेंट बुक करो, चेक करो, कैंसल करो, या रिस्केड्यूल करो।"
            elif detected_language == "ta":
                response = "மன்னிக்கவும், எனக்கு புரியவில்லை. நீங்கள் பதிவு செய், பார்க்க, ரத்து செய் அல்லது மாற்று என்று சொல்லலாம்."
            else:
                response = "Sorry, I did not understand. You can say book appointment, check appointment, cancel appointment, or reschedule appointment."

            tts_start = time.perf_counter()
            speak(response)
            tts_ms = int((time.perf_counter() - tts_start) * 1000)
            total_ms = int((time.perf_counter() - total_start) * 1000)

            log_conversation(text, response, detected_language)
            log_latency(text, detected_language, stt_ms, reasoning_ms, 0, tts_ms, total_ms)
            return response

        tool_start = time.perf_counter()
        tool_result = execute_tool(intent, data)
        tool_ms = int((time.perf_counter() - tool_start) * 1000)

        response = localize_response(tool_result, detected_language)

        tts_start = time.perf_counter()
        speak(response)
        tts_ms = int((time.perf_counter() - tts_start) * 1000)

        total_ms = int((time.perf_counter() - total_start) * 1000)

        print(
            f"Latency => stt:{stt_ms}ms reasoning:{reasoning_ms}ms tool:{tool_ms}ms "
            f"tts:{tts_ms}ms total:{total_ms}ms"
        )

        log_conversation(text, response, detected_language)
        log_latency(text, detected_language, stt_ms, reasoning_ms, tool_ms, tts_ms, total_ms)

        return response

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return error_msg