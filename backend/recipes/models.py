from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (RECIPE_NAME_MAX_LENGTH,
                        RECIPE_IMAGE_UPLOAD_DIR,
                        MIN_COOKING_TIME_VALUE,
                        MIN_INGREDIENT_AMOUNT_VALUE)
from ingredients.models import Ingredient
from users.models import FoodgramUser

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название'
    )

    image = models.ImageField(
        upload_to=RECIPE_IMAGE_UPLOAD_DIR,
        verbose_name='Фото блюда'
    )

    text = models.TextField(
        verbose_name='Описание'
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME_VALUE)
        ],
        verbose_name='Время приготовления'
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientToRecipe',
        verbose_name='Ингредиенты'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class IngredientToRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT_VALUE)
        ],
        verbose_name='Колчиество'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('amount',)

    def __str__(self):
        return (
            f'{self.recipe}: {self.ingredient} '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Добавивший в избранное'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ('recipe__name',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Cart(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='cart_recipes',
        verbose_name='Добавивший в корзину'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        ordering = ('recipe__name',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_in_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
