# Приложение Foodgram

Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

Чтобы использовать все возможности сайта — нужна регистрация. Проверка адреса электронной почты не осуществляется, вы можете ввести любой email.

Заходите и делитесь своими любимыми рецептами!

## Запуск приложения

Для запуска проекта необходимо в директории infra создать .env по примеру .env.example (также находится в infra). Пример содежания .env:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=django-insecure-=e7s9zvygrgc%v*zgiaxuptr8gkh&@_w$879mt99o3capsw985
DJANGO_DEBUG_DISABLED=true
DJANGO_ALLOWED_HOSTS=localhost,*
DJANGO_USE_POSTGRES=true
```

Далее, находясь в директории infra, необходимо выполнить команду:

```bash
docker compose up
```

После сборки контейнеров приложение будет доступно по адресу http://localhost.

Админка приложения будет доступна по адресу http://localhost/admin/.

По адресу http://localhost/api/docs/ представлена спецификация API, используемого веб-приложением.
