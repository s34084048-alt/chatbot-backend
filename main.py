"""
AI Chatbot Backend
FastAPI + OpenAI API
Built by Farzad Abbasi — AI Developer, Dubai UAE
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Chatbot API", version="1.0.0")

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BUSINESS_PROFILES = {
    "default": {
        "name": "Our Business",
        "system": """You are a helpful customer service AI assistant.
Be friendly, concise, and professional.
Keep responses under 3 sentences unless asked for more detail.
Support both Arabic and English."""
    },
    "realestate_demo": {
        "name": "Prime Properties Dubai",
        "system": """You are an AI assistant for Prime Properties Dubai.
Services: buying, selling, renting in Dubai, Abu Dhabi, Sharjah.
Contact: +971-XX-XXX-XXXX | info@primeproperties.ae
Hours: Mon-Sat 9am-7pm UAE time.
Respond in Arabic or English based on what the user writes."""
    },
    "clinic_demo": {
        "name": "Wellness Clinic Dubai",
        "system": """You are an AI receptionist for Wellness Clinic Dubai.
Services: consultation, dental, physiotherapy, dermatology.
Location: Business Bay, Dubai.
Hours: Sat-Thu 8am-9pm, Fri 2pm-9pm.
Never give specific medical advice. Respond in Arabic or English."""
    },
}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    business_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    business_name: str

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Chatbot API"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    profile = BUSINESS_PROFILES.get(req.business_id, BUSINESS_PROFILES["default"])
    messages = []
    for msg in (req.history or []):
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})
    if len(messages) > 10:
        messages = messages[-10:]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=400,
            messages=[{"role": "system", "content": profile["system"]}] + messages,
        )
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply, business_name=profile["name"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

@app.post("/api/lead")
async def capture_lead(request: Request):
    data = await request.json()
    print(f"New Lead: {data}")
    return {"status": "received", "message": "Lead captured successfully"}

@app.get("/api/profiles")
def list_profiles():
    return {bid: {"name": p["name"]} for bid, p in BUSINESS_PROFILES.items()}
