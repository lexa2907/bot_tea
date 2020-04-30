from django.db import models


class Users(models.Model):
    name = models.PositiveIntegerField('id_пользователя', unique=True)
    nickname = models.CharField('има пользователя', max_length=100)
    mobile = models.CharField('Телефон', max_length=11, blank=True, null=True)
    address = models.TextField('Адрес', blank=True, null=True)
    delivery = models.CharField('Тип доставки', max_length=15, default='🚗 Привезти')
    status = models.CharField(max_length=1, default='1')

    def __str__(self):
        return '{}'.format(self.nickname)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'


class Orders(models.Model):
    number_order = models.PositiveIntegerField('№ Заказа', unique=True,primary_key=True)
    user_order = models.TextField('Заказ пользователя с его данными')


class Basket(models.Model):
    count = models.PositiveSmallIntegerField('Количество')
    baskUser = models.ForeignKey(Users, models.CASCADE, verbose_name='Продукт пользователя')
    name_product = models.CharField('Наименование товара', max_length=250, db_index=True)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=0, default=0)

    def __str__(self):
        return self.name_product

    class Meta:
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Корзина пользователей'


class CategoryOne(models.Model):
    name = models.CharField('Разделы чая', max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Первая категория'
        verbose_name_plural = 'Первая категория'


class AllMenu(models.Model):
    name = models.CharField('Название товара', max_length=250, unique=True)
    photo = models.URLField('URL фото продукта', blank=True, null=True)
    weight = models.DecimalField('Вес в гр.', max_digits=7, decimal_places=0)
    volume = models.PositiveSmallIntegerField('Количество шт.', default=1)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=0, default=0)
    category_one = models.ForeignKey(CategoryOne, models.CASCADE, verbose_name='Категория-1')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Все типы чая'
        verbose_name_plural = 'Все типы чая'
