import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    try:
        # 1. Fix boolean column
        cursor.execute("ALTER TABLE notes_note ALTER COLUMN is_completed TYPE boolean USING is_completed::int::boolean;")
        print("Updated notes_note.is_completed to boolean.")

        # 2. Fix ID sequence
        cursor.execute("CREATE SEQUENCE IF NOT EXISTS notes_note_id_seq OWNED BY notes_note.id;")
        cursor.execute("ALTER TABLE notes_note ALTER COLUMN id SET DEFAULT nextval('notes_note_id_seq');")
        
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM notes_note;")
        max_id = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT setval('notes_note_id_seq', {max_id + 1}, false);")
        print(f"Set notes_note ID sequence. Next ID will be {max_id + 1}.")
        
    except Exception as e:
        print(f"Error: {e}")
