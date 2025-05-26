from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class FoodgramUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\z')
        ],
        blank=False,
        null=False,
        verbose_name="Уникальный юзернейм"
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Адрес электронной почты"
    )

    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Имя"
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Фамилия"
    )

    avatar = models.ImageField(
        upload_to='avatar/images/',
        blank=True,
        null=True,
        default=None,
        verbose_name="Аватар пользователя"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'
