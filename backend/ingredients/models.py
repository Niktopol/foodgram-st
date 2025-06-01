from django.db import models

from .constants import (MAX_INGREDIENT_NAME_LENGTH,
                        MAX_MEASUREMENT_UNIT_NAME_LENGTH)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Название'
    )

    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_NAME_LENGTH,
        blank=False,
        null=False,
        verbose_name='Единица измерения',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
