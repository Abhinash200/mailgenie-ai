# MailGenie AI

MailGenie AI is a smart email assistant that uses OpenAI or Groq's LLaMA model to generate polished emails with selected tone, grammar correction, file attachments, and optional Google Calendar scheduling.

## Features
- ✅ Email tone selection
- ✅ Grammar correction using LanguageTool
- ✅ AI email generation via OpenAI or Groq (LLaMA)
- ✅ Gmail SMTP email sending
- ✅ Google Calendar API integration
- ✅ Attachment support
- ✅ Basic interaction memory

## Setup
1. Copy `.env.example` to `.env` and fill in your API keys.
2. Install dependencies: `pip install -r requirements.txt`
3. Add your `credentials.json` for Google Calendar.
4. Run the app: `streamlit run app.py`

## Notes
- Use Gmail App Password for email sending.
- Uses Streamlit as UI.