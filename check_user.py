import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from django.contrib.auth.models import User

username = '462633995787'
try:
    user = User.objects.get(username=username)
    print(f"User found: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is active: {user.is_active}")
    print(f"Last login: {user.last_login}")
except User.DoesNotExist:
    print(f"User {username} not found.")

# Also list all users to see if there are similar ones
print("\nAll users:")
for u in User.objects.all():
    print(f"- {u.username} ({u.email})")
