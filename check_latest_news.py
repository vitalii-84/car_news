# ===============================
# Car News Checker - Telegram notifier
# ===============================

import os
import requests
from bs4 import BeautifulSoup

# ===============================
# Налаштування Telegram
# ===============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Telegram credentials are not set in environment variables")


def send_telegram_message(message: str):
    """Відправка повідомлення в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.ok:
        print("✅ Повідомлення надіслано")
    else:
        print("❌ Помилка Telegram:", response.text)


# ===============================
# Налаштування сайту
# ===============================
URL = "https://hyundai-kyiv.com.ua/specialoffers-bogdanauto"
LAST_POST_FILE = "last_post_id.txt"

# ===============================
# Отримання останньої новини
# ===============================
try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()
except requests.RequestException as e:
    print("❌ Помилка при отриманні сторінки:", e)
    exit(1)

soup = BeautifulSoup(response.text, "html.parser")

# Перевірка першого елемента
first_news_div = soup.find("div", class_="views-field-title")
if not first_news_div:
    print("❌ Не вдалося знайти новини на сторінці")
    exit(1)

link_tag = first_news_div.find("a")
if not link_tag or not link_tag.get("href"):
    print("❌ Не вдалося отримати посилання на новину")
    exit(1)

post_url = "https://hyundai-kyiv.com.ua" + link_tag["href"]
post_title = link_tag.text.strip()
post_id = link_tag["href"].split("/")[-1]

# ===============================
# Перевірка останнього збереженого поста
# ===============================
last_post_id = None
if os.path.exists(LAST_POST_FILE):
    with open(LAST_POST_FILE, "r") as f:
        last_post_id = f.read().strip()

if post_id == last_post_id:
    print("ℹ️ Новин немає, остання вже відправлена")
else:
    message = f"{post_title}\n{post_url}"
    send_telegram_message(message)
    # Зберігаємо новий останній пост
    with open(LAST_POST_FILE, "w") as f:
        f.write(post_id)
    print("✅ Збережено новий last_post_id:", post_id)
