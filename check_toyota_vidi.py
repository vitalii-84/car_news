'''

# ===============================
# Toyota VIDI (toyota-ua.com) News Checker
# ===============================

import os
import time
import requests
from bs4 import BeautifulSoup

# ===============================
# Telegram налаштування
# ===============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Telegram credentials are not set")

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=payload, timeout=10)

    if response.ok:
        print("✅ Повідомлення надіслано в Telegram")
    else:
        print("❌ Помилка Telegram:", response.text)


# ===============================
# Сайт Toyota VIDI
# ===============================
URL = "https://toyota-ua.com/ua/actions/"
BASE_URL = "https://toyota-ua.com"
LAST_POST_FILE = "last_post_id_toyota_vidi.txt"


# ===============================
# Отримання HTML з retries
# ===============================
def fetch_page(url, max_retries=3, timeout=30):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Attempt {attempt} to fetch page...")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"⚠️ Attempt {attempt} failed:", e)
            time.sleep(5)

    return None


# ===============================
# Основна логіка
# ===============================
html = fetch_page(URL)

if html is None:
    print("❌ Сайт недоступний")
    exit(0)

soup = BeautifulSoup(html, "html.parser")

# 👉 Вкладка "ВСІ АКЦІЇ" = id="cars"
cars_tab = soup.find("div", id="cars")

if not cars_tab:
    print("❌ Не знайдено вкладку ВСІ АКЦІЇ")
    exit(0)

first_post = cars_tab.find("div", class_="post_card")

if not first_post:
    print("❌ Не знайдено жодної акції")
    exit(0)

# ===============================
# Отримання даних
# ===============================
title_tag = first_post.find("a", class_="post_desc")
link_tag = first_post.find("a", class_="post_card-img")

if not title_tag or not link_tag:
    print("❌ Не вдалося отримати заголовок або посилання")
    exit(0)

post_title = title_tag.text.strip()
post_url = BASE_URL + link_tag["href"]
post_id = link_tag["href"].strip("/").split("/")[-1]

print("TITLE:", post_title)
print("URL:", post_url)
print("POST_ID:", post_id)

# ===============================
# Перевірка last_post_id
# ===============================
last_post_id = None

if os.path.exists(LAST_POST_FILE):
    with open(LAST_POST_FILE, "r") as f:
        last_post_id = f.read().strip()

if post_id == last_post_id:
    print("ℹ️ Новин немає, остання вже оброблена")
else:
    print("🆕 Знайдена нова акція!")
    message = f"{post_title}\n{post_url}"
    send_telegram_message(message)

    with open(LAST_POST_FILE, "w") as f:
        f.write(post_id)

    print("✅ Збережено новий last_post_id")
