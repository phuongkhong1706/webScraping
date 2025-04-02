## Overview
This project involves web crawling and an ETL (Extract, Transform, Load) process to manage book data efficiently
## Task
The processes will have two tasks

**Task 1 - Crawling**

- Crawling all books from [Books to Scrape](https://books.toscrape.com/) and save to collections named **books** in MongoDB.


**Task 2 - ETL design**:

The ETL process runs in predefined time intervals (e.g., every 10 minutes) and consists of two phases:

- **Phrase 1: Emulation**
    - Simulate and generate platform events of four types: `click`, `addToCart`, `rate`, and `buy`.
    - Store these events in the **events** table.
    - After event generation, recalculate the book ratings and update the **books** collection.

- **Phrase 2: Aggregation**
    - Maintain a **statistics** table with hourly aggregated data for each book.
    - Maintain a **best_seller** table that tracks the top 3 best-selling books in each genre over different time units (hourly, daily, weekly).


**Table information**:

### **books** (MongoDB)
Stores book information.
```python
'_id' (str): Book id
'title' (str): Title of book 
'description' (str): Description of Book 
'price'(float): Price of a book 
'rate' (float): Average rate of a book
'genre' (str): Genre of a book.
```

### **events** (PostgreSQL)
Stores user interactions on the platform.
```python
'_id' (str): Unique event ID
'type' (str): Event type (`click`, `rate`, `addToCart`, `buy`)
'timestamp' (int): Event timestamp
'userId' (str): ID of the user triggering the event
'metadata' (int): Additional data (e.g., rating score from 1 to 5 for `rate` events)
```


### **statistics** (PostgreSQL)
Stores hourly aggregated statistics for each book.
```python
'_id' (str)
'timestamp' (int) 
'numViews' (int): number of views
'numFavour' (int): number of favours
'numBuy'(int): number of buys
'numRate' (int): number of rates
'avgRate' (float): average rate
```


### **best_seller** (PostgreSQL)
Tracks the top-selling books in each genre over specific time intervals.
```python
'_id' (str): Book id
'genre' (str): Genre of book
'rank' (str): Rank of the book in genre
'totalBuy'(float): total number of a book have been bought
'timeUnit' (str): hourly, daily, weekly
'timestamp' (int) 
```
