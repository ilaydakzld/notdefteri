import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    try:
        # safely cast due_date text to date, treating empty strings as NULL
        cursor.execute("ALTER TABLE notes_note ALTER COLUMN due_date TYPE date USING NULLIF(due_date, '')::date;")
        print("Updated notes_note.due_date to date.")
    except Exception as e:
        print(f"Error: {e}")
