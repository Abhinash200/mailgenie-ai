import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"

def generate_email(name, message, tone, sender_name):
    prompt = (
        f"Compose a professional email with the following details:\n"
        f"Recipient Name: {name}\n"
        f"Sender Name: {sender_name}\n"
        f"Desired Tone: {tone}\n"
        f"Key Message: {message}\n\n"
        f"STRUCTURE YOUR RESPONSE EXACTLY AS FOLLOWS:\n"
        f"Subject: [Your subject line here, keep it under 8 words]\n\n"
        f"Dear {name},\n\n"
        f"[Email body here - make sure to naturally include the key message: '{message}']\n\n"
        f"Best regards,\n"
        f"{sender_name}\n"
        f"NOTE: Do not include any additional text after the sender's name."
    )

    try:
        response = openai.ChatCompletion.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        full_response = response['choices'][0]['message']['content']

        # Extract subject and body with more robust parsing
        subject_line = "Regarding your message"  # default
        body = full_response  # default to full response if parsing fails
        
        if "Subject:" in full_response:
            subject_parts = full_response.split("Subject:", 1)
            subject_line = subject_parts[1].split("\n")[0].strip()
            body = subject_parts[1].split("\n", 1)[1].strip()
            
            # Ensure the body starts with "Dear [Name]"
            if not body.startswith(f"Dear {name}"):
                body = f"Dear {name},\n\n{body}"

        # Final cleanup of the body
        body = body.replace(f"Best regards,\n{sender_name}", "").strip()
        body += f"\n\nBest regards,\n{sender_name}"

        return subject_line, body

    except Exception as e:
        print(f"Error generating email: {e}")
        # Return a default formatted email if there's an error
        subject_line = f"Regarding your message"
        body = (
            f"Dear {name},\n\n"
            f"{message}\n\n"
            f"Best regards,\n"
            f"{sender_name}"
        )
        return subject_line, body