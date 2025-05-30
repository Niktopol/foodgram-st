from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import FoodgramUser, Subscription
from .pagination import UserInfoPagination
from .serializers import (FoodgramUserSerializer,
                          AvatarSerializer,
                          SubscriptionUserSerializer)


class CustomUserViewSet(UserViewSet):
    pagination_class = UserInfoPagination

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
        )

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
        following = get_object_or_404(FoodgramUser, id=id)

        if request.method == 'POST':
            if user == following:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif Subscription.objects.filter(
                user=user,
                following=following
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                Subscription.objects.create(
                    user=user,
                    following=following
                )
                serializer = SubscriptionUserSerializer(
                    following,
                    context=self.get_serializer_context()
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                following=following
            )

            if subscription is not None:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
