import requests
from datetime import timedelta

ACCESS_TOKEN = "IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3"

url = f"https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={ACCESS_TOKEN}"
res = requests.get(url).json()

print(res)

if "access_token" in res and "expires_in" in res:
    expires_in = res["expires_in"]  # soniyada
    days = expires_in // 86400
    hours = (expires_in % 86400) // 3600
    print(f"Qolgan muddat: {days} kun {hours} soat")
else:
    print("Xatolik yoki noto‘g‘ri token:", res)
