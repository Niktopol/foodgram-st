import json
import os

from django.core.files import File
from django.core.management.base import BaseCommand

from recipes.models import Recipe, IngredientToRecipe, Ingredient
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка рецептов из data/recipes.json'

    def handle(self, *args, **kwargs):
        recipes_file = os.path.join('data', 'recipes.json')
        images_dir = os.path.join('data', 'recipes_images')
        created_count = 0

        with open(recipes_file, encoding='utf-8') as file:
            recipes = json.load(file)

            for data in recipes:
                author = User.objects.get(id=data['author'])
                image_path = os.path.join(images_dir, data['image'])

                with open(image_path, 'rb') as img_file:
                    recipe = Recipe.objects.create(
                        name=data['name'],
                        text=data['text'],
                        cooking_time=data['cooking_time'],
                        author=author,
                        image=File(img_file, name=data['image'])
                    )

                for ing in data['ingredients']:
                    ingredient = Ingredient.objects.get(id=ing['id'])
                    IngredientToRecipe.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=ing['amount']
                    )

                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Загружено рецептов: {created_count}')
        )
