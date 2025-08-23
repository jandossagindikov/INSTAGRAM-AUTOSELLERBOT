# instagram_api.py
import requests

ACCESS_TOKEN = "YOUR_LONIGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3G_ACCESS_TOKEN"  # bu yerga tokeningizni yozing
API_BASE = "https://graph.instagram.com/v23.0"

def reply_to_comment(comment_id, message):
    """Kommentga javob yozish"""
    url = f"{API_BASE}/{comment_id}/replies"
    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print("[OK] Kommentga javob yuborildi")
    else:
        print("[ERROR] Kommentga javob yuborilmadi:", r.text)

def send_quick_replies(user_id, prompt_text, replies):
    """Quick Replies yuborish"""
    url = f"{API_BASE}/{user_id}/messages"
    payload = {
        "recipient": {"id": user_id},
        "messaging_type": "RESPONSE",
        "message": {
            "text": prompt_text,
            "quick_replies": [
                {"content_type": "text", "title": r["title"], "payload": r["payload"]}
                for r in replies
            ]
        },
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    print("[Quick Replies]", r.status_code, r.text)

def send_generic_template(user_id, elements):
    """Generic Template carousel yuborish"""
    url = f"{API_BASE}/{user_id}/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }
        },
        "access_token": ACCESS_TOKEN
    }
    r = requests.post(url, json=payload)
    print("[Generic Template]", r.status_code, r.text)
