import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notdefteri.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    try:
        cursor.execute("ALTER TABLE auth_user ALTER COLUMN is_active TYPE boolean USING is_active::int::boolean;")
        cursor.execute("ALTER TABLE auth_user ALTER COLUMN is_staff TYPE boolean USING is_staff::int::boolean;")
        cursor.execute("ALTER TABLE auth_user ALTER COLUMN is_superuser TYPE boolean USING is_superuser::int::boolean;")
        print("Updated columns successfully.")
    except Exception as e:
        print(f"Error updating columns: {e}")
