from rest_framework import serializers

from .models import Recipe


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.avatar.url

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
