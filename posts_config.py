import requests
import json

# Instagram biznes yoki creator account ID
APP_USERS_IG_ID = "17841475962377751"
ACCESS_TOKEN = "IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3"

API_VERSION = "v23.0"
HOST_URL = "https://graph.instagram.com"  # Siz so‘ragan host

# Webhookdan keladigan qiymatlar
COMMENT_ID = "18069875366138879"  # Foydalanuvchi kommenti ID

def send_private_reply_generic(comment_id):
    """
    Private reply + Generic Template yuborish
    """
    url = f"{HOST_URL}/{API_VERSION}/{APP_USERS_IG_ID}/messages"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    payload = {
        "recipient": {
            "comment_id": comment_id  # private reply uchun comment_id ishlatiladi
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Bizning yangi mahsulot!",
                            "image_url": "https://example.com/image.jpg",
                            "subtitle": "Qo‘shimcha ma’lumot olish uchun tugmani bosing",
                            "default_action": {
                                "type": "web_url",
                                "url": "https://example.com"
                            },
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "url": "https://example.com",
                                    "title": "Saytga o‘tish"
                                },
                                {
                                    "type": "postback",
                                    "title": "Batafsil",
                                    "payload": "DETAILS_PAYLOAD"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("✅ Xabar yuborildi:", response.json())
    else:
        print("❌ Xato:", response.status_code, response.text)

# Ishga tushirish
send_private_reply_generic(COMMENT_ID)
