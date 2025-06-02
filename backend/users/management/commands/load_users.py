import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка пользователей из data/users.json'

    def handle(self, *args, **kwargs):
        file_path = settings.BASE_DIR / 'data' / 'users.json'
        created_count = 0

        with file_path.open(encoding='utf-8') as file:
            users = json.load(file)
            for user_data in users:
                email = user_data['email']
                if User.objects.filter(email=email).exists():
                    continue

                user = User.objects.create_user(
                    email=email,
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password=user_data['password']
                )

                if user_data.get('is_admin'):
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()

                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Создано пользователей: {created_count}')
        )
