from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd


def get_data(url) -> list:
    # Tạo ChromeOptions và chạy trình duyệt ở chế độ headless
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--headless") # Chạy ở chế độ không hiển thị
    browser_options.add_argument("--no-sandbox")
    
    # Khởi động trình duyệt
    driver = webdriver.Chrome(options=browser_options)
    driver.get(url)

    # Nhấp vào danh mục "Humor"
    element = driver.find_element(By.LINK_TEXT, "Humor")
    element.click()

    # Tìm tất cả các sách trên trang
    books = driver.find_elements(By.CSS_SELECTOR, ".product_pod")
    data = []
    for book in books:
        title = book.find_element(By.CSS_SELECTOR, "h3 > a")
        price = book.find_element(By.CSS_SELECTOR, ".price_color")
        stock = book.find_element(By.CSS_SELECTOR, ".instock.availability")
        book_item = {
            'title': title.get_attribute("title"),
            'price': price.text,
            'stock': stock. text
        }
        data.append(book_item)

    # Đóng trình duyệt
    driver.quit()
    return data


def main():
    data = get_data("https://books.toscrape.com/")
    # Lưu vào file CSV
    df = pd.DataFrame(data)
    df.to_csv("books.csv", index=False, encoding="utf-8")

    print("Dữ liệu đã được lưu vào books.csv")


if __name__ == '__main__':
    main()
