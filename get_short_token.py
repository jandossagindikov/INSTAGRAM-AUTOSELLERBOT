import requests

# Bu ma'lumotlarni o'zingiznikiga moslang:
CLIENT_ID = "759830353162193"
CLIENT_SECRET = "5e9d794f76127981511c8aec49679a6d"
REDIRECT_URI = "https://e90c897709f8.ngrok-free.app/callback"
CODE = "AQCIEfeFf7FRcFMpMQRBZ8oRY_tOoGkD48-jqUJuCEJO8xfQ3iWN7hrNt-6_PBa246EE2sW3fuacr5THRhVIHsudiImB7JM6J2kgtHBZZkh6aXLZdRhUI2l2eGdMLZHwEs163YegWtWLkZQ2O_HfYmJZCWzfncvBcjKv7Yigs0GY8Y2FBrWb5Bllyfb-Vt-whe-TcT6Dhu-7Sw6jtvhjHBMUtIPD0utUxxdcwWYkagvZ1Q"  # Instagram qaytargan code ni bu yerga yozing

url = "https://api.instagram.com/oauth/access_token"

data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code": CODE
}

response = requests.post(url, data=data)

# Natijani chiqaramiz
print("Status:", response.status_code)
print("Javob:", response.json())
