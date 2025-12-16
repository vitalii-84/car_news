import requests
from bs4 import BeautifulSoup

URL = "https://hyundai-kyiv.com.ua/specialoffers-bogdanauto"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()  # перевірка, що сторінка доступна

soup = BeautifulSoup(response.text, "html.parser")

# Знаходимо перший блок з новиною
first_news = soup.find("div", class_="views-field views-field-title")
link_tag = first_news.find("a")
news_title = link_tag.text.strip()
news_url = "https://hyundai-kyiv.com.ua" + link_tag['href']

print(news_title)
print(news_url)
