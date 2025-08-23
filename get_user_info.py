import requests
import json

ACCESS_TOKEN = 'IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3'
IG_ID = '17841475962377751'  # o'z biznes akkauntingiz IDsi
IGSID = '1100419184851307'  # sizga DM yozgan userning IDsi

url = f'https://graph.instagram.com/v23.0/{IG_ID}/messages'

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

payload = {
    "recipient": {
        "id": IGSID
    },
    "message": {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": "Sizga qanday yordam bera olishim mumkin?",
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "https://example.com",
                        "title": "Saytga o‘tish"
                    },
                    {
                        "type": "postback",
                        "title": "Yordam kerak",
                        "payload": "NEED_HELP"
                    }
                ]
            }
        }
    }
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print("✅ Button template yuborildi:", response.json())
else:
    print("❌ Xato:", response.status_code, response.text)