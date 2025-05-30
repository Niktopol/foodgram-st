import base64
from django.core.files.base import ContentFile
from rest_framework import serializers

from ingredients.models import Ingredient
from users.serializers import FoodgramUserSerializer
from .models import Recipe, IngredientToRecipe


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='avatar.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = FoodgramUserSerializer(read_only=True)
    ingredients = IngredientToRecipeSerializer(
        many=True,
        write_only=True,
        required=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text',
                  'cooking_time', 'author', 'ingredients')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredients = IngredientToRecipe.objects.filter(recipe=instance)
        representation['ingredients'] = IngredientToRecipeSerializer(
            ingredients,
            many=True
        ).data
        return representation

    def create_ingredients(self, ingredients_data, recipe):
        for item in ingredients_data:
            IngredientToRecipe.objects.create(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is None:
            raise self.fields['ingredients'].fail('required')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is not None:
            IngredientToRecipe.objects.filter(recipe=instance).delete()
            self.create_ingredients(ingredients_data, instance)
        return super().update(instance, validated_data)
