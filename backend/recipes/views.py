from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Recipe, Favorite, Cart, IngredientToRecipe
from .pagination import RecipePagination
from .permissions import IsAdminOrAuthor
from .serializers import RecipeSerializer
from .filters import RecipeFilter
from users.serializers import SubscriptionRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOrAuthor,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = RecipePagination
    lookup_field = 'id'
    filterset_class = RecipeFilter

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite'
    )
    def set_favorited(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = SubscriptionRecipeSerializer(
                recipe,
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favourite = Favorite.objects.filter(user=user, recipe=recipe)
            if favourite.exists():
                favourite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart'
    )
    def edit_cart(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            if Cart.objects.filter(user=user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Cart.objects.create(user=request.user, recipe=recipe)
            serializer = SubscriptionRecipeSerializer(
                recipe,
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_recipe = Cart.objects.filter(user=user, recipe=recipe)
            if cart_recipe.exists():
                cart_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def get_shopping_cart_file(self, request):
        user = request.user
        ingredients = IngredientToRecipe.objects.filter(
            recipe__cart__user=user
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

        content = '\n'.join(lines)
        filename = 'shopping_cart.txt'

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
