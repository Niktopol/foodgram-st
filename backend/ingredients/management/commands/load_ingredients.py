import json
import os
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из data/ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('data', 'ingredients.json')
        count = 0
        with open(file_path, encoding='utf-8') as file:
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
