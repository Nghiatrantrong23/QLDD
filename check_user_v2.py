import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone

# Check user 462633995787
username = '462633995787'
try:
    user = User.objects.get(username=username)
    print(f"User: {user.username}")
    print(f"Email: {user.email}")
    print(f"Date Joined: {user.date_joined}")
    print(f"Last Login: {user.last_login}")
    # We can't see the password, but we can see if it was recently changed if we had a password_change_date field.
    # Django doesn't have one by default.
except User.DoesNotExist:
    print(f"User {username} not found.")

print("\nRecent users (last 5):")
for u in User.objects.all().order_by('-date_joined')[:5]:
    print(f"- {u.username} ({u.email}) joined {u.date_joined}")
