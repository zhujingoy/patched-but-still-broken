import os

DB_CONFIG = {
    'host': '121.29.19.131',
    'port': 3306,
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'appdb',
    'charset': 'utf8mb4'
}
