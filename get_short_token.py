import requests

# Instagram foydalanuvchi ID'si (Professional yoki Creator account)
IG_USER_ID = "17841475962377751"  # Masalan: 17841400008460056
ACCESS_TOKEN = "IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3"  # Uzoq muddatli access token

def get_media_ids():
    url = f"https://graph.instagram.com/v23.0/{IG_USER_ID}/media"
    params = {
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        media_ids = [item["id"] for item in data.get("data", [])]
        print("📌 Media IDs:")
        for mid in media_ids:
            print(mid)
        return media_ids
    else:
        print("❌ Xatolik:", response.status_code, response.text)
        return []

if __name__ == "__main__":
    get_media_ids()
