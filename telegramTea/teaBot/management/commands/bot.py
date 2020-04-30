from django.core.management.base import BaseCommand
import telebot
from telebot import types
from telebot import apihelper
from django.db.models import F
import re
from django.core import exceptions
import json
from teaBot.models import CategoryOne, AllMenu, Users, Basket, Orders
from telegramTea.settings import BOT, PAYMENTS_PROVIDER_TOKEN, ID_HELP_CHANNEL, ID_ORDER_CHANNEL
from teaBot.keyboardBot import type_of_payment, canceling_a_request, start_menu, keyboard_user_number, name_user, keyboard_category_one, keyboard_count, type_delivery, keyboard_count_tea,keyboard_catalog


class Command(BaseCommand):
    help = "Телеграмм бот"

    def handle(self, *args, **options):
        bot = telebot.TeleBot(BOT)
        apihelper.proxy = {'https': 'socks5h://PrhZ8F:eebLU48kCY@188.130.129.144:5501'}
        basket_count = {}

        def help_user(chat_id):
            keyboard = types.ReplyKeyboardMarkup(True, False)
            keyboard.row('✉️Вопрос оператору')
            keyboard.row('🏢 О компании')
            keyboard.row('🔙 Назад')
            bot.send_message(chat_id, '*Телефон*:\n☎️Мобильный: +99898 125 31 03\n'
                                      '☎️Мобильный: +99898 126 31 03\n\n*Наша почта*: info@mehrigiyo.uz\n📍'
                                      '*Наш адрес*: Республика Узбекистан, Ферганская область Учкуприкский'
                                      ' район, ул. Урозимерган, 94\n\n*Мы открыты*: 8.00 - 18.00',
                             parse_mode='markdown', reply_markup=keyboard)

        def order_registration(chat_id, user):
            if user.basket_set.count() == 0:
                bot.send_message(chat_id, 'Ваша корзина пуста')
            else:
                user.basket_set.filter(count=0).delete()
                if user.basket_set.count() == 0:
                    bot.send_message(chat_id, 'Ваша корзина пуста')
                else:
                    user.status = '5'
                    user.save(update_fields=["status"])
                    bot.send_message(chat_id, 'Введите свое имя:', reply_markup=name_user(user.nickname))

        def user_basket(user, user_id):
            user.basket_set.filter(count=0).delete()
            count = user.basket_set.count()
            keyboard = types.ReplyKeyboardMarkup(True, False)
            if count > 0:
                keyboard.row('🗑️Очистить корзину')
                basket_user = user.basket_set.in_bulk()
                text = 'Ваша корзина:\n\n'
                all_sum = 0
                for i in basket_user:
                    if basket_user[i].count == 0:
                        continue
                    else:
                        keyboard.row(f'✏️ {basket_user[i].name_product} ({basket_user[i].count} шт.)')
                        sum_position = basket_user[i].count * basket_user[i].price
                        text += f'*{basket_user[i].name_product}*\n{basket_user[i].count} x {basket_user[i].price} = ' \
                                f'{sum_position} ₽\n'
                        all_sum += sum_position

                text += f'\nИтого: {all_sum} ₽'
                keyboard.row('📋 Главное меню', '🚖 Оформить заказ')
                if all_sum == 0:
                    bot.send_message(user_id, 'Ваша корзина очищена', reply_markup=start_menu())
                else:
                    bot.send_message(user_id, text, parse_mode='markdown', reply_markup=keyboard)
            else:
                keyboard.row('📋 Главное меню')
                bot.send_message(user_id, 'В вашей корзине пусто', reply_markup=keyboard)

        @bot.message_handler(commands=['start'])
        def start_bot(message):
            user, _ = Users.objects.get_or_create(name=message.chat.id,
                                                  defaults={'nickname': message.from_user.first_name})
            user.status = '1'
            user.save(update_fields=['status'])
            bot.send_message(message.chat.id, 'Вас приветствует официальный телеграмм - бот компании "Mehrigiyo"',
                             reply_markup=start_menu())

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '2')
        def category_tea(message):
            user = Users.objects.get(name=message.chat.id)
            if message.text == '📋 Главное меню':
                start_bot(message)
            elif message.text == "🚖 Оформить заказ":
                order_registration(message.chat.id, user)
            elif message.text == "📥 Корзина":
                user.status = '1'
                user.save(update_fields=["status"])
                user_basket(user, message.chat.id)
            elif CategoryOne.objects.filter(name=message.text).exists():
                user.status = '3'
                user.save(update_fields=["status"])
                category = CategoryOne.objects.get(name=message.text)
                bot.send_message(message.chat.id, 'Выберите нужный раздел',
                                 reply_markup=keyboard_category_one(category))
            else:
                bot.send_message(message.chat.id, 'Выберите пожалуйста раздел на клавиатуре')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '3')
        def tea(message):
            user = Users.objects.get(name=message.chat.id)
            user.basket_set.filter(count=0).delete()
            if message.text == '🚖 Оформить заказ':
                order_registration(message.chat.id, user)
            elif message.text == "📥 Корзина":
                user.status = '1'
                user.save(update_fields=["status"])
                user_basket(user, message.chat.id)
            elif message.text == '🔙 Назад':
                user.status = '2'
                user.save(update_fields=["status"])
                bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=keyboard_catalog())
            elif AllMenu.objects.filter(name=message.text).exists():
                user.status = '4'
                user.save(update_fields=["status"])
                object_tea = AllMenu.objects.get(name=message.text)
                basket_count[f'{message.chat.id}'] = message.text
                if object_tea.weight == 0:
                    bot.send_photo(message.chat.id, object_tea.photo,
                                   f'{object_tea.name}\nОбъем: {object_tea.volume} шт.\nЦена: {object_tea.price} ₽',
                                   reply_markup=keyboard_count())
                else:
                    bot.send_photo(message.chat.id, object_tea.photo,
                                   f'{object_tea.name}\nОбъем: {object_tea.weight} г.\nЦена: {object_tea.price} ₽',
                                   reply_markup=keyboard_count())
            else:
                bot.send_message(message.chat.id, 'Выберите пожалуйста раздел на клавиатуре')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '4')
        def count_product(message):
            user = Users.objects.get(name=message.chat.id)
            if message.text.isdigit():
                try:
                    if user.basket_set.filter(name_product=basket_count[f'{message.chat.id}']).exists():
                        object_tea = user.basket_set.get(name_product=basket_count[f'{message.chat.id}'])
                        if object_tea.count + int(message.text) > 10000:
                            bot.send_message(message.chat.id, 'Введите корректное число.\nКоличество в корзине'
                                                              ' не должно превышать 10000 шт.')
                        else:
                            object_tea.count += int(message.text)
                            user.status = '2'
                            user.save(update_fields=["status"])
                            object_tea.save(update_fields=["count"])
                            del basket_count[f'{message.chat.id}']
                            bot.send_message(message.chat.id, 'Добавлено в корзину. Продолжим?',
                                             reply_markup=keyboard_catalog())
                    else:
                        if int(message.text) > 10000:
                            bot.send_message(message.chat.id, 'Введите корректное число.\nКоличество в корзине'
                                                              ' не должно превышать 10000 шт.')
                        else:
                            user.status = '2'
                            user.save(update_fields=["status"])
                            arr = AllMenu.objects.get(name=basket_count[f'{message.chat.id}'])
                            Basket.objects.create(name_product=basket_count[f'{message.chat.id}'],
                                                  price=arr.price, baskUser=user, count=int(message.text))
                            del basket_count[f'{message.chat.id}']
                            bot.send_message(message.chat.id, 'Добавлено в корзину. Продолжим?',
                                             reply_markup=keyboard_catalog())
                except KeyError:
                    user.status = '1'
                    user.save(update_fields=["status"])
                    keyboard = types.ReplyKeyboardMarkup(True, False)
                    keyboard.row('Начать с главного меню')
                    bot.send_message(message.chat.id, 'Вы отсутствовали долгое время, вам требуется начать с /start',
                                     reply_markup=keyboard)
            elif message.text == '📥 Корзина':
                user.status = '1'
                user.save(update_fields=["status"])
                user_basket(user, message.chat.id)
            elif message.text == '🔙 Назад':
                user.status = '3'
                user.save(update_fields=["status"])
                category = AllMenu.objects.get(name=basket_count[f'{message.chat.id}']).category_one
                bot.send_message(message.chat.id, 'Выберите нужный раздел',
                                 reply_markup=keyboard_category_one(category))
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, 'Введите корректное число.')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '5')
        def order_registration_name(message):
            user = Users.objects.get(name=message.chat.id)
            if message.text == '⬅️ Отменить заявку':
                Users.objects.filter(name=message.chat.id).update(status='1')
                bot.send_message(message.chat.id, 'Главное меню:', reply_markup=start_menu())
            elif (message.text.isalpha() and len(message.text) < 30) or message.text == user.nickname:
                user.nickname = message.text
                user.status = '6'
                user.save(update_fields=['nickname', 'status'])

                bot.send_message(message.chat.id, 'Выберите тип доставки.\nСтоимость доставки 300р.'
                                                  '\nБесплатная доставка при заказе от 2000 ₽.',
                                 reply_markup=type_delivery())
            else:
                bot.send_message(message.chat.id, 'Введите корректно имя', reply_markup=name_user(user.nickname))

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '6')
        def order_registration_delivery(message):
            if message.text == '⬅️ Отменить заявку':
                Users.objects.filter(name=message.chat.id).update(status='1')
                bot.send_message(message.chat.id, 'Главное меню:', reply_markup=start_menu())
            elif message.text == '🚗 Привезти':
                Users.objects.filter(name=message.chat.id).update(delivery=message.text, status='7')
                bot.send_message(message.chat.id, 'Введите адрес доставки\nУлица, номер дома, номер квартиры',
                                 reply_markup=canceling_a_request())
            elif message.text == '🏃 Заберу сам':
                Users.objects.filter(name=message.chat.id).update(delivery=message.text, status='8')
                bot.send_message(message.chat.id, 'Нажмите на кнопку для отправки своего номера',
                                 reply_markup=keyboard_user_number())
            else:
                bot.send_message(message.chat.id, 'Выберите на клавиатуре способ получения товара')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == '7')
        def order_registration_location(message):
            if message.text == '⬅️ Отменить заявку':
                Users.objects.filter(name=message.chat.id).update(status='1')
                bot.send_message(message.chat.id, 'Главное меню:', reply_markup=start_menu())
            elif len(message.text) < 50:
                Users.objects.filter(name=message.chat.id).update(address=message.text, status='8')
                bot.send_message(message.chat.id, 'Нажмите на кнопку для отправки своего номера',
                                 reply_markup=keyboard_user_number())
            else:
                bot.send_message(message.chat.id, 'Введите корректо адрес')

        @bot.message_handler(content_types="contact")
        def order_registration_number(message):
            if Users.objects.get(name=message.chat.id).status == '8':
                if message.contact is not None:
                    Users.objects.filter(name=message.chat.id).update(mobile=message.contact.phone_number, status='p')
                    bot.send_message(message.chat.id, 'Выберите способ оплаты', reply_markup=type_of_payment())
                else:
                    bot.send_message(message.chat.id, 'Выберите кнопку на клавиатуре')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == 'p')
        def pay(message):
            if message.text == '⬅️ Отменить заявку':
                start_bot(message)
            elif message.text == '💳Оплата онлайн':
                user = Users.objects.get(name=message.chat.id)
                user.status = '1'
                user.save(update_fields=['status'])
                price = []
                count = 1
                all_sum = 0
                with open('order_number.json', 'r') as f:
                    number = json.load(f)['number']
                number_order = json.dumps({"number": number + 1})
                with open('order_number.json', 'w') as f:
                    f.write(number_order)
                text = f'*Заказ № {number}*\n'
                text_admin = f'❗️ *Вам пришел заказ № {number}*\n\n'
                if user.delivery == '🏃 Заберу сам':
                    text_admin += f'👤Данные покупателя\n{user.nickname}, ' \
                           f'{user.mobile}\n📦Тип доставки:\n{user.delivery}\n\n-----\n🛒Товары:\n'
                else:
                    text_admin += f'👤Данные покупателя\n{user.nickname}, ' \
                           f'{user.mobile}\n📦Тип доставки:\n{user.delivery}\n' \
                           f'адрес доставки:{user.address}\n\n-----\n🛒Товары:\n'
                for i in user.basket_set.all():
                    position_sum = i.count * i.price
                    all_sum += position_sum
                    price.append(types.LabeledPrice(label=f'позиция {count}: {i.count}шт. x {i.price}₽',
                                                    amount=int(position_sum * 100)))
                    text += f'*позиция {count}* - {i.name_product}\n{i.count} x {i.price} = {position_sum} ₽\n'
                    text_admin += f'*позиция {count}* - {i.name_product}\n{i.count} x {i.price} = {position_sum} ₽\n'
                    count += 1
                if user.delivery == '🚗 Привезти':
                    if all_sum < 2000:
                        price.append(types.LabeledPrice(label=f'Доставка 300 ₽',
                                                        amount=30000))
                        text += '\n+ _Доставка 300 ₽_'
                        text_admin += f'\n-----\n*Доставка:* 200 ₽\n✅*ОПЛАЧЕНО* {all_sum + 300} ₽'
                    else:
                        text_admin += f'\n-----\n✅*ОПЛАЧЕНО* {all_sum} ₽'
                else:
                    text_admin += f'\n-----\n✅*ОПЛАЧЕНО* {all_sum} ₽'
                Orders.objects.create(number_order=number, user_order=text_admin)
                user.basket_set.all().delete()
                bot.send_message(message.chat.id, text, parse_mode='markdown', reply_markup=start_menu())
                bot.send_invoice(chat_id=message.chat.id,
                                 title=f'Заказ № {number}',
                                 description=f'Оплата заказа № {number}',
                                 provider_token=PAYMENTS_PROVIDER_TOKEN,
                                 currency='RUB', is_flexible=False,
                                 prices=price, start_parameter='time-machine-example',
                                 invoice_payload='{0}'.format(number))
            elif message.text == '💵Оплата при получении':
                user = Users.objects.get(name=message.chat.id)
                user.status = 'q'
                user.save(update_fields=['status'])
                with open('order_number.json', 'r') as f:
                    number = json.load(f)['number']
                text = f'*Заказ № {number}*\n\n'
                keyboard = types.ReplyKeyboardMarkup(True, False)
                keyboard.row('✅ Подтвердить и отправить')
                keyboard.row('⬅️ Отменить заявку')
                all_sum = 0
                for i in user.basket_set.all():
                    position_sum = i.count * i.price
                    text += f'*{i.name_product}*\n{i.count} x {i.price} = {position_sum} ₽\n'
                    all_sum += position_sum
                if user.delivery == '🚗 Привезти':
                    if all_sum < 2000:
                        text += '+_Доставка: 300 ₽_'
                        all_sum += 300
                text += f'\n\n*Итого:* {all_sum} ₽'
                bot.send_message(message.chat.id, text, parse_mode='markdown', reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, 'Выберите способ оплаты')

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == 'q')
        def confirm(message):
            if message.text == '⬅️ Отменить заявку':
                start_bot(message)
            elif message.text == '✅ Подтвердить и отправить':
                user = Users.objects.get(name=message.chat.id)
                user.status = '1'
                user.save(update_fields=['status'])
                with open('order_number.json', 'r') as f:
                    number = json.load(f)['number']
                number_order = json.dumps({"number": number + 1})
                with open('order_number.json', 'w') as f:
                    f.write(number_order)
                if user.delivery == '🏃 Заберу сам':
                    text = f'❗️ *Вам пришел заказ № {number}*\n\n👤Данные покупателя\n{user.nickname}, ' \
                           f'{user.mobile}\n📦Тип доставки:\n{user.delivery}\n\n-----\n🛒Товары:\n'
                else:
                    text = f'❗️ *Вам пришел заказ № {number}*\n\n👤Данные покупателя\n{user.nickname}, ' \
                           f'{user.mobile}\n📦Тип доставки:\n{user.delivery}\n' \
                           f'адрес доставки:{user.address}\n\n-----\n🛒Товары:\n'
                all_sum = 0
                for i in user.basket_set.all():
                    position_sum = i.count * i.price
                    text += f'*{i.name_product}*\n{i.count} x {i.price} = {position_sum} ₽\n'
                    all_sum += position_sum
                if user.delivery == '🚗 Привезти':
                    if all_sum < 2000:
                        text += '\n+ _Доставка: 300 ₽_'
                        all_sum += 300
                text += f'\n-----\n💰*Итого:* {all_sum} ₽\n ❌*НЕ ОПЛАЧЕНО*'
                user.basket_set.all().delete()
                bot.send_message(ID_ORDER_CHANNEL, text=text, parse_mode='markdown')
                bot.send_message(message.chat.id, "Ваш заказ оформлен", reply_markup=start_menu())
            else:
                bot.send_message(message.chat.id, 'Нажмите кнопку на клавиатуре')

        @bot.pre_checkout_query_handler(func=lambda query: True)
        def process_pre_checkout_query(pre_checkout_query):
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

        @bot.message_handler(content_types=['successful_payment'])
        def process_successful_payment(message: types.Message):
            user_id = Orders.objects.get(number_order=int(message.successful_payment.invoice_payload))
            Orders.objects.filter(number_order=int(message.successful_payment.invoice_payload)).delete()
            user = Users.objects.get(name=message.chat.id)
            bot.send_message(ID_ORDER_CHANNEL, user_id.user_order, parse_mode='markdown')
            bot.send_message(message.chat.id, "Ваш заказ оформлен")

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == 's')
        def user_problem(message):
            if message.text == '⬅️ Отменить заявку':
                start_bot(message)
            else:
                bot.forward_message(ID_HELP_CHANNEL, message.chat.id, message.message_id)
                Users.objects.filter(name=message.chat.id).update(status='1')
                bot.send_message(message.chat.id, 'Вопрос успешно отправлен', reply_markup=start_menu())

        @bot.message_handler(func=lambda message: Users.objects.get(name=message.chat.id).status == 'h')
        def info(message):
            if message.text == '🔙 Назад':
                Users.objects.filter(name=message.chat.id).update(status='1')
                help_user(message.chat.id)
            else:
                bot.delete_message(message.chat.id, message_id=message.message_id)

        @bot.message_handler(content_types=['text'])
        def bases(message):
            if message.text == '📋 Каталог':
                user = Users.objects.get(name=message.chat.id)
                user.status = '2'
                user.save(update_fields=["status"])
                bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=keyboard_catalog())
            elif message.text == "Начать с главного меню":
                start_bot(message)
            elif message.text == '📥 Корзина':
                user = Users.objects.get(name=message.chat.id)
                user_basket(user, message.chat.id)
            elif message.text == '📋 Главное меню':
                start_bot(message)
            elif message.text[:2] == '✏️':
                object_tea = re.sub(r'\s*[(]\d*\s*шт.[)]\s*', '', message.text[3:])
                user = Users.objects.get(name=message.chat.id)
                id_tea = user.basket_set.get(name_product=object_tea).id
                bot.send_message(message.chat.id, f'{message.text[3:]}', reply_markup=keyboard_count_tea(id_tea))
            elif message.text == '🗑️Очистить корзину':
                user = Users.objects.get(name=message.chat.id)
                user.basket_set.all().delete()
                bot.send_message(message.chat.id, 'Ваша корзина очищена', reply_markup=start_menu())
            elif message.text == '📳 Контакты':
                help_user(message.chat.id)
            elif message.text == '🏢 О компании':
                Users.objects.filter(name=message.chat.id).update(status='h')
                keyboard = types.InlineKeyboardMarkup()
                keyboard_two = types.ReplyKeyboardMarkup(True, False)
                keyboard_two.row('🔙 Назад')
                with open('photo_id.json', 'r') as f:
                    number_photo = json.load(f)
                but_1 = types.InlineKeyboardButton('◀️', callback_data='d|23')
                but_2 = types.InlineKeyboardButton('1/23', callback_data='empty')
                but_3 = types.InlineKeyboardButton('▶️', callback_data='f|2')
                keyboard.add(but_1, but_2, but_3)
                bot.send_message(message.chat.id, 'Информация о компании ', reply_markup=keyboard_two)
                bot.send_photo(message.chat.id, number_photo['1'], reply_markup=keyboard)
            elif message.text == '🚖 Оформить заказ':
                user = Users.objects.get(name=message.chat.id)
                order_registration(message.chat.id, user)
            elif message.text == '✉️Вопрос оператору':
                Users.objects.filter(name=message.chat.id).update(status='s')
                bot.send_message(message.chat.id, 'Задайте вопрос, оператор вам ответит в течение 5 минут',
                                 reply_markup=canceling_a_request())
            elif message.text == '🔙 Назад':
                Users.objects.filter(name=message.chat.id).update(status='1')
                bot.send_message(message.chat.id, 'Главное меню:', reply_markup=start_menu())
            elif message.text == '⬅️ Отменить заявку':
                Users.objects.filter(name=message.chat.id).update(status='1')
                bot.send_message(message.chat.id, 'Главное меню:', reply_markup=start_menu())
            else:
                bot.delete_message(message.chat.id, message.message_id)

        @bot.callback_query_handler(func=lambda c: True)
        def inline(c):
            user = Users.objects.get(name=c.message.chat.id)
            if user.status == '1':
                if c.data.split('|')[0] == 'add':
                    tea_object = user.basket_set.get(id=c.data.split('|')[1])
                    tea_object.count += 1
                    tea_object.save()
                    bot.edit_message_text(f'{tea_object.name_product} ({tea_object.count} шт.)', c.message.chat.id,
                                          c.message.message_id, reply_markup=keyboard_count_tea(c.data.split('|')[1]))
                elif c.data.split('|')[0] == 'down':
                    try:
                        tea_object = user.basket_set.get(id=c.data.split('|')[1])
                        if tea_object.count == 0:
                            keyboard = types.InlineKeyboardMarkup()
                            but_1 = types.InlineKeyboardButton(text='➕', callback_data=f"add|{c.data.split('|')[1]}")
                            but_2 = types.InlineKeyboardButton(text='➖', callback_data='empty')
                            but_3 = types.InlineKeyboardButton(text='✅', callback_data='ok')
                            keyboard.add(but_1, but_2)
                            keyboard.add(but_3)
                            bot.edit_message_text(f'{tea_object.name_product} ({tea_object.count} шт.)',
                                                  c.message.chat.id, c.message.message_id, reply_markup=keyboard)
                        else:
                            tea_object.count -= 1
                            tea_object.save(update_fields=['count'])
                            bot.edit_message_text(f'{tea_object.name_product} ({tea_object.count} шт.)',
                                                  c.message.chat.id, c.message.message_id,
                                                  reply_markup=keyboard_count_tea(c.data.split('|')[1]))
                    except exceptions.ObjectDoesNotExist:
                        bot.answer_callback_query(c.id, text="")

                elif c.data == 'ok':
                    user_basket(user, c.message.chat.id)
                    bot.delete_message(c.message.chat.id, c.message.message_id)
                elif c.data == 'empty':
                    bot.answer_callback_query(c.id, text="")
            elif c.data.split('|')[0] == 'd' or c.data.split('|')[0] == 'f':
                keyboard = types.InlineKeyboardMarkup()
                with open('photo_id.json', 'r') as f:
                    number_photo = json.load(f)
                if c.data.split('|')[1] == '1':
                    but_1 = types.InlineKeyboardButton('◀️', callback_data='d|23')
                    but_2 = types.InlineKeyboardButton('1/23', callback_data='empty')
                    but_3 = types.InlineKeyboardButton('▶️', callback_data='f|2')
                    keyboard.add(but_1, but_2, but_3)
                elif c.data.split('|')[1] == '23':
                    but_1 = types.InlineKeyboardButton('◀️', callback_data='d|22')
                    but_2 = types.InlineKeyboardButton('23/23', callback_data='empty')
                    but_3 = types.InlineKeyboardButton('▶️', callback_data='f|1')
                    keyboard.add(but_1, but_2, but_3)
                else:
                    but_1 = types.InlineKeyboardButton('◀️', callback_data=f'd|{int(c.data.split("|")[1]) - 1}')
                    but_2 = types.InlineKeyboardButton(f'{c.data.split("|")[1]}/23', callback_data='empty')
                    but_3 = types.InlineKeyboardButton('▶️', callback_data=f'f|{int(c.data.split("|")[1]) + 1}')
                    keyboard.add(but_1, but_2, but_3)
                bot.edit_message_media(types.InputMediaPhoto(number_photo[c.data.split("|")[1]]), c.message.chat.id,
                                       c.message.message_id, reply_markup=keyboard)
            else:
                bot.answer_callback_query(c.id, text="")
        bot.polling(none_stop=True)