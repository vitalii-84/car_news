import requests
from bs4 import BeautifulSoup
import os
import urllib3

# ================== Налаштування ==================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://toyota.com.ua/promos/'
LAST_FILE = 'last_post_id_toyota_avtosamit.txt'
# ===================================================

# Вимикаємо warning для unverified HTTPS request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_telegram(message):
    # Використовуємо простий запит через Telegram API
    requests.get(
        f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
        params={'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    )

def get_latest_news():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    r = requests.get(URL, headers=headers, verify=False)  # verify=False через проблеми з сертифікатом
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Перший блок новини
    first_news = soup.select_one('.news-grid-item-new')
    if not first_news:
        return None, None
    
    title_tag = first_news.select_one('.news-grid-item__heading')
    link_tag = first_news.select_one('.btn-more')
    
    if not title_tag or not link_tag:
        return None, None
    
    title = title_tag.text.strip()
    href = link_tag.get('href').strip()
    
    # Додаємо домен, якщо посилання відносне
    if not href.startswith('http'):
        href = 'https://toyota.com.ua/' + href.lstrip('/')
    
    return title, href

def read_last():
    if not os.path.exists(LAST_FILE):
        return ''
    with open(LAST_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def write_last(text):
    with open(LAST_FILE, 'w', encoding='utf-8') as f:
        f.write(text)

def main():
    title, link = get_latest_news()
    if not title or not link:
        print("Не вдалося знайти новини.")
        return
    
    last = read_last()
    if title != last:
        message = f"{title}\n{link}"
        send_telegram(message)
        write_last(title)
        print("Надіслано нову акцію:", title)
    else:
        print("Немає нових акцій.")

if __name__ == '__main__':
    main()
