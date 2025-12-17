import os
import requests
from bs4 import BeautifulSoup

# ===============================
# Telegram налаштування
# ===============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("⚠️ Telegram credentials не задані, повідомлення не будуть відправлені")
    send_telegram = False
else:
    send_telegram = True

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.ok:
            print("✅ Повідомлення надіслано в Telegram")
        else:
            print("❌ Помилка Telegram:", response.text)
    except requests.RequestException as e:
        print("❌ Помилка Telegram:", e)

# ===============================
# Налаштування сайту
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

# ===============================
# Завантаження сторінки
# ===============================
response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# ===============================
# Парсинг першої новини
# ===============================
first_news = soup.find("div", class_="news-item-info-")
if not first_news:
    print("❌ Не знайдено новини")
    exit(0)

link_tag = first_news.find("a", class_="news-item-title-")
if not link_tag or not link_tag.get("href"):
    print("❌ Не знайдено посилання")
    exit(0)

title = link_tag.text.strip()
relative_url = link_tag["href"]
url = "https://cityplaza.toyota.ua" + relative_url
post_id = relative_url.split("/")[-1]

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
    message = f"{title}\n{url}"

    print("🆕 Знайдена нова новина!")
    print("TITLE:", title)
    print("URL:", url)

    # Відправка Telegram, якщо налаштовано
    if send_telegram:
        send_telegram_message(message)

    # Збереження нового last_post_id
    with open(LAST_POST_FILE, "w") as f:
        f.write(post_id)

    print("✅ Збережено новий last_post_id")
