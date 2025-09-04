import requests

# Instagram Graph API ma’lumotlari
ACCESS_TOKEN = "IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3"   # <-- o'zingizning access tokeningizni yozasiz
MEDIA_ID = "17969407511952944"   # <-- kerakli media ID (post/reels/story)

def get_media_insights(media_id, access_token):
    """
    Instagram Media Insights API orqali faqat views, reach, saved, shares olish
    """
    url = f"https://graph.instagram.com/v23.0/{media_id}/insights"
    params = {
        "metric": "views,reach,saved,shares",
        "access_token": access_token
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json().get("data", [])
        # Qulay formatga o‘tkazamiz
        insights = {item["name"]: item["values"][0]["value"] for item in data}
        return insights
    else:
        print("❌ API xato:", response.text)
        return {}

# Test qilish
if __name__ == "__main__":
    result = get_media_insights(MEDIA_ID, ACCESS_TOKEN)
    print("📊 Media Insights natijasi:")
    for metric, value in result.items():
        print(f"{metric}: {value}")
