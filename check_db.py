import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'auth_user';")
    for row in cursor.fetchall():
        print(row)
