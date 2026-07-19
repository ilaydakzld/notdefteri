import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

tables_to_check = ['auth_user', 'notes_note']

with connection.cursor() as cursor:
    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"{table} count: {count}")
        except Exception as e:
            print(f"{table} error: {e}")
