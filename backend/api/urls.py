from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet
from .views import IngredientViewSet
from .views import RecipeViewSet

router = routers.SimpleRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
