from db import run_query

try:
    df = run_query("SELECT COUNT(*) as total FROM orders")
    print("Connected! Orders in DB:", df['total'][0])
except Exception as e:
    print("Failed:", e)