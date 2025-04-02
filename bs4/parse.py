import requests
from bs4 import BeautifulSoup

# Lấy nội dung từ trang web
response = requests.get('https://books.toscrape.com')

# Kiểm tra nếu request thành công
if response.status_code != 200:
    print('Could not fetch the page')
    exit(1)

print('Successfully fetched the page')

# Parse nội dung HTML bằng BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Tìm tất cả các thẻ <article> chứa thông tin sách
articles = soup.find_all('article')

# Lưu tiêu đề sách vào danh sách
titles = []
for article in articles:
    title = article.h3.a.attrs['title']
    titles.append(title)
    print(title) # In ra tiêu đề sách