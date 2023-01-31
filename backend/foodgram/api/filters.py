from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe
from rest_framework.filters import SearchFilter
from users.models import User


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.NumberFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_filter'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')

    def is_favorited_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset
