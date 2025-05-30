from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Название'
    )

    measurement_unit = models.CharField(
        max_length=10,
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
