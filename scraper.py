import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

BASE_URL = "https://books.toscrape.com/catalogue/"
OUTPUT_DIR = 'data'


RATTING_MAP = {
    "One":1, "Two":2, "Three":3, "Four":4, "Five":5
}

def get_books(page_url):
    response = requests.get(page_url, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    
    books = []
    for article in soup.select("article.product_pod"):
        title = article.h3.a['title']
        price = article.select_one('p.price_color').text.strip()
        rating_word = article.p['class'][1]
        rating = RATTING_MAP.get(rating_word, 0)
        availability = article.select_one("p.availability").text.strip()
        
        books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
        })
    return books

def get_next_page(page_url, soup):
    """次のページのURLを返す。なければ None"""
    next_btn = soup.select_one("li.next a")
    if next_btn:
        return BASE_URL + next_btn["href"]
    return None


def scrape_all(max_pages=5):
    """全ページをスクレイピングして全書籍データを返す"""
    url = BASE_URL + "page-1.html"
    all_books = []
    page_num = 1

    while url and page_num <= max_pages:
        print(f"取得中: ページ {page_num} - {url}")
        response = requests.get(url, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        all_books.extend(get_books(url))
        url = get_next_page(url, soup)
        page_num += 1

    return all_books


def save_to_csv(books):
    """日付付きのCSVファイルに保存する"""
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(OUTPUT_DIR, f"books_{today}.csv")

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=["title", "price", "rating", "availability"]
        )
        writer.writeheader()
        writer.writerows(books)

    print(f"保存完了: {filename} ({len(books)}件)")
    return filename


def main():
    print(f"スクレイピング開始: {datetime.now()}")
    books = scrape_all(max_pages=5)
    save_to_csv(books)
    print("完了!")


if __name__ == "__main__":
    main()
        
        
        