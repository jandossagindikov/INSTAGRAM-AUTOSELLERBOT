from flask import Flask, request, render_template, redirect
import requests
import json
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from products import products
from datetime import datetime, timedelta, timezone

# Tashkent tz (ZoneInfo mavjud bo'lmasa, UTC+5 bilan ishlayveradi)
try:
    from zoneinfo import ZoneInfo
    TASHKENT_TZ = ZoneInfo("Asia/Tashkent")
except Exception:
    TASHKENT_TZ = timezone(timedelta(hours=5))

app = Flask(__name__)

# --- Config ---
VERIFY_TOKEN = "myverifytoken123"
ACCESS_TOKEN = "IGAAKzD8pKL9FBZAE1YdUlDRms5NjZADNDhfdktIbGFZARHR4cnVKWEhRRlNQWTNXS1pFNGpqMThaMkUxelFRRURncUI0ZAjA1WGU3ajdOcjM1em1RQ1RYMXZAZAQ2NsdUJrU3pLZAzBMNVltWDNKVGlYYUtjekV3"
TOKEN_EXPIRES_AT = time.time() + 60*24*3600
APP_USERS_IG_ID = "17841475962377751"
API_VERSION = "v23.0"
API_BASE = "https://graph.instagram.com"  # (mavjud loyihangga mos qoldirdim)
admin_telegram = "https://t.me/shopwithuzummarket"

