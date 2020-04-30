from telebot import types
from teaBot.models import CategoryOne


def type_of_payment():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('💳Оплата онлайн', '💵Оплата при получении')
    keyboard.row('⬅️ Отменить заявку')
    return keyboard


def canceling_a_request():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('⬅️ Отменить заявку')
    return keyboard


def start_menu():
    start_keyboard = types.ReplyKeyboardMarkup(True, False)
    start_keyboard.row('📋 Каталог')
    start_keyboard.row('📥 Корзина', '📳 Контакты')
    start_keyboard.row('🚖 Оформить заказ')
    return start_keyboard


def keyboard_user_number():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.add(types.KeyboardButton(text="📱Отправить мой номер телефона", request_contact=True))
    keyboard.row('⬅️ Отменить заявку')
    return keyboard


def name_user(name):
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row(f'{name}')
    keyboard.row('⬅️ Отменить заявку')
    return keyboard


def keyboard_category_one(category):
    keyboard = types.ReplyKeyboardMarkup(True, False)
    for i in category.allmenu_set.all():
        keyboard.row(f'{i.name}')
    keyboard.row('🚖 Оформить заказ')
    keyboard.row('🔙 Назад', '📥 Корзина')
    return keyboard


def keyboard_count():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('1', '2', '3')
    keyboard.row('4', '5', '6')
    keyboard.row('7', '8', '9')
    keyboard.row('🔙 Назад', '📥 Корзина')
    return keyboard


def type_delivery():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('🏃 Заберу сам', '🚗 Привезти')
    keyboard.row('⬅️ Отменить заявку')
    return keyboard


def keyboard_count_tea(tea_id):
    keyboard = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text='➕', callback_data=f'add|{tea_id}')
    but_2 = types.InlineKeyboardButton(text='➖', callback_data=f'down|{tea_id}')
    but_3 = types.InlineKeyboardButton(text='✅', callback_data='ok')
    keyboard.add(but_1, but_2)
    keyboard.add(but_3)
    return keyboard


def keyboard_catalog():
    keyboard = types.ReplyKeyboardMarkup(True, False)
    arr = CategoryOne.objects.all()
    if len(arr) % 2 == 0:
        for i in range(0, len(arr), 2):
            if len(arr[i].name) > 25:
                keyboard.row(f'{arr[i].name}')
                keyboard.row(f'{arr[i + 1].name}')
            elif len(arr[i + 1].name) > 25:
                keyboard.row(f'{arr[i].name}')
                keyboard.row(f'{arr[i + 1].name}')
            else:
                keyboard.row(f'{arr[i].name}', f'{arr[i + 1].name}')
    else:
        for i in range(0, len(arr) - 1, 2):
            if len(arr[i].name) > 25:
                keyboard.row(f'{arr[i].name}')
                keyboard.row(f'{arr[i + 1].name}')
            elif len(arr[i + 1].name) > 25:
                keyboard.row(f'{arr[i].name}')
                keyboard.row(f'{arr[i + 1].name}')
            else:
                keyboard.row(f'{arr[i].name}', f'{arr[i + 1].name}')
        keyboard.row(f'{arr[-1].name}')
    keyboard.row('🚖 Оформить заказ')
    keyboard.row('📋 Главное меню', '📥 Корзина')
    return keyboard