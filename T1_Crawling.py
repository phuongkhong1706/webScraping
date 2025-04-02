import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import html
import re  # Thư viện xử lý regex

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.books_db
collection = db.books

BASE_URL = "https://books.toscrape.com/"

def get_categories():
    """Lấy danh sách URL của tất cả thể loại sách từ sidebar"""
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("❌ Không thể truy cập trang chủ")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    categories = []

    for category in soup.select(".side_categories ul li ul li a"):
        category_name = category.text.strip()
        category_url = BASE_URL + category["href"]
        categories.append((category_name, category_url))

    return categories

def clean_text(text):
    """Loại bỏ các ký tự đặc biệt, chỉ giữ lại chữ cái, chữ số và dấu cách"""
    text = html.unescape(text)  # Giải mã HTML entity (&quot; -> ")
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Chỉ giữ lại chữ cái, số và dấu cách
    return text.strip()

def get_book_details(book_url):
    """Lấy thông tin mô tả và thể loại từ trang chi tiết sách"""
    try:
        response = requests.get(book_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Không thể lấy dữ liệu từ {book_url} (HTTP {response.status_code})")
            return {"description": "No description available"}

        soup = BeautifulSoup(response.text, "html.parser")

        # Lấy mô tả sách từ phần Product Description
        description_tag = soup.select_one("meta[name='description']")
        description = description_tag["content"].strip() if description_tag else "No description available"

        # Làm sạch description để loại bỏ ký tự đặc biệt
        description = clean_text(description)

        return {"description": description}

    except requests.exceptions.RequestException as e:
        print(f"🚨 Lỗi khi lấy {book_url}: {e}")
        return {"description": "No description available"}

def crawl_books():
    """Duyệt qua từng thể loại sách và lấy dữ liệu sách từ đó"""
    categories = get_categories()
    if not categories:
        print("❌ Không tìm thấy danh mục nào!")
        return

    for genre, genre_url in categories:
        print(f"📚 Đang quét thể loại: {genre}")

        page = 1
        while True:
            url = genre_url.replace("index.html", f"page-{page}.html") if page > 1 else genre_url
            response = requests.get(url)
            if response.status_code != 200:
                break  # Không còn trang tiếp theo

            soup = BeautifulSoup(response.text, "html.parser")
            books = []

            for article in soup.find_all("article"):
                title = article.h3.a.attrs['title']
                price = article.select_one(".price_color").text.replace('Â', '').replace('£', '').strip()
                rate = article.p.attrs["class"][1]
                
                # Lấy đường dẫn chính xác từ href
                relative_url = article.h3.a.attrs["href"]
                book_url = BASE_URL + "catalogue/" + relative_url.replace("../", "")

                # Chuyển đổi rating từ chữ sang số
                rating_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
                rate = rating_dict.get(rate, 0)

                # Lấy thông tin chi tiết
                details = get_book_details(book_url)

                book = {
                    "title": title,
                    "price": float(price),
                    "rate": float(rate),
                    "genre": genre,
                    "description": details["description"]
                }
                books.append(book)

            if books:
                collection.insert_many(books)
                print(f"✅ Đã lưu {len(books)} sách từ thể loại '{genre}', trang {page}")

            page += 1  # Chuyển sang trang tiếp theo

    print("✅ Hoàn thành quét toàn bộ sách!")

if __name__ == "__main__":
    crawl_books()
