import os
import requests
from bs4 import BeautifulSoup

# ===============================
# Telegram
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
    response.raise_for_status()

# ===============================
# Site settings
# ===============================
URL = "https://cityplaza.toyota.ua/news"
LAST_POST_FILE = "last_post_id_cityplaza.txt"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

first_news = soup.find("div", class_="news-item-info-")
if not first_news:
    print("❌ Не знайдено новини")
    exit(0)

link_tag = first_news.find("a", class_="news-item-title-")
if not link_tag or not link_tag.get("href"):
    print("❌ Посилання відсутнє")
    exit(0)

title = link_tag.text.strip()
relative_url = link_tag["href"]
url = "https://cityplaza.toyota.ua" + relative_url
post_id = relative_url.split("/")[-1]

# ===============================
# last_post_id check
# ===============================
last_post_id = None
if os.path.exists(LAST_POST_FILE):
    with open(LAST_POST_FILE, "r") as f:
        last_post_id = f.read().strip()

if post_id == last_post_id:
    print("ℹ️ Новин немає")
else:
    message = f"{title}\n{url}"
    send_telegram_message(message)

    with open(LAST_POST_FILE, "w") as f:
        f.write(post_id)

    print("✅ Надіслано в Telegram та збережено last_post_id")
