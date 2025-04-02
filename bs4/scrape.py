import requests

# URL của trang web cần scrape
response = requests.get('https://books.toscrape.com')

# Kiểm tra nếu request thành công
if response.status_code != 200:
    print('Could not fetch the page')
    exit(1)

print('Successfully fetched the page')