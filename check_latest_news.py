import requests
from bs4 import BeautifulSoup

URL = "https://hyundai-kyiv.com.ua/specialoffers-bogdanauto"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Беремо ПЕРШУ новину
first_news = soup.select_one(".views-field-title a")

if not first_news:
    raise RuntimeError("❌ Не вдалося знайти новини на сторінці")

title = first_news.get_text(strip=True)
link = first_news["href"]

# Якщо лінк відносний — робимо абсолютний
if link.startswith("/"):
    link = "https://hyundai-kyiv.com.ua" + link

print("✅ Знайдено останню спецпропозицію:")
print(title)
print(link)
