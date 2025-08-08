import requests
import json

ACCESS_TOKEN = 'IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3'
IG_ID = '17841475962377751'  # o'z biznes akkauntingiz IDsi
IGSID = '1100419184851307'  # sizga DM yozgan userning IDsi

url = f"https://graph.instagram.com/v23.0/{IG_ID}/messenger_profile?access_token={ACCESS_TOKEN}"

headers = {
    'Content-Type': 'application/json'
}

payload = {
    "platform": "instagram",
    "ice_breakers": [
        {
            "locale": "default",
            "call_to_actions": [
                {
                    "question": "🛍 Nimalar bor?",
                    "payload": "PRODUCTS"
                },
                {
                    "question": "📦 Buyurtma holati?",
                    "payload": "ORDER_STATUS"
                },
                {
                    "question": "💬 Yordam kerak",
                    "payload": "NEED_SUPPORT"
                },
                {
                    "question": "📍 Manzilingiz qayerda?",
                    "payload": "LOCATION"
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print("✅ Ice Breakers muvaffaqiyatli o‘rnatildi:", response.json())
else:
    print("❌ Xatolik:", response.status_code, response.text)