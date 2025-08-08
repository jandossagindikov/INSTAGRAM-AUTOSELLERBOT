import requests

# ⚠️ O'zingizning ma'lumotlaringizni shu yerga joylashtiring
short_lived_access_token = 'EAACEdEose0...'  # bu siz oldin olgan token
client_secret = 'a1b2C3D4'  # bu sizning app secret'ingiz

# So‘rov yuboriladi
url = 'https://graph.instagram.com/access_token'

params = {
    'grant_type': 'ig_exchange_token',
    'client_secret': "5e9d794f76127981511c8aec49679a6d",
    'access_token': 'IGAAKzD8pKL9FBZAE1ZAdVo3ek5WQjFCdjBvRFRPMWZAEeUhvTFprallWUGw2TmlobENRODVwQWdiVF9kU3lldi1DTkNpMk9QUEloVFAtcEUtbDF0akw4ZAk1kODhEZA2k5U09fdFczY19aR0Vmb0FZAU0dleHFPUDF3M2lTQWl0ZADcwa1FhdEVpRTNTRkUwaE1KY0xqdU5ycW5B',
}

response = requests.get(url, params=params)

# Natijani tekshiramiz
if response.status_code == 200:
    data = response.json()
    print("✅ Long-lived access token:")
    print("Access Token:", data.get('access_token'))
    print("Token Type:", data.get('token_type'))
    print("Expires In (seconds):", data.get('expires_in'))
else:
    print("❌ Xatolik yuz berdi:")
    print(response.status_code)
    print(response.text)
