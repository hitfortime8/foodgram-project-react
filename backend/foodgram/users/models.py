from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=settings.LENGTH_150,
        unique=True
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=settings.LENGTH_EMAIL,
        unique=True
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.LENGTH_150
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.LENGTH_150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LENGTH_150
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='Unique_follow_relation'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='User_is_not_author'
            ),
        ]

    def __str__(self):
        return self.user
