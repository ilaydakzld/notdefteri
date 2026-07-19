import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT due_date FROM notes_note;")
    for row in cursor.fetchall():
        print(row)
