from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FoodgramUser, Subscription


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    model = FoodgramUser
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_active',
        'is_staff'
    )
    list_display_links = ('email', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': (
            'username',
            'first_name',
            'last_name',
            'avatar'
        )}),
        ('Права доступа', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions'
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'first_name',
                'last_name',
                'avatar',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            )}),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    search_fields = ('user__username', 'following__username')
