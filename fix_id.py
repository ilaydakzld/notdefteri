import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    try:
        # Create a sequence for the id column if it doesn't exist
        cursor.execute("CREATE SEQUENCE IF NOT EXISTS auth_user_id_seq OWNED BY auth_user.id;")
        
        # Set the default value to use the sequence
        cursor.execute("ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq');")
        
        # Look up the max id currently in the table
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM auth_user;")
        max_id = cursor.fetchone()[0]
        
        # Set sequence to max_id + 1
        cursor.execute(f"SELECT setval('auth_user_id_seq', {max_id + 1}, false);")
        
        print(f"Sequence created and default set successfully. Next ID will be {max_id + 1}")
    except Exception as e:
        print(f"Error: {e}")
