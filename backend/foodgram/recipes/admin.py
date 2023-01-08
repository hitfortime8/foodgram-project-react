from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientTabular(admin.TabularInline):
    model = IngredientsAmount
    extra = 3
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-Пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
    empty_value_display = '-Пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    list_filter = ('name',)
    empty_value_display = '-Пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('user', )
    empty_value_display = '-Пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'cooking_time',
        'get_favorites',
    )
    search_fields = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    inlines = (IngredientTabular,)
    empty_value_display = '-Пусто-'

    def get_favorites(self, obj):
        return obj.favorites.count()

    get_favorites.short_description = 'Избранное'


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
