from django.contrib import admin

from .models import Recipe, IngredientToRecipe, Favorite, Cart


class IngredientToRecipeInline(admin.TabularInline):
    model = IngredientToRecipe
    extra = 1  # Показывает 1 пустую строку для нового ингредиента
    min_num = 1
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты рецепта"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'cooking_time')
    search_fields = ('name', 'author__username')
    list_filter = ('author',)
    inlines = (IngredientToRecipeInline,)
    readonly_fields = ('id',)
    ordering = ('name',)


@admin.register(IngredientToRecipe)
class IngredientToRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('ingredient',)
    ordering = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    ordering = ('recipe__name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    ordering = ('recipe__name',)
