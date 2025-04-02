from pymongo import MongoClient
import psycopg2
import random
import time
from datetime import datetime

# Kết nối MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client.books_db
mongo_collection = mongo_db.books

# Kết nối PostgreSQL
pg_conn = psycopg2.connect(
    dbname="books_db",
    user="phuong",
    password="phuong",
    host="localhost",
    port="5432"
)
pcursor = pg_conn.cursor()

# Tạo bảng trong PostgreSQL (bao gồm book_id)
create_events_table = """
CREATE TABLE IF NOT EXISTS events (
    _id TEXT PRIMARY KEY,
    type TEXT,
    timestamp BIGINT,
    userId TEXT,
    metadata INT,
    book_id TEXT
);
"""

create_statistics_table = """
CREATE TABLE IF NOT EXISTS statistics (
    _id TEXT,
    timestamp BIGINT,
    numViews INT DEFAULT 0,
    numFavour INT DEFAULT 0,
    numBuy INT DEFAULT 0,
    numRate INT DEFAULT 0,
    avgRate FLOAT DEFAULT 0,
    CONSTRAINT unique_id_timestamp UNIQUE (_id, timestamp)  -- Thêm unique constraint cho cặp cột (_id, timestamp)
);
"""

create_best_seller_table = """
CREATE TABLE IF NOT EXISTS best_seller (
    _id TEXT,
    genre TEXT,
    rank TEXT,
    totalBuy FLOAT DEFAULT 0,
    timeUnit TEXT,
    timestamp BIGINT,
    CONSTRAINT unique_book UNIQUE (_id, timeUnit, timestamp)  -- Thêm ràng buộc unique
);
"""

pcursor.execute(create_events_table)
pcursor.execute(create_statistics_table)
pcursor.execute(create_best_seller_table)
pg_conn.commit()

# Lấy danh sách book_id từ MongoDB (ObjectId)
book_data = {str(book["_id"]): book["genre"] for book in mongo_collection.find({}, {"_id": 1, "genre": 1})}
book_ids = list(book_data.keys())
user_ids = [f"user_{i}" for i in range(1, 101)]  # 100 user giả lập

# Set lưu các event_id đã tạo ra để tránh trùng lặp
generated_event_ids = set()

def generate_fake_event():
    event_types = ["click", "rate", "addToCart", "buy"]
    event_type = random.choice(event_types)
    # Đảm bảo event_id không bị trùng lặp
    event_id = f"event_{random.randint(1000, 9999)}"
    while event_id in generated_event_ids:
        event_id = f"event_{random.randint(1000, 9999)}"
    generated_event_ids.add(event_id)

    book_id = random.choice(book_ids)
    user_id = random.choice(user_ids)
    timestamp = int(time.time())
    metadata = random.randint(1, 5) if event_type == "rate" else None

    # Thêm book_id vào sự kiện
    pcursor.execute(
        "INSERT INTO events (_id, type, timestamp, userId, metadata, book_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (event_id, event_type, timestamp, user_id, metadata, book_id)
    )
    pg_conn.commit()
    print(f"Inserted event: {event_id}, type: {event_type}, book: {book_id}")

def update_statistics():
    timestamp = int(time.time()) // 3600 * 3600  # Round down to the nearest hour
    pcursor.execute("""
        SELECT book_id, COUNT(*) FILTER (WHERE type = 'click') AS numViews,
                COUNT(*) FILTER (WHERE type = 'addToCart') AS numFavour,
                COUNT(*) FILTER (WHERE type = 'buy') AS numBuy,
                COUNT(*) FILTER (WHERE type = 'rate') AS numRate,
                AVG(metadata) FILTER (WHERE type = 'rate') AS avgRate
        FROM events
        WHERE timestamp >= %s
        GROUP BY book_id
    """, (timestamp,))
    
    rows = pcursor.fetchall()
    for row in rows:
        book_id, numViews, numFavour, numBuy, numRate, avgRate = row
        pcursor.execute("""
            INSERT INTO statistics (_id, timestamp, numViews, numFavour, numBuy, numRate, avgRate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (_id, timestamp) 
            DO UPDATE SET numViews = excluded.numViews, numFavour = excluded.numFavour, 
                         numBuy = excluded.numBuy, numRate = excluded.numRate, avgRate = excluded.avgRate
        """, (book_id, timestamp, numViews, numFavour, numBuy, numRate, avgRate))
        pg_conn.commit()
        print(f"Updated statistics for book: {book_id} at timestamp: {timestamp}")

def update_best_seller():
    timestamp = int(time.time()) // 3600 * 3600  # Round down to the nearest hour
    pcursor.execute("""
        SELECT s._id, SUM(s.numBuy) AS totalBuy
        FROM statistics s
        WHERE s.timestamp >= %s
        GROUP BY s._id
        ORDER BY totalBuy DESC
        LIMIT 3
    """, (timestamp,))
    
    rows = pcursor.fetchall()
    for i, row in enumerate(rows, start=1):
        book_id, totalBuy = row
        genre = book_data.get(book_id, "unknown")  # Lấy genre từ MongoDB
        pcursor.execute("""
            INSERT INTO best_seller (_id, genre, rank, totalBuy, timeUnit, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (_id, timeUnit, timestamp)
            DO UPDATE SET totalBuy = excluded.totalBuy
        """, (book_id, genre, str(i), totalBuy, 'hourly', timestamp))
        pg_conn.commit()
        print(f"Updated best seller: {book_id}, genre: {genre}, rank: {i}, totalBuy: {totalBuy}")

# Chạy giả lập sự kiện và cập nhật dữ liệu mỗi phút và mỗi 2 phút
while True:
    generate_fake_event()
    current_time = int(time.time())

    if current_time % 60 == 0:  # Mỗi 1 phút
        update_statistics()
    
    if current_time % 120 == 0:  # Mỗi 2 phút
        update_best_seller()

    time.sleep(1)
