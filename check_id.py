import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'auth_user' AND column_name = 'id';
    """)
    print("Default value of auth_user id:", cursor.fetchone())
