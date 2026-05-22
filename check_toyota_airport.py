'''

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ===============================
# Налаштування сайту
# ===============================
BASE_URL = "https://toyota-airport.com.ua"
NEWS_URL = "https://toyota-airport.com.ua/ua/actions/"
LAST_POST_FILE = "last_post_id_toyota_airport.txt"

# ===============================
# Telegram
# ===============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_ENABLED = bool(BOT_TOKEN and CHAT_ID)

def send_to_telegram(title: str, url: str):
    """Надсилає повідомлення в Telegram"""
    if not TELEGRAM_ENABLED:
        return

    message = (
        "🆕 Нова акція Toyota Airport\n\n"
        f"{title}\n{url}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )
    response.raise_for_status()
    print("✅ Повідомлення надіслано в Telegram")

# ===============================
# Парсинг останньої акції
# ===============================
def fetch_latest_action():
    response = requests.get(NEWS_URL, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    all_tab = soup.find("div", id="all")
    if not all_tab:
        raise RuntimeError("Не знайдено вкладку ВСІ АКЦІЇ")

    first_action = all_tab.find("a", class_="actions__special__offers__box")
    if not first_action:
        raise RuntimeError("Не знайдено акцій")

    title_el = first_action.find("p", class_="actions__special-title")
    if not title_el:
        raise RuntimeError("Не знайдено заголовок")

    title = title_el.get_text(strip=True)
    relative_url = first_action.get("href")
    full_url = urljoin(BASE_URL, relative_url)

    post_id = relative_url.rstrip("/").split("/")[-1]

    return title, full_url, post_id

# ===============================
# Основна логіка
# ===============================
def main():
    title, url, post_id = fetch_latest_action()

    print("TITLE:", title)
    print("URL:", url)
    print("POST_ID:", post_id)

    # Створюємо файл, якщо його немає
    if not os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
            f.write("")
        print(f"ℹ️ Створено файл {LAST_POST_FILE}")

    # Читаємо попередній post_id
    with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
        last_post_id = f.read().strip()

    if post_id == last_post_id:
        print("ℹ️ Нових акцій немає")
        return

    print("🆕 Знайдена нова акція!")
    send_to_telegram(title, url)

    # Зберігаємо новий post_id
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write(post_id)

    print(f"✅ Збережено новий last_post_id: {post_id}")

if __name__ == "__main__":
    main()
