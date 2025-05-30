import csv
import os
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из data/ingredients.csv'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('data', 'ingredients.csv')
        count = 0
        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                obj, created = Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
                if created:
                    count += 1
        self.stdout.write(
            self.style.SUCCESS(f'Ингредиентов загружено: {count}')
        )
