import requests
from datetime import datetime, timedelta

# Instagram foydalanuvchi ID'si (Professional yoki Creator account)
IG_USER_ID = "17841475962377751"
ACCESS_TOKEN = "IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3"


def check_long_lived_token():
    """Long-lived token muddati qancha qolganini chiqarish"""
    url = "https://graph.instagram.com/refresh_access_token"
    params = {
        "grant_type": "ig_refresh_token",
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        expires_in = data.get("expires_in")  # sekundlarda
        expiry_date = datetime.now() + timedelta(seconds=expires_in)
        print(f"⏳ Token tugash sanasi: {expiry_date}")
        print(f"📌 Qolgan vaqt: {expires_in // 86400} kun {(expires_in % 86400) // 3600} soat")
    else:
        print("❌ Tokenni tekshirishda xatolik:", response.status_code, response.text)


def get_media_ids():
    """Media ID lar va sanasini chiqarish"""
    url = f"https://graph.instagram.com/v23.0/{IG_USER_ID}/media"
    params = {
        "fields": "id,timestamp",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        media_items = data.get("data", [])
        print("📌 Media IDs va sanalari:")
        for item in media_items:
            mid = item["id"]
            timestamp = item.get("timestamp", "sana yo‘q")
            print(f"{mid} | {timestamp}")
        return [item["id"] for item in media_items]
    else:
        print("❌ Xatolik:", response.status_code, response.text)
        return []


if __name__ == "__main__":
    check_long_lived_token()
    get_media_ids()
