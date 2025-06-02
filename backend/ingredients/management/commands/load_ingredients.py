import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из data/ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = settings.BASE_DIR / 'data' / 'ingredients.json'
        count = 0
        with file_path.open(encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                obj, created = Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit'],
                )
                if created:
                    count += 1
        self.stdout.write(
            self.style.SUCCESS(f'Ингредиентов загружено: {count}')
        )
