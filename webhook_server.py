from flask import Flask, request, render_template, redirect
import requests
import json
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# --- Config ---
VERIFY_TOKEN = "myverifytoken123"
APP_USERS_IG_ID = "17841475962377751"
API_VERSION = "v23.0"
API_BASE = "https://graph.instagram.com"
admin_telegram = "https://t.me/sagindikov_04"

# === Global tokenlar ===
ACCESS_TOKEN = None
TOKEN_EXPIRES_AT = 0

# === PostgreSQL ulanish ===
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://jandos:DMgvx8yeBT2OcAsrYUgMCTpan68LPo4x@dpg-d2ljl5h5pdvs73aqbqp0-a.frankfurt-postgres.render.com/monitoringlist"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Jadval yaratish (bir marta ishlaydi)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS counts (
        media_id TEXT PRIMARY KEY,
        plus_count INTEGER DEFAULT 0,
        read_count INTEGER DEFAULT 0,
        buy_clicks INTEGER DEFAULT 0,
        contact_clicks INTEGER DEFAULT 0
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS message_map (
        mid TEXT PRIMARY KEY,
        media_id TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS access_tokens (
        id SERIAL PRIMARY KEY,
        token TEXT NOT NULL,
        expires_at BIGINT
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

# === Access token DB helpers ===
def save_access_token(new_token, expires_at):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM access_tokens;")  # faqat 1ta token saqlanadi
    cur.execute("INSERT INTO access_tokens (token, expires_at) VALUES (%s, %s);",
                (new_token, int(expires_at)))
    conn.commit()
    cur.close()
    conn.close()

def load_access_token():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT token, expires_at FROM access_tokens ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row["token"], row["expires_at"]
    return None, 0

# === Mahsulotlar ro‘yxati ===
products = [
    {
        "media_id": "17991437924683241",
        "media_url": "https://www.instagram.com/reel/DNNj6RSP7_t/",
        "buy_link": "https://uzum.uz/uz/product/rasshiritel-dlya-nosa-oq---5-1660905?skuId=5662019",
        "image_url": "https://images.uzum.uz/d0e434i7s4fo7mq89ujg/original.jpg",
        "title": "Burun kengaytirgich"
    },
    {
        "media_id": "18137348917428416",
        "media_url": "https://www.instagram.com/p/DNlU4nwqe39/?img_index=1",
        "buy_link": "https://uzum.uz/uz/product/windows-ornatilgan-ofis-metall-kulrang---291-1694031?skuId=5780830",
        "image_url": "https://images.uzum.uz/d24ccst2lln1ps3bs800/original.jpg",
        "title": "iTech noutbuki"
    }
]

# === Helper: productni media_id orqali topish ===
def get_product_by_media_id(media_id):
    for product in products:
        if product["media_id"] == media_id:
            return product
    return None

# === DB helpers ===
def increment_count(media_id, field):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO counts (media_id, {field})
        VALUES (%s, 1)
        ON CONFLICT (media_id) DO UPDATE SET {field} = counts.{field} + 1;
    """, (media_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_counts(media_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM counts WHERE media_id = %s", (media_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row
    else:
        return {"plus_count": 0, "read_count": 0, "buy_clicks": 0, "contact_clicks": 0}

def set_mapping(mid, media_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO message_map (mid, media_id)
        VALUES (%s, %s)
        ON CONFLICT (mid) DO UPDATE SET media_id = EXCLUDED.media_id;
    """, (mid, media_id))
    conn.commit()
    cur.close()
    conn.close()

def get_mapping(mid):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT media_id FROM message_map WHERE mid = %s", (mid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["media_id"] if row else None

# === Instagram helpers ===
def get_media_insights(media_id, access_token):
    url = f"{API_BASE}/{API_VERSION}/{media_id}/insights"
    params = {"metric": "views,reach,saved,shares", "access_token": access_token}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json().get("data", [])
        return {item["name"]: item["values"][0]["value"] for item in data}
    return {}

def refresh_long_lived_token(current_token):
    url = f"{API_BASE}/refresh_access_token"
    params = {"grant_type": "ig_refresh_token", "access_token": current_token}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        return data.get("access_token"), time.time() + data.get("expires_in")
    return current_token, None

def get_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRES_AT
    if time.time() > TOKEN_EXPIRES_AT - 24*3600:
        new_token, new_exp = refresh_long_lived_token(ACCESS_TOKEN)
        if new_token and new_exp:
            ACCESS_TOKEN, TOKEN_EXPIRES_AT = new_token, new_exp
            save_access_token(ACCESS_TOKEN, TOKEN_EXPIRES_AT)
    return ACCESS_TOKEN

def get_base_domain():
    try:
        return request.host_url.rstrip("/")
    except RuntimeError:
        return "http://localhost:5000"

# === Monitoring page ===
@app.route('/')
def monitoring():
    token = get_access_token()
    monitoring_data = []
    for idx, product in enumerate(products, start=1):
        insights = get_media_insights(product["media_id"], token)
        counts = get_counts(product["media_id"])
        monitoring_data.append({
            "num": idx,
            "media_id": product["media_id"],
            "media_url": product["media_url"],
            "views": insights.get("views", 0),
            "reach": insights.get("reach", 0),
            "shares": insights.get("shares", 0),
            "saved": insights.get("saved", 0),
            "plus_comments": counts["plus_count"],
            "read_dm": counts["read_count"],
            "buy_clicks": counts["buy_clicks"],
            "aloqa_clicks": counts["contact_clicks"]
        })
    return render_template("index.html", monitoring_data=monitoring_data)

# === Click tracking ===
@app.route('/click/<action>/<media_id>')
def track_click(action, media_id):
    if action == "buy":
        increment_count(media_id, "buy_clicks")
        return redirect(get_product_by_media_id(media_id)["buy_link"])
    elif action == "contact":
        increment_count(media_id, "contact_clicks")
        return redirect(admin_telegram)
    return "Not found", 404

# === Webhook ===
@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    data = request.json
    token = get_access_token()
    try:
        entry = data["entry"][0]
        for change in entry.get("changes", []):
            if change.get("field") == "comments":
                comment_data = change["value"]
                comment_id = comment_data["id"]
                comment_text = comment_data["text"].strip()
                media_id = comment_data["media"]["id"]
                if comment_text == "+":
                    increment_count(media_id, "plus_count")
                    product = get_product_by_media_id(media_id)
                    if product:
                        reply_to_comment(comment_id, "Directni tekshiring 👀", token)
                        send_private_reply(comment_id, product, media_id, token)
        for msg in entry.get("messaging", []):
            if "read" in msg:
                mid = msg["read"]["mid"]
                media_id = get_mapping(mid)
                if media_id:
                    increment_count(media_id, "read_count")
    except Exception as e:
        print("❌ Webhook error:", e)
    return "OK", 200

def reply_to_comment(comment_id, message, access_token):
    url = f"{API_BASE}/{comment_id}/replies"
    requests.post(url, json={"message": message, "access_token": access_token})

def send_private_reply(comment_id, product, media_id, access_token):
    url = f"{API_BASE}/{API_VERSION}/{APP_USERS_IG_ID}/messages"
    headers = {"Content-Type":"application/json","Authorization":f"Bearer {access_token}"}
    base_url = get_base_domain()
    payload = {
        "recipient":{"comment_id":comment_id},
        "message":{"attachment":{
            "type":"template",
            "payload":{"template_type":"generic","elements":[
                {"title":product["title"],
                 "image_url":product["image_url"],
                 "subtitle":"Mahsulotimizni xarid qilishni istaysizmi?",
                 "buttons":[
                     {"type":"web_url","url":f"{base_url}/click/buy/{media_id}","title":"Do‘konga o‘tish"},
                     {"type":"web_url","url":f"{base_url}/click/contact/{media_id}","title":"Aloqa"}
                 ]}
            ]}
        }}
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        mid = r.json().get("message_id")
        if mid:
            set_mapping(mid, media_id)

# === App init (Render uchun muhim!) ===
@app.before_first_request
def setup_app():
    global ACCESS_TOKEN, TOKEN_EXPIRES_AT
    init_db()
    ACCESS_TOKEN, TOKEN_EXPIRES_AT = load_access_token()
    if not ACCESS_TOKEN:
        ACCESS_TOKEN = "IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3"
        TOKEN_EXPIRES_AT = int(time.time()) + 60*24*3600
        save_access_token(ACCESS_TOKEN, TOKEN_EXPIRES_AT)

# === Main ===
if __name__ == '__main__':
    app.run(port=5000, debug=True)
