import requests
from bs4 import BeautifulSoup

URL = "https://hyundai-kyiv.com.ua/specialoffers-bogdanauto"
BASE_URL = "https://hyundai-kyiv.com.ua"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
}


response = requests.get(
    URL,
    headers=headers,
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

news_div = soup.find("div", class_="views-field views-field-title")
if not news_div:
    raise RuntimeError("Не вдалося знайти новини на сторінці")

link = news_div.find("a")
if not link:
    raise RuntimeError("Не вдалося знайти посилання на новину")

title = link.get_text(strip=True)
relative_url = link.get("href")
full_url = BASE_URL + relative_url

print("Заголовок:", title)
print("Посилання:", full_url)
