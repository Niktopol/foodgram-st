from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import FoodgramUser


class CustomUserSerializer(UserSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    avatar = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = FoodgramUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'avatar')

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None
