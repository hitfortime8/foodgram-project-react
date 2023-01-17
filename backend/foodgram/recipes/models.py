from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

from .validators import HexValidator, LettersValidator, SlugValidator


class Tag(models.Model):

    name = models.CharField(
        'Название',
        max_length=settings.LENGTH_STANDARD_RECIPE,
        validators=[LettersValidator()],
        unique=True
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        validators=[HexValidator],
        unique=True
    )
    slug = models.CharField(
        'Уникальный слаг',
        max_length=settings.LENGTH_STANDARD_RECIPE,
        validators=[SlugValidator],
        unique=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):

    name = models.CharField(
        'Наименование',
        max_length=settings.LENGTH_STANDARD_RECIPE,
        validators=[LettersValidator()]
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=settings.LENGTH_STANDARD_RECIPE,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='Уникальные_ингредиенты'
            )
        ]


class Recipe(models.Model):

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название',
        max_length=settings.LENGTH_STANDARD_RECIPE,
        validators=[LettersValidator()]
    )
    image = models.ImageField(
        'Ссылка на картинку на сайте',
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления должно быть больше 0'),
        )
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='%(app_label)s_%(class)s_unique'
            )
        ]


class Favorite(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_list'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'


class IngredientsAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Ингредиент'
    )
    amount = models.SmallIntegerField(
        'Количество',
        validators=(MinValueValidator(
            limit_value=1, message='Количество должно быть больше 0'),
        )
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients'
    )

    class Meta:
        verbose_name = 'Набор ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='Unique ingredients'
            )
        ]
