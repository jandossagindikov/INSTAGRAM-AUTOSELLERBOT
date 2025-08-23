# product_data.py
import json
import os

DATA_FILE = "products.json"

# Agar fayl mavjud bo'lmasa, bo'sh ro'yxat bilan yaratamiz
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def load_products():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def add_product(media_id, image_url, buy_link, details_text, admin_telegram, product_type="post"):
    """
    Yangi post yoki reels qo'shish.
    product_type: 'post' yoki 'reels'
    """
    products = load_products()

    new_product = {
        "media_id": media_id,
        "image_url": image_url,
        "buy_link": buy_link,
        "details": details_text,
        "admin_telegram": admin_telegram,
        "product_type": product_type,
        "stats": {
            "viewers": 0,
            "plus_comments": 0,
            "dm_replies": 0,
            "details_clicks": 0,
            "buy_clicks": 0
        }
    }

    products.append(new_product)
    save_products(products)
    print(f"[INFO] Yangi {product_type} qo‘shildi: {media_id}")

def update_stats(media_id, key, value):
    """
    Statistika yangilash: key bo'yicha qiymatni oshirish yoki o'rnatish.
    key: viewers, plus_comments, dm_replies, details_clicks, buy_clicks
    """
    products = load_products()
    for p in products:
        if p["media_id"] == media_id:
            if isinstance(value, int):
                p["stats"][key] = value
            else:
                p["stats"][key] += 1
            break
    save_products(products)
