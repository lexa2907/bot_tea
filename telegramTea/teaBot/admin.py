from django.contrib import admin
from .models import *


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['name', 'nickname', 'mobile', 'address', 'delivery','id']
    search_fields = ('nickname',)
    exclude = ['status','basket_sum']


@admin.register(CategoryOne)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(AllMenu)
class AssortmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo', 'price', 'weight','volume', 'category_one']
    search_fields = ('category_one__name', 'name',)
    ordering = ('category_one',)
    list_filter = ('category_one',)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['name_product', 'baskUser', 'count', 'price']
    ordering = ('baskUser',)

# Register your models here.
