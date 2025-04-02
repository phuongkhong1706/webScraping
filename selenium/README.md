# Web Scraping with Python Selenium

- [Web Scraping with Python Selenium](#web-scraping-with-python-selenium)
  - [Docs: Tutorial](#docs-tutorial)
  - [Installing Selenium](#installing-selenium)
  - [Scraping with Selenium](#scraping-with-selenium)

In this article, we’ll cover an overview of web scraping with Selenium using a real-life example.

## Docs: [Tutorial](https://www.scrapingbee.com/blog/selenium-python/)

## Installing Selenium

1. Create a virtual environment:

```sh
python3 -m venv .env
source venv/bin/activate
```

2. Install Selenium using pip:

```sh
pip install Basic/WebScraping/selenium/requirements.txt
```


## Scraping with Selenium

Import required modules as follows:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
```

Add the skeleton of the script as follows:

```python
def get_data(url) -> list:
   ...


def main():
    ...

if __name__ == '__main__':
    main()
```

Create ChromeOptions object and set `headless` to `True`. Use this to create an instance of `Chrome`.

```python
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--headless")
    browser_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=browser_options)
```

Call the `driver.get` method to load a URL. After that, locate the link for the Humor section by link text and click it:

```python
    driver.get(url)

    element = driver.find_element(By.LINK_TEXT, "Humor")
    element.click()
```

Create a CSS selector to find all books from this page. After that run a loop on the books and find the bookt title, price, stock availability. Use a dictionary to store one book information and add all these dictionaries to a list. See the code below:

```python
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

```

Lastly, return the `data` dictionary from this function.

For the complete code, see [main.py](src/main.py).

For a detailed tutorial on Selenium, see [our blog](https://oxylabs.io/blog/selenium-web-scraping).
