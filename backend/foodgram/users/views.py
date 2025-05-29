from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .pagination import UserInfoPagination
from .serializers import CustomUserSerializer, AvatarSerializer


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

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == "PUT":
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     methods=['get'],
    #     detail=False,
    #     url_path='subscriptions'
    # )
    # def user_subscriptions(self, request):
    #     user = request.user

    #     if request.method == "PUT":
    #         serializer = AvatarSerializer(user, data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     elif request.method == "DELETE":
    #         user.avatar.delete(save=True)
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     methods=['post', 'delete'],
    #     detail=True,
    #     url_path='me/avatar'
    # )
    # def subscribe(self, request):
    #     user = request.user

    #     if request.method == "PUT":
    #         serializer = AvatarSerializer(user, data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     elif request.method == "DELETE":
    #         user.avatar.delete(save=True)
    #         return Response(status=status.HTTP_204_NO_CONTENT)
