from djoser.views import UserViewSet
from rest_framework import permissions

from .pagination import UserInfoPagination
from .serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    pagination_class = UserInfoPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if all([self.action in ['update', 'partial_update', 'destroy', 'me'],
                self.request.method in ['PUT', 'PATCH', 'DELETE']]):
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if all([self.action in ['list', 'retrieve', 'me'],
               self.request.method == 'GET']):
            return CustomUserSerializer
        return super().get_serializer_class()
