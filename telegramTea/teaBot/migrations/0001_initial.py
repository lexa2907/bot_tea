# Generated by Django 2.2.10 on 2020-04-21 08:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryOne',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Разделы чая')),
            ],
            options={
                'verbose_name': 'Первая категория',
                'verbose_name_plural': 'Первая категория',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.PositiveIntegerField(unique=True, verbose_name='id_пользователя')),
                ('nickname', models.CharField(max_length=100, verbose_name='има пользователя')),
                ('mobile', models.CharField(blank=True, max_length=11, null=True, verbose_name='Телефон')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Адрес')),
                ('delivery', models.CharField(default='🚗 Привезти', max_length=15, verbose_name='Тип доставки')),
                ('time_delivery', models.CharField(default='Как можно скорее', max_length=20, verbose_name='Время доставки')),
                ('status', models.CharField(default='1', max_length=1)),
                ('basket_sum', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Пользователи',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='AllMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Название товара')),
                ('photo', models.URLField(blank=True, null=True, verbose_name='URL фото продукта')),
                ('weight', models.DecimalField(decimal_places=0, max_digits=7, verbose_name='Вес в гр.')),
                ('volume', models.PositiveSmallIntegerField(default=1, verbose_name='Количество шт.')),
                ('price', models.DecimalField(decimal_places=0, default=0, max_digits=8, verbose_name='Цена')),
                ('category_one', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teaBot.CategoryOne', verbose_name='Категория-1')),
            ],
            options={
                'verbose_name': 'Все типы чая',
                'verbose_name_plural': 'Все типы чая',
            },
        ),
    ]
