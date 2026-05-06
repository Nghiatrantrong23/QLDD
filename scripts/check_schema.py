import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

def check():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name LIKE 'myapp_%'
            ORDER BY table_name, column_name
        """)
        for row in cursor.fetchall():
            print(f"Table: {row[0]}, Column: {row[1]}, Type: {row[2]}")

if __name__ == "__main__":
    check()
