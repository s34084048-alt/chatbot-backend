# AI Chatbot Backend — Deployment Guide
Built by Farzad Abbasi | AI Developer, Dubai UAE

---

## ساختار فایل‌ها

```
chatbot-backend/
├── main.py           ← FastAPI app + Claude API
├── requirements.txt  ← dependencies
└── .env.example      ← تنظیمات

chatbot-widget.html   ← کد embed برای سایت مشتری
service-page.html     ← صفحه فروش سرویس
```

---

## Deploy روی Railway (رایگان، ۵ دقیقه)

1. برو به https://railway.app و sign up کن
2. "New Project" → "Deploy from GitHub"
3. ریپو رو آپلود کن یا از local deploy کن
4. توی Settings → Variables اضافه کن:
   - `ANTHROPIC_API_KEY` = کلید Claude ات
   - `ALLOWED_ORIGINS` = آدرس سایت مشتری
5. بعد از deploy، یه URL مثل این می‌گیری:
   `https://chatbot-xxx.railway.app`

---

## برای هر مشتری جدید

**۱. توی `main.py` یه profile اضافه کن:**
```python
BUSINESS_PROFILES["client_name"] = {
    "name": "اسم کسب‌وکار",
    "system": """You are an AI assistant for [Business Name].
Services: ...
Location: ...
Contact: ...
Hours: ..."""
}
```

**۲. توی `chatbot-widget.html` تنظیم کن:**
```javascript
const CONFIG = {
  botName: "اسم ربات",
  businessName: "اسم کسب‌وکار",
  apiEndpoint: "https://your-backend.railway.app/api/chat",
  businessId: "client_name",  // همون کلیدی که بالا اضافه کردی
};
```

**۳. کد embed رو به مشتری بده:**
```html
<!-- این رو قبل </body> در سایت مشتری بذار -->
<script src="https://yourchatbot.netlify.app/widget.js"></script>
```

---

## قیمت‌گذاری پیشنهادی

| پکیج | قیمت | شامل |
|------|------|------|
| Basic | $300 | نصب + ۱ ماه support |
| Pro | $500 | Basic + lead capture + گزارش ماهانه |
| Monthly | $99/ماه | نگهداری + آپدیت + API costs |

---

## تست محلی

```bash
cd chatbot-backend
pip install -r requirements.txt
cp .env.example .env
# API key رو توی .env بذار
uvicorn main:app --reload
# باز کن: http://localhost:8000/docs
```
