import base64
import json

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from recipes.models import IngredientToRecipe, Recipe


class Command(BaseCommand):
    help = 'Загрузка рецептов из data/recipes.json'

    def handle(self, *args, **kwargs):
        recipes_file = settings.BASE_DIR / 'data' / 'recipes.json'
        created_count = 0

        with recipes_file.open(encoding='utf-8') as file:
            recipes = json.load(file)

            for data in recipes:
                image_data = data['image']

                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'image.{ext}'
                )

                recipe = Recipe.objects.create(
                    name=data['name'],
                    text=data['text'],
                    cooking_time=data['cooking_time'],
                    author_id=data['author'],
                    image=image_file
                )

                ingredients_to_recipe = []
                for ing in data['ingredients']:
                    ingredients_to_recipe.append(
                        IngredientToRecipe(
                            recipe=recipe,
                            ingredient_id=ing['id'],
                            amount=ing['amount']
                        )
                    )
                IngredientToRecipe.objects.bulk_create(ingredients_to_recipe)
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Загружено рецептов: {created_count}')
        )
