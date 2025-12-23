import os
import requests
from bs4 import BeautifulSoup

# ===============================
# Telegram налаштування
# ===============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Якщо немає токена або chat_id, Telegram буде вимкнено
TELEGRAM_ENABLED = bool(BOT_TOKEN and CHAT_ID)

def send_telegram_message(message: str):
    """Відправка повідомлення в Telegram"""
    if not TELEGRAM_ENABLED:
        print("⚠️ Telegram вимкнено. Повідомлення не буде відправлено.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print("✅ Повідомлення надіслано в Telegram")
    except requests.RequestException as e:
        print("❌ Помилка Telegram:", e)

# ===============================
# Налаштування сайту
# ===============================
URL = "https://cityplaza.toyota.ua/news"
LAST_POST_FILE = "last_post_id_cityplaza.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ===============================
# Завантаження сторінки
# ===============================
try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    print("❌ Не вдалося завантажити сторінку:", e)
    exit(1)

soup = BeautifulSoup(response.text, "html.parser")

# ===============================
# Парсинг першої (найновішої) новини
# ===============================
first_news = soup.find("div", class_="news-item-info-")
if not first_news:
    print("❌ Не знайдено новини на сторінці")
    exit(0)

link_tag = first_news.find("a", class_="news-item-title-")
if not link_tag or not link_tag.get("href"):
    print("❌ Не знайдено посилання на новину")
    exit(0)

title = link_tag.text.strip()
relative_url = link_tag["href"]
full_url = "https://cityplaza.toyota.ua" + relative_url
post_id = relative_url.rstrip("/").split("/")[-1]

# ===============================
# Перевірка last_post_id
# ===============================
# Створюємо файл, якщо його немає
if not os.path.exists(LAST_POST_FILE):
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write("")  # порожній файл

# Зчитування last_post_id з файлу
with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
    last_post_id = f.read().strip()

# ===============================
# Логіка перевірки новизни
# ===============================
if post_id == last_post_id:
    print("ℹ️ Новин немає, остання вже оброблена")
    exit(0)  # Немає нових новин, завершуємо виконання

# ===============================
# Знайдено нову новину
# ===============================
print("🆕 Знайдена нова новина!")
print("TITLE:", title)
print("URL:", full_url)

# Відправка повідомлення в Telegram
message = f"{title}\n{full_url}"
send_telegram_message(message)

# Збереження нового last_post_id у файл
with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
    f.write(post_id)

print("✅ Збережено новий last_post_id:", post_id)
