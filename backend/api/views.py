from django.db.models import Count, Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ingredients.models import Ingredient
from recipes.models import Cart, Favorite, IngredientToRecipe, Recipe
from users.models import FoodgramUser, Subscription

from .constants import SHOPPING_LIST_FILE_NAME
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrAuthor
from .serializers import (
    AvatarSerializer,
    CartSerializer,
    FavoriteSerializer,
    FoodgramUserSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscriptionSerializer,
    SubscriptionUserSerializer,
)


# Вьюсеты пользователей

class CustomUserViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return (permissions.AllowAny(),)
        if all([self.action in ['update', 'partial_update', 'destroy', 'me'],
                self.request.method in ['PUT', 'PATCH', 'DELETE']]):
            return (permissions.IsAdminUser(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if all([self.action in ['list', 'retrieve', 'me'],
               self.request.method == 'GET']):
            return FoodgramUserSerializer
        return super().get_serializer_class()

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions'
    )
    def user_subscriptions(self, request):
        queryset = FoodgramUser.objects.filter(
            subscriptions__user=request.user
        ).annotate(recipes_count=Count('recipes'))

        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionUserSerializer(
            pages,
            many=True,
            context=self.get_serializer_context()
        )

        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe'
    )
    def subscribe(self, request, id):
        user = request.user

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'following': id},
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            following = FoodgramUser.objects.annotate(
                recipes_count=Count('recipes')
            ).get(id=id)

            resp = SubscriptionUserSerializer(
                following,
                context=self.get_serializer_context()
            )
            return Response(resp.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                following_id=id
            )
            if subscription.delete()[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Вьюсеты ингредиентов

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    pagination_class = None
    search_fields = ('name',)


# Вьюсеты рецептов

class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.select_related('author').prefetch_related(
        Prefetch(
            'ingredients_to_recipe',
            queryset=IngredientToRecipe.objects.select_related(
                'ingredient'
            )
        )
    )

    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOrAuthor,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitPageNumberPagination
    lookup_field = 'id'
    filterset_class = RecipeFilter

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite'
    )
    def set_favorited(self, request, id):
        user = request.user

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'recipe': id},
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            resp = ShortRecipeSerializer(
                Recipe.objects.get(id=id),
                context=self.get_serializer_context()
            )
            return Response(resp.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favourite = Favorite.objects.filter(user=user, recipe_id=id)
            if favourite.delete()[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart'
    )
    def edit_cart(self, request, id):
        user = request.user

        if request.method == 'POST':
            serializer = CartSerializer(
                data={'recipe': id},
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            resp = ShortRecipeSerializer(
                Recipe.objects.get(id=id),
                context=self.get_serializer_context()
            )
            return Response(resp.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_recipe = Cart.objects.filter(user=user, recipe_id=id)
            if cart_recipe.delete()[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_shopping_cart_file_text(self, ingredients):
        lines = []
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            lines.append(f'{name} - {amount} {unit}')

        return '\n'.join(lines)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def get_shopping_cart_file(self, request):
        user = request.user
        ingredients = IngredientToRecipe.objects.filter(
            recipe__added_to_cart_by__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name').all()

        lines = []
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            lines.append(f'{name} - {amount} {unit}')

        content = self.get_shopping_cart_file_text(ingredients)
        filename = f'{SHOPPING_LIST_FILE_NAME}.txt'

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def retrieve_short_link(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        link = request.build_absolute_uri(f'/s/{recipe.id}')
        return Response(
            {'short-link': link},
            status=status.HTTP_200_OK
        )
