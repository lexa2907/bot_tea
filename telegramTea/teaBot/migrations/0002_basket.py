# Generated by Django 2.2.10 on 2020-04-22 19:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teaBot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveSmallIntegerField(verbose_name='Количество')),
                ('name_product', models.CharField(db_index=True, max_length=250, verbose_name='Наименование товара')),
                ('price', models.DecimalField(decimal_places=0, default=0, max_digits=8, verbose_name='Цена')),
                ('baskUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teaBot.Users', verbose_name='Продукт пользователя')),
            ],
            options={
                'verbose_name': 'Корзина пользователя',
                'verbose_name_plural': 'Корзина пользователей',
            },
        ),
    ]