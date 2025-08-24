import psycopg2

conn = psycopg2.connect(
    dbname="knowyourcampus",
    user="kyc",
    password="knowyourcampus",
    host="192.168.137.65",
    port="5432"
)
print("Connected successfully!")
conn.close()