# === PostgreSQL ulanish ===
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jandos:DMgvx8yeBT2OcAsrYUgMCTpan68LPo4x@dpg-d2ljl5h5pdvs73aqbqp0-a.frankfurt-postgres.render.com/monitoringlist")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Jadval yaratish (bir marta ishlaydi)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Asl counts jadvali (saqlab qolamiz)
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
    # YANGI: har bir post (media_id) uchun "plus" yozgan foydalanuvchini alohida saqlaymiz
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plus_authors (
        media_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        first_commented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        dm_sent BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (media_id, user_id)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

# === Mahsulotlar ro‘yxati importdan keladi ===

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

def get_unique_plus_count(media_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM plus_authors WHERE media_id = %s;", (media_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return (row or {}).get("c", 0)

def get_counts(media_id):
    """
    plus_count endi counts jadvalidan emas, plus_authors dan olinadi (noyob odamlar soni).
    Qolganlari counts jadvalidan.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT read_count, buy_clicks, contact_clicks FROM counts WHERE media_id = %s", (media_id,))
    row = cur.fetchone() or {}
    cur.close()
    conn.close()
    return {
        "plus_count": get_unique_plus_count(media_id),
        "read_count": row.get("read_count", 0),
        "buy_clicks": row.get("buy_clicks", 0),
        "contact_clicks": row.get("contact_clicks", 0),
    }

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

# --- Yangi helperlar: '+' yozgan noyob userni ro'yxatga olish va DM holatini boshqarish
def record_plus_user(media_id, user_id):
    """
    return: (is_new_user, need_dm)
    - Agar user birinchi marta '+' yozsa: yozib qo'yamiz (dm_sent=False), counts.plus_count ni ham +1 qilamiz.
    - Agar user mavjud-u dm_sent=False bo'lsa: DM yuborish kerak (need_dm=True).
    - Agar user mavjud va dm_sent=True bo'lsa: DM yubormaymiz.
    """
    if not user_id:
        # user_id bo'lmasa, deduplikatsiya qila olmaymiz — bitta marta DM yuborishga ruxsat beramiz
        return (False, True)

    conn = get_db_connection()
    cur = conn.cursor()
    # Tekshir
    cur.execute("""
        SELECT dm_sent FROM plus_authors WHERE media_id = %s AND user_id = %s;
    """, (media_id, user_id))
    row = cur.fetchone()
    if row is None:
        # Yangi foydalanuvchi
        cur.execute("""
            INSERT INTO plus_authors (media_id, user_id, dm_sent)
            VALUES (%s, %s, %s);
        """, (media_id, user_id, False))
        # Noyob odamlar soni statistikasi uchun counts.plus_count ni oshirib qo'yamiz
        cur.execute("""
            INSERT INTO counts (media_id, plus_count)
            VALUES (%s, 1)
            ON CONFLICT (media_id) DO UPDATE SET plus_count = counts.plus_count + 1;
        """, (media_id,))
        conn.commit()
        cur.close()
        conn.close()
        return (True, True)  # yangi va DM yuborish kerak
    else:
        dm_sent = row["dm_sent"]
        cur.close()
        conn.close()
        if dm_sent:
            return (False, False)  # allaqachon DM yuborilgan
        else:
            return (False, True)   # hali DM yuborilmagan — yuboramiz

def mark_dm_sent(media_id, user_id):
    if not user_id:
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE plus_authors SET dm_sent = TRUE
        WHERE media_id = %s AND user_id = %s;
    """, (media_id, user_id))
    conn.commit()
    cur.close()
    conn.close()

# === Instagram helpers ===
def get_media_insights(media_id, access_token):
    url = f"{API_BASE}/v23.0/{media_id}/insights"
    params = {"metric": "views,reach,saved,shares", "access_token": access_token}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json().get("data", [])
        return {item["name"]: item["values"][0]["value"] for item in data}
    return {}

def get_media_info(media_id, access_token):
    url = f"{API_BASE}/{API_VERSION}/{media_id}"
    params = {
        "fields": "id,media_type,media_url,timestamp",
        "access_token": access_token
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()
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
        ACCESS_TOKEN, TOKEN_EXPIRES_AT = refresh_long_lived_token(ACCESS_TOKEN)
    return ACCESS_TOKEN

def get_base_domain():
    try:
        return request.host_url.rstrip("/")
    except RuntimeError:
        return "http://localhost:5000"

# --- Yordamchi: komment muallifini olish (webhookda kelmasa)
def get_comment_author_id(comment_id, access_token):
    # Mavjud API bo'yicha: /{comment_id}?fields=from{id,username}
    try:
        url = f"{API_BASE}/{API_VERSION}/{comment_id}"
        params = {"fields": "from{id,username}", "access_token": access_token}
        r = requests.get(url, params=params)
        if r.status_code == 200:
            data = r.json()
            frm = data.get("from") or {}
            return frm.get("id") or None
    except Exception:
        pass
    return None

# === Monitoring page ===
@app.route('/')
def monitoring():
    token = get_access_token()
    monitoring_data = []
    for idx, product in enumerate(products, start=1):
        insights = get_media_insights(product["media_id"], token)
        counts = get_counts(product["media_id"])
        media_info = get_media_info(product["media_id"], token)

        # timestamp -> Tashkent vaqti
        raw_time = media_info.get("timestamp")
        if raw_time:
            try:
                # IG timestamp odatda UTC bo'ladi, masalan: 2025-09-05T11:22:33+0000 yoki +00:00
                # Har ikkisini ham qo'llab-quvvatlash uchun almashtiramiz
                iso = raw_time.replace("+0000", "+00:00")
                dt = datetime.fromisoformat(iso)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                dt_tash = dt.astimezone(TASHKENT_TZ)
                formatted_time = dt_tash.strftime("%Y-%m-%d %H:%M")
            except Exception:
                formatted_time = raw_time
        else:
            formatted_time = "-"

        monitoring_data.append({
            "num": idx,
            "media_id": product["media_id"],
            "media_url": product["media_url"],
            "views": insights.get("views", 0),
            "reach": insights.get("reach", 0),
            "shares": insights.get("shares", 0),
            "saved": insights.get("saved", 0),
            "plus_comments": counts["plus_count"],  # endi noyob odamlar soni
            "read_dm": counts["read_count"],
            "buy_clicks": counts["buy_clicks"],
            "aloqa_clicks": counts["contact_clicks"],
            "timestamp": formatted_time
        })
    return render_template("index.html", monitoring_data=monitoring_data)

# === Click tracking ===
@app.route('/click/<action>/<media_id>')
def track_click(action, media_id):
    product = get_product_by_media_id(media_id)
    if not product:
        return "Not found", 404

    if action == "buy":
        increment_count(media_id, "buy_clicks")

        product_url = product["buy_link"]
        product_id = None
        if "product/" in product_url:
            product_id = product_url.split("product/")[1].split("?")[0]

        ua = request.headers.get("User-Agent", "").lower()
        if product_id and ("android" in ua or "iphone" in ua):
            return redirect(f"uzum://product/{product_id}")
        else:
            return redirect(product_url)

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

    data = request.json or {}
    token = get_access_token()
    try:
        entry = (data.get("entry") or [])[0]

        # Comments o'zgarishlari
        for change in entry.get("changes", []):
            if change.get("field") == "comments":
                comment_data = change.get("value", {})
                comment_id = comment_data.get("id")
                comment_text = (comment_data.get("text") or "").strip()

                media_info = comment_data.get("media", {})
                media_type = media_info.get("media_product_type", "")
                if media_type == "AD":
                    media_id = media_info.get("original_media_id")
                else:
                    media_id = media_info.get("id")

                # Komment muallifi (har xil payloadlarda nomi farq qilishi mumkin)
                user_id = None
                frm = comment_data.get("from") or {}
                user_id = frm.get("id") or comment_data.get("user_id") or comment_data.get("sender_id")

                # Agar webhookda kelmasa, API orqali aniqlab olamiz
                if not user_id and comment_id:
                    user_id = get_comment_author_id(comment_id, token)

                # Faqat faqat '+' belgilaridan iborat bo'lsa ishlaymiz
                if comment_text and set(comment_text) == {"+"} and media_id and comment_id:
                    # Noyob userni tekshiramiz
                    _, need_dm = record_plus_user(media_id, user_id)

                    if need_dm:
                        # Komment ostiga reply
                        reply_to_comment(comment_id, "Directni tekshiring 👀", token)
                        # DM yuborish
                        ok, mid = send_private_reply(comment_id, get_product_by_media_id(media_id), media_id, token)
                        # Muvaffaqiyatli bo'lsa, shu user uchun dm_sent=True qilamiz
                        if ok and user_id:
                            mark_dm_sent(media_id, user_id)

        # DM read eventlari uchun
        for msg in entry.get("messaging", []):
            if "read" in msg:
                mid = msg["read"].get("mid")
                if mid:
                    media_id = get_mapping(mid)
                    if media_id:
                        increment_count(media_id, "read_count")

    except Exception as e:
        print("❌ Webhook error:", e)
    return "OK", 200

def reply_to_comment(comment_id, message, access_token):
    url = f"{API_BASE}/{comment_id}/replies"
    try:
        requests.post(url, json={"message": message, "access_token": access_token}, timeout=10)
    except Exception as e:
        print("reply_to_comment error:", e)

def send_private_reply(comment_id, product, media_id, access_token):
    """
    return: (ok, message_id_or_None)
    """
    if not product:
        return (False, None)
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
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            mid = r.json().get("message_id")
            if mid:
                set_mapping(mid, media_id)
            return (True, mid)
        else:
            print("send_private_reply status:", r.status_code, r.text)
            return (False, None)
    except Exception as e:
        print("send_private_reply error:", e)
        return (False, None)

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)
