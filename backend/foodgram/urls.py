from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from users.views import CustomUserViewSet
from ingredients.views import IngredientViewSet

router = routers.SimpleRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
