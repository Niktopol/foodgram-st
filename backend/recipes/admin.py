from django.db.models import Prefetch
from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilter

from .models import Recipe, IngredientToRecipe, Favorite, Cart


class IngredientToRecipeInline(admin.TabularInline):
    model = IngredientToRecipe
    min_num = 1
    extra = 0
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты рецепта"


class AuthorFilter(AutocompleteFilter):
    title = 'Автор'
    field_name = 'author'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'cooking_time')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = (AuthorFilter,)
    inlines = (IngredientToRecipeInline,)
    readonly_fields = ('id', 'favorite_count')
    ordering = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author').prefetch_related(
            Prefetch(
                'ingredients_to_recipe',
                queryset=IngredientToRecipe.objects.select_related(
                    'ingredient'
                )
            )
        )

    def favorite_count(self, obj):
        return obj.favorited_by.count()
    favorite_count.short_description = 'Добавлений в избранное'


class IngredientFilter(AutocompleteFilter):
    title = 'Ингредиент'
    field_name = 'ingredient'


class RecipeFilter(AutocompleteFilter):
    title = 'Рецепт'
    field_name = 'recipe'


@admin.register(IngredientToRecipe)
class IngredientToRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_display_links = ('ingredient',)
    list_filter = (IngredientFilter, RecipeFilter)
    ordering = ('recipe',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('recipe').select_related('ingredient')


class AddedByFilter(AutocompleteFilter):
    title = 'Добавивший'
    field_name = 'user'


class BaseUserRecipe(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('recipe',)
    list_filter = (RecipeFilter, AddedByFilter)
    ordering = ('recipe__name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user').select_related('recipe')


@admin.register(Favorite)
class FavoriteAdmin(BaseUserRecipe):
    pass


@admin.register(Cart)
class CartAdmin(BaseUserRecipe):
    pass
