import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ===============================
# Налаштування
# ===============================
BASE_URL = "https://toyota-airport.com.ua"
NEWS_URL = "https://toyota-airport.com.ua/ua/actions/"
LAST_POST_ID_FILE = "last_post_id_toyota_airport.txt"


# ===============================
# Telegram
# ===============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Telegram credentials are not set")


# ===============================
# Робота з last_post_id
# ===============================
def load_last_post_id():
    if not os.path.exists(LAST_POST_ID_FILE):
        return None
    with open(LAST_POST_ID_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_last_post_id(post_id):
    with open(LAST_POST_ID_FILE, "w", encoding="utf-8") as f:
        f.write(post_id)


# ===============================
# Парсинг ВСІ АКЦІЇ (Toyota Airport)
# ===============================
def fetch_latest_action():
    response = requests.get(NEWS_URL, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Вкладка "ВСІ АКЦІЇ"
    all_tab = soup.find("div", id="all")
    if not all_tab:
        raise RuntimeError("Не знайдено вкладку ВСІ АКЦІЇ (id='all')")

    # Перша (найновіша) акція
    first_action = all_tab.find("a", class_="actions__special__offers__box")
    if not first_action:
        raise RuntimeError("Не знайдено жодної акції")

    title_el = first_action.find("p", class_="actions__special-title")
    if not title_el:
        raise RuntimeError("Не знайдено заголовок акції")

    title = title_el.get_text(strip=True)
    relative_url = first_action.get("href")
    full_url = urljoin(BASE_URL, relative_url)

    post_id = relative_url.strip("/").split("/")[-1]

    return {
        "title": title,
        "url": full_url,
        "post_id": post_id
    }


# ===============================
# Надсилання в Telegram
# ===============================
def send_to_telegram(title, url):
    message = (
        "🆕 Нова акція Toyota Airport\n\n"
        f"{title}\n"
        f"{url}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=20
    )
    response.raise_for_status()


# ===============================
# Основна логіка
# ===============================
def main():
    latest = fetch_latest_action()

    print(f"TITLE: {latest['title']}")
    print(f"URL: {latest['url']}")
    print(f"POST_ID: {latest['post_id']}")

    last_post_id = load_last_post_id()

    if latest["post_id"] == last_post_id:
        print("ℹ️ Нових акцій немає, остання вже оброблена")
        return

    print("🆕 Знайдена нова акція!")
    send_to_telegram(latest["title"], latest["url"])
    save_last_post_id(latest["post_id"])
    print("✅ Збережено новий last_post_id")


if __name__ == "__main__":
    main()
