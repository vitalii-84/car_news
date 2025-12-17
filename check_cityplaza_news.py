import requests
from bs4 import BeautifulSoup

URL = "https://cityplaza.toyota.ua/news"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

html = response.text
soup = BeautifulSoup(html, "html.parser")

# 1️⃣ знаходимо перший контейнер новини
first_news = soup.find("div", class_="news-item-info-")

if not first_news:
    print("❌ Не знайдено жодної новини")
    exit()

# 2️⃣ знаходимо посилання
link_tag = first_news.find("a", class_="news-item-title-")

if not link_tag or not link_tag.get("href"):
    print("❌ Не знайдено посилання")
    exit()

title = link_tag.text.strip()
relative_url = link_tag["href"]
url = "https://cityplaza.toyota.ua" + relative_url
post_id = relative_url.split("/")[-1]

print("TITLE:", title)
print("URL:", url)
print("POST_ID:", post_id)
