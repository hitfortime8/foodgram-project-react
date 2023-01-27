from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User


class UserSerializer(UserSerializer):
    username = serializers.CharField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'username', 'password', 'email', 'first_name',
                  'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    amount = serializers.FloatField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientsAmount


class IngredientsAmountWriteSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Ingredient.objects.all(),
        read_only=False
    )

    class Meta:
        fields = ('id', 'amount')
        model = IngredientsAmount


class ReadRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientsAmountSerializer(many=True)
    tags = TagSerializer(read_only=True, many=True)
    image = serializers.CharField(source='image.url')
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'author', 'ingredients', 'tags',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorite', 'is_in_shopping_cart')
        model = Recipe

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(
            user=request.user,
            recipe=obj
        ).exists()


class WriteRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsAmountWriteSerializer(many=True, required=False)
    image = Base64ImageField(required=True)

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for data in ingredients:
            ingredient_list.append(
                IngredientsAmount(
                    ingredient=data.pop('id'),
                    amount=data.pop('amount'),
                    recipe=recipe,
                )
            )
        IngredientsAmount.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        request = self.context.get('request', None)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientsAmount.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance=instance,
                                    context=self.context
                                    ).data

    class Meta:
        fields = ('id', 'ingredients', 'tags', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscriberSerializer(UserSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        author_id = self.context.get('request').parser_context.get(
            'kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(detail='Вы уже подписаны')
        if user == author:
            raise ValidationError(detail='Нельзя подписаться на себя')
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeSmallSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe',)
        model = ShoppingCart

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe',)
        model = Favorite

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в  избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
