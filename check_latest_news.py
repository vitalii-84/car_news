import requests
from bs4 import BeautifulSoup

URL = "https://hyundai-kyiv.com.ua/specialoffers-bogdanauto"
BASE_URL = "https://hyundai-kyiv.com.ua"

response = requests.get(URL, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# знаходимо перший заголовок новини
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
