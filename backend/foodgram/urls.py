from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from users.views import CustomUserViewSet
from ingredients.views import IngredientViewSet
from recipes.views import RecipeViewSet

router = routers.SimpleRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('s/<int:id>', RecipeViewSet.as_view({'get': 'retrieve'})),
    path('api/auth/', include('djoser.urls.authtoken')),
]
