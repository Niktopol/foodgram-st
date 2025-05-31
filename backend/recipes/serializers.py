import base64
from django.core.files.base import ContentFile
from rest_framework import serializers

from ingredients.models import Ingredient
from users.serializers import FoodgramUserSerializer
from .models import Recipe, IngredientToRecipe, Favorite, Cart


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
        error_messages={
            'invalid': 'List contains repetitive ingredients'
        }
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Cart.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text', 'cooking_time', 'author',
                  'is_favorited', 'is_in_shopping_cart', 'ingredients')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredients = IngredientToRecipe.objects.filter(recipe=instance)
        representation['ingredients'] = IngredientToRecipeSerializer(
            ingredients,
            many=True
        ).data
        return representation

    def check_ingredients(self, ingredients_data):
        if ingredients_data is None or len(ingredients_data) == 0:
            raise self.fields['ingredients'].fail('required')
        ingredient_ids = [item['ingredient'].id for item in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise self.fields['ingredients'].fail('invalid')

    def create_ingredients(self, ingredients_data, recipe):
        for item in ingredients_data:
            IngredientToRecipe.objects.create(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        self.check_ingredients(ingredients_data)
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        self.check_ingredients(ingredients_data)
        IngredientToRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients_data, instance)
        return super().update(instance, validated_data)
