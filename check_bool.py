import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT is_active, is_staff, is_superuser FROM auth_user;")
    for row in cursor.fetchall():
        print(row)
