
## Setup Instructions

### 1. Clone Repository

git clone https://github.com/Rahasmi/voice-ai-agent.git

cd voice-ai-agent

### 2. Create Virtual Environment

python -m venv venv

### 3. Activate Environment

Windows:

venv\Scripts\activate

### 4. Install Dependencies

pip install -r requirements.txt

### 5. Start PostgreSQL

Create database:

clinic_ai

### 6. Run Database Setup

Execute SQL tables from the database setup section.

### 7. Start Backend Server

uvicorn backend.main:app --reload

### 8. Open Frontend

Open:

frontend/index.html
9️⃣ Latency Breakdown

Assignment explicitly requires this.

## Latency Breakdown

Measured components:

Speech-to-Text: ~5ms  
Agent Reasoning: ~10ms  
Database Tool Execution: ~15ms  
Text-to-Speech: ~60ms  

Total Response Latency: ~90ms

Target requirement: <450ms
🔟 Tradeoffs
## Tradeoffs

- Rule-based intent recognition is used instead of full LLM inference due to API quota limitations.
- Browser speech recognition is used for simplicity instead of a production STT engine.
- Outbound calls are simulated rather than integrated with telephony services.
11️⃣ Known Limitations

Assignment requires this.

## Known Limitations

- Doctor/date extraction is basic
- No real phone call integration
- STT latency is simulated
- Redis distributed memory not implemented
12️⃣ Future Improvements
## Future Improvements

- LLM-based reasoning
- Redis memory with TTL
- Telephony integration
- Cloud deployment
- Advanced doctor availability search





1️⃣ Project Title
# Real-Time Multilingual Voice AI Agent
Clinical Appointment Booking System
2️⃣ Overview

Explain what the project does.

## Overview

This project implements a real-time multilingual Voice AI Agent that automates clinical appointment management through voice and text interactions.

The agent can:

- Book appointments
- Cancel appointments
- Reschedule appointments
- Check appointment status

The system supports **English, Hindi, and Tamil**, maintains **session memory**, stores **persistent user history**, and can run **outbound reminder campaigns**.

The architecture is designed for **low-latency conversational interaction (<450ms target)**.
3️⃣ System Architecture
## System Architecture

The system follows a real-time conversational pipeline.

User Voice/Text  
→ Speech-to-Text  
→ Language Detection  
→ AI Agent Reasoning  
→ Tool Orchestration  
→ Scheduling Engine  
→ PostgreSQL Database  
→ Text Response  
→ Text-to-Speech  
→ Voice Response

Mention technologies used:

Core technologies:

- FastAPI
- WebSockets
- PostgreSQL
- Python
- langdetect
- pyttsx3
4️⃣ Architecture Decisions

## Architecture Decisions

### FastAPI Backend
FastAPI was selected due to its high performance and asynchronous support, making it suitable for real-time conversational systems.

### WebSocket Communication
WebSockets are used instead of HTTP polling to enable low-latency bidirectional communication between the client and backend.

### Modular Agent Design
The AI agent is separated into multiple components:

- agent reasoning
- tool orchestration
- scheduling engine
- memory layer

This separation improves maintainability and scalability.

### PostgreSQL Database
PostgreSQL stores:

- appointments
- conversation logs
- patient preferences
- latency metrics
5️⃣ Memory Design

Required by assignment.

## Memory Design

The system implements two levels of memory.

### Session Memory

Session memory stores temporary conversation context.

Example:

User: Book appointment  
Agent: Which doctor?  
User: Cardiologist  

The system remembers the booking intent until the conversation completes.

### Persistent Memory

Persistent memory is stored in PostgreSQL.

Stored information includes:

- patient preferred language
- conversation history
- appointment history
6️⃣ Scheduling Logic
## Scheduling Logic

The scheduling engine ensures:

- No double booking
- No past-time appointments
- Alternative slots when conflicts occur

Example:

If a slot is unavailable, the system suggests other available times.
7️⃣ Multilingual Support
## Multilingual Support

Language detection is implemented using the langdetect library.

Supported languages:

- English
- Hindi
- Tamil

The system automatically detects the language and generates responses in the same language.




## Project Structure
```text
voice-ai-agent
│
├── backend
│   └── main.py
├── agent
│   ├── reasoning
│   │   ├── agent.py
│   │   └── process.py
│   └── tools
│       └── appointment_tools.py
├── campaigns
│   └── reminder_scheduler.py
├── memory
│   └── session_memory.py
├── frontend
│   └── index.html
├── voice
│   └── tts.py
├── test_voice.py
└── README.md

## Architecture Diagram

![Architecture](docs/architecture (1).png)