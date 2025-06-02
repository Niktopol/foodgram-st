from djoser.serializers import UserSerializer
from rest_framework import serializers

from ingredients.models import Ingredient
from recipes.models import Cart, Favorite, IngredientToRecipe, Recipe
from users.models import FoodgramUser, Subscription

from .fields import Base64ImageField


# Сериализаторы пользователей

class FoodgramUserSerializer(UserSerializer):
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = FoodgramUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'avatar', 'is_subscribed')

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, following=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = FoodgramUser
        fields = ('avatar',)


class SubscriptionSerializer(serializers.ModelSerializer):
    following = serializers.PrimaryKeyRelatedField(
        queryset=FoodgramUser.objects.all(),
        error_messages={
            'invalid': 'Неверные данные для подписки.'
        }
    )

    class Meta:
        model = Subscription
        fields = ('following',)

    def validate_following(self, value):
        user = self.context['request'].user

        if user == value or Subscription.objects.filter(
            user=user,
            following=value
        ).exists():
            raise self.fields['following'].fail('invalid')

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        following = validated_data['following']
        return Subscription.objects.create(user=user, following=following)


class SubscriptionUserSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return ShortRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    class Meta(FoodgramUserSerializer.Meta):
        fields = (FoodgramUserSerializer.Meta.fields
                  + ('recipes', 'recipes_count'))


# Сериализаторы ингредиентов

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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


# Сериализаторы рецептов

class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = FoodgramUserSerializer(read_only=True)
    ingredients = IngredientToRecipeSerializer(
        many=True,
        write_only=True,
        error_messages={
            'invalid': 'Ингредиенты не должны повторяться'
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
        representation['ingredients'] = IngredientToRecipeSerializer(
            instance.ingredients_to_recipe,
            many=True
        ).data
        return representation

    def validate(self, data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError({
                'ingredients': [
                    self.fields['ingredients'].error_messages['required']
                ]
            })
        return super().validate(data)

    def validate_ingredients(self, value):
        if value is None or len(value) == 0:
            raise self.fields['ingredients'].fail('required')

        ingredient_ids = [item['ingredient'].id for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise self.fields['ingredients'].fail('invalid')

        return value

    def create_ingredients(self, ingredients_data, recipe):
        IngredientToRecipe.objects.bulk_create([
            IngredientToRecipe(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            )
            for item in ingredients_data
        ])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        IngredientToRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients_data, instance)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        error_messages={
            'invalid': 'Неверные данные для добавления в избранное.'
        }
    )

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def validate_recipe(self, value):
        user = self.context['request'].user

        if Favorite.objects.filter(user=user, recipe=value).exists():
            raise self.fields['recipe'].fail('invalid')

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = validated_data['recipe']
        return Favorite.objects.create(user=user, recipe=recipe)


class CartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        error_messages={
            'invalid': 'Неверные данные для добавления в корзину.'
        }
    )

    class Meta:
        model = Cart
        fields = ('recipe',)

    def validate_recipe(self, value):
        user = self.context['request'].user

        if Cart.objects.filter(user=user, recipe=value).exists():
            raise self.fields['recipe'].fail('invalid')

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = validated_data['recipe']
        return Cart.objects.create(user=user, recipe=recipe)
