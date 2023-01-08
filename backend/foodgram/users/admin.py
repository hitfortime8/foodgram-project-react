from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    fields = ('username', 'email', 'password', 'first_name', 'last_name',)
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name',)
    list_filter = ('email', 'username',)
    empty_value_display = '-Пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user', 'author',)
    empty_value_display = '-Пусто-'
