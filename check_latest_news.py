# ===============================
# Car News Checker - Telegram notifier
# ===============================

import os
import requests
from bs4 import BeautifulSoup
import time

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
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.ok:
            print("✅ Повідомлення надіслано")
        else:
            print("❌ Помилка Telegram:", response.text)
    except requests.RequestException as e:
        print("❌ Помилка Telegram:", e)


# ===============================
# Налаштування сайту
# ===============================
URL = "https://hyundai-kyiv.com.ua/specialoffers-bogdanauto"
LAST_POST_FILE = "last_post_id.txt"

# ===============================
# Функція для отримання сторінки з retries
# ===============================
def fetch_page(url, max_retries=3, timeout=30):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml"
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
# Основний блок
# ===============================
html = fetch_page(URL)

if html is None:
    print("❌ Сайт недоступний після кількох спроб. Пропускаємо запуск.")
    exit(0)  # Важливо: exit 0, щоб workflow не падав

soup = BeautifulSoup(html, "html.parser")

first_news_div = soup.find("div", class_="views-field-title")
if not first_news_div:
    print("❌ Не вдалося знайти новини на сторінці")
    exit(0)

link_tag = first_news_div.find("a")
if not link_tag or not link_tag.get("href"):
    print("❌ Не вдалося отримати посилання на новину")
    exit(0)

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
    with open(LAST_POST_FILE, "w") as f:
        f.write(post_id)
    print("✅ Збережено новий last_post_id:", post_id)
