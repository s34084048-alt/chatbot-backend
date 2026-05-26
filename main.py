"""
AI Chatbot Backend
FastAPI + Claude API
Built by Farzad Abbasi — AI Developer, Dubai UAE
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# ── CORS (هر client site رو اضافه کن) ──
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ══════════════════════════════════════════
# BUSINESS PROFILES
# هر مشتری یه profile جداگانه داره
# ══════════════════════════════════════════
BUSINESS_PROFILES = {
    "default": {
        "name": "Our Business",
        "system": """You are a helpful customer service AI assistant.
Be friendly, concise, and professional.
Answer questions about services and pricing.
If you don't know something, offer to connect them with a human.
Keep responses under 3 sentences unless asked for more detail.
Support both Arabic and English — respond in the same language the user writes in."""
    },

    # ── مثال: Real Estate Agency ──
    "realestate_demo": {
        "name": "Prime Properties Dubai",
        "system": """You are an AI assistant for Prime Properties Dubai, a premium real estate agency.
Services: buying, selling, and renting properties in Dubai, Abu Dhabi, and Sharjah.
Areas covered: Downtown Dubai, Palm Jumeirah, JBR, Business Bay, Dubai Marina.
Contact: +971-XX-XXX-XXXX | info@primeproperties.ae
Working hours: Mon-Sat 9am-7pm UAE time.
Be professional and warm. Help visitors find properties, schedule viewings, or get valuations.
Respond in the same language the user writes in (Arabic or English)."""
    },

    # ── مثال: Clinic ──
    "clinic_demo": {
        "name": "Wellness Clinic Dubai",
        "system": """You are an AI receptionist for Wellness Clinic Dubai.
Services: general consultation, dental, physiotherapy, dermatology.
Location: Business Bay, Dubai.
Appointments: call +971-XX-XXX or book online at wellnessclinic.ae
Hours: Sat-Thu 8am-9pm, Fri 2pm-9pm.
Insurance accepted: Daman, AXA, MetLife, Thiqa.
Be caring and professional. Help book appointments and answer basic medical FAQs.
Never give specific medical advice — always recommend consulting a doctor.
Respond in Arabic or English based on what the user writes."""
    },
}


# ══════════════════════════════════════════
# MODELS
# ══════════════════════════════════════════
class Message(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    business_id: Optional[str] = "default"
    lead_info: Optional[dict] = None  # اگه lead capture فعاله

class ChatResponse(BaseModel):
    reply: str
    business_name: str


# ══════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Chatbot API"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # پیدا کردن profile کسب‌وکار
    profile = BUSINESS_PROFILES.get(req.business_id, BUSINESS_PROFILES["default"])

    # ساخت تاریخچه مکالمه
    messages = []
    for msg in (req.history or []):
        messages.append({"role": msg.role, "content": msg.content})

    # اضافه کردن پیام جدید
    messages.append({"role": "user", "content": req.message})

    # محدود کردن history به ۱۰ پیام (صرفه‌جویی در token)
    if len(messages) > 10:
        messages = messages[-10:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=400,
            messages=[{"role": "system", "content": profile["system"]}] + messages,
        )

        reply = response.choices[0].message.content

        return ChatResponse(
            reply=reply,
            business_name=profile["name"]
        )
except Exception as auth_err:
            if "401" in str(auth_err) or "authentication" in str(auth_err).lower():
                raise HTTPException(status_code=401, detail="Invalid API key")
            elif "429" in str(auth_err) or "rate" in str(auth_err).lower():
                raise HTTPException(status_code=429, detail="Rate limit reached")
            else:
                raise HTTPException(status_code=500, detail=f"AI error: {str(auth_err)}")
   

@app.post("/api/lead")
async def capture_lead(request: Request):
    """ذخیره اطلاعات lead از chatbot"""
    data = await request.json()
    # در production: ذخیره در database یا ارسال به email/CRM
    # فعلاً لاگ می‌کنیم
    print(f"📧 New Lead: {data}")
    return {"status": "received", "message": "Lead captured successfully"}


@app.get("/api/profiles")
def list_profiles():
    """لیست business profileها"""
    return {
        bid: {"name": p["name"]}
        for bid, p in BUSINESS_PROFILES.items()
    }
