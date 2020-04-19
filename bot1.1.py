# -*- coding: utf-8 -*-

import telebot
from telebot import types

import json
import requests
import config

tb = telebot.TeleBot(config.token)
URL_ED = config.URL_ED

manual = '''
*Инструкция пользования:*\r\n
Для того, чтобы добавить товар в корзину нажм. на кнопку с названием продукта. \r\n
Хотите добавить второй такой же товар - нажмите на продукт ещё раз .\r\n
Весь заказ в любой момент можно просмотреть нажав. *Корзина* 🧺
Хотите оформить заказ - нажм. *заказать*, после этого
Вам будет предложено поделиться номером телефона и оставить голосовое 
сообщения для внесения поправок в заказ _напр. "Отрежьте, пожалуйста,  350 гр. сыра "Черный Принц!" 
(по умолчанию добавляет 1 кг.)_
\r\nВот и всё заказ сформирован. Далее с Вами свяжутся, для уточнения деталей доставки. 
\r\n/short - показать сокрщения
'''
startmessage = '''
Бот доставки 🚙 продуктов по Геленджику.\n
Поможет заказать продукты домой 🏠
Ассортимент пока мал, но постоянно пополняется !\n
_Рекомендуется ознакомиться с его работой (нажм."Инструкция")_',
'''
short = '''
*Сокращения:*
б/к - без кости
c/м - свежезамороженные
подбед. - подбедерок
'''


@tb.message_handler(commands=['start', 'short'])
def start(message):
    # buttons main menu
    kbrd_start = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1_start = types.KeyboardButton('Заказать продукты 🍽')
    btn2_start = types.KeyboardButton('Корзина 🧺')
    btn3_start = types.KeyboardButton('Инструкция 📕')
    kbrd_start.add(btn1_start)
    kbrd_start.add(btn3_start, btn2_start)
    mci = message.chat.id
    if message.text == '/start':
        tb.send_message(mci, startmessage, parse_mode='Markdown', reply_markup=kbrd_start)
    elif message.text == '/short':
        tb.send_message(mci, short, parse_mode='Markdown', reply_markup=kbrd_start)


# heandler phome nimber /заправшивает номер клиента
@tb.message_handler(content_types=['contact', 'voice'])
def get_number(message):
    mci = message.chat.id
    global ttime
    if message.contact:
        ttime = message.date
        phone = message.contact.phone_number
        global data_to_us
        data_to_us = {'type': 'sendorder', 'chat_id': mci, 'phone': phone, 'token': config.token_ed}
        kbrd_voice = types.InlineKeyboardMarkup()
        btn1_voice = types.InlineKeyboardButton('Деталей нет', callback_data='pass_voice')
        kbrd_voice.add(btn1_voice)
        tb.send_message(mci, 'Отправьте голосовое с указанием деталей\r\n\r\n'
                             '(можете сказать сколько грамм мяса или сыра Вам отрезать или другие детали)'
                             '\r\n\r\n_Принимается только_ *первое* _голосовое сообщение_',
                        parse_mode='Markdown', reply_markup=kbrd_voice)
    if message.voice:
        ttime2 = message.date
        try:
            if ttime:
                if ttime2 > ttime:
                    kbrd_start2 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                    btn1_start = types.KeyboardButton('Заказать продукты 🍽')
                    btn2_start = types.KeyboardButton('Корзина 🧺 ')
                    btn3_start = types.KeyboardButton('Инструкция 📕')
                    kbrd_start2.add(btn1_start)
                    kbrd_start2.add(btn3_start, btn2_start)
                    tb.forward_message("@deliiivery", mci, message.message_id)
                    tb.send_message(message.chat.id, '*Ваш заказ сформирован!\r\nМенеджер свяжется c Вами для уточнения деталей*',
                                    reply_markup=kbrd_start2, parse_mode='Markdown')
                    tb.send_message(call.message.chat.id, 'Давайте вместе улучшим этот сервис!'
                                                          'Расскажите, что можно улучшить'
                                                          '\r\n https://t.me/joinchat/AAAAAElAAlQ_waJRJmk8LQ')
                    p = requests.post(URL_ED, params=data_to_us)
        except:
            tb.send_message(mci, manual, parse_mode='Markdown')


# pass_voice
@tb.callback_query_handler(func=lambda call: call.data == 'pass_voice')
def voice(call):
    if call.data == 'pass_voice':
        tb.delete_message(call.message.chat.id, call.message.message_id)
        kbrd_start2 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1_start = types.KeyboardButton('Заказать продукты 🍽')
        btn2_start = types.KeyboardButton('Корзина 🧺')
        btn3_start = types.KeyboardButton('Инструкция 📕')
        kbrd_start2.add(btn1_start)
        kbrd_start2.add(btn3_start, btn2_start)
        tb.send_message(call.message.chat.id, '*Ваш заказ сформирован!\r\nМенеджер свяжется c Вами для уточнения деталей*',
                        reply_markup=kbrd_start2, parse_mode='Markdown')
        tb.send_message(call.message.chat.id, 'Давайте вместе улучшим этот сервис!'
                                              'Расскажите, что можно улучшить'
                                              '\r\n https://t.me/joinchat/AAAAAElAAlQ_waJRJmk8LQ')

        try:
            p = requests.post(URL_ED, params=data_to_us)
        except:
            pass

# erase shoping cart
@tb.callback_query_handler(func=lambda call: call.data == 'erase_cart')
def cart0(call):
    if call.data == 'erase_cart':
        cmci = call.message.chat.id
        data_erase_cart = {'type': 'clearcart', 'chat_id': cmci, 'token': config.token_ed}
        z = requests.post(URL_ED, params=data_erase_cart)
        tb.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                 text="Корзина ощищена")

        tb.edit_message_text(chat_id=cmci, message_id=call.message.message_id,
                             text='Вы очистили корзину', reply_markup=None)


# shoping cart / Корзина
@tb.message_handler(func=lambda message: message.text == 'Корзина 🧺')
def shoping_cart(message):
    kbrd_cart = types.InlineKeyboardMarkup()
    btn1_cart = types.InlineKeyboardButton("Очистить корзину", callback_data='erase_cart')
    btn2_cart = types.InlineKeyboardButton("Заказать!", callback_data='offer', )
    kbrd_cart.add(btn1_cart, btn2_cart)
    mci = message.chat.id
    data_cart = {'type': 'getcart', 'chat_id': mci, 'token': config.token_ed}
    r_cart = requests.get(URL_ED, params=data_cart)
    r_cart = r_cart.json()
    if r_cart['products']:
        answer = '*Ваш заказ:* \r\n\r\n'
        i = 1
        check = 0
        for id in r_cart['products']:
            product = r_cart['products'][id]
            check = check + product["price"]
            answer += f' {i}. {product["name"]} x {product["quantity"]}   \r\n\r*= {product["price"]}р.*    \r\n\r\n'
            i += 1
        answer = f'{answer} \r\n Сумма заказа: *{check} рублей* '
        tb.send_message(mci, answer, parse_mode='Markdown', reply_markup=kbrd_cart)
    else:
        tb.send_message(mci, "Корзина пуста\r\nЗакажите что-нибудь:)")


@tb.message_handler(content_types='text')
def show_categories(message):
    mci = message.chat.id
    if message.text == 'Заказать продукты 🍽':
        kbrd_cats = types.InlineKeyboardMarkup(row_width=3)
        data_cat = {'type': 'categories', 'token': config.token_ed}
        r0 = requests.get(URL_ED, params=data_cat)
        list = []
        r0 = r0.json()
        for i in r0:
            item = types.InlineKeyboardButton(str(i['name']), callback_data='cat' + str(i['id']))
            list.append(item)
        kbrd_cats.add(*list)
        tb.send_message(mci, "Минимальная сумма заказа *1200 рублей.* \r\n\r\nВыберите категорию: \r\n  ",
                        parse_mode='Markdown', reply_markup=kbrd_cats)
    elif message.text == 'Инструкция 📕':
        tb.send_message(mci, manual, parse_mode='Markdown')
    elif message.text == 'Назад':
        kbrd_start = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1_start = types.KeyboardButton('Заказать продукты 🍽')
        btn2_start = types.KeyboardButton('Корзина 🧺')
        btn3_start = types.KeyboardButton('Инструкция 📕')
        kbrd_start.add(btn1_start)
        kbrd_start.add(btn3_start, btn2_start)
        tb.send_message(mci, 'Вы перешли в главное меню\r\nКорзина заполнена', reply_markup=kbrd_start)
    else:
        tb.send_message(mci, manual, parse_mode='Markdown')


# heandler for button "back to categories"
@tb.callback_query_handler(func=lambda call: call.data == 'back_to_cat')
def back_to_cat(call):
    cmci = call.message.chat.id
    if call.data == 'back_to_cat':
        tb.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Назад в категории")
        kbrd_cats = types.InlineKeyboardMarkup(row_width=3)
        payload = {'type': 'categories', 'token': config.token_ed}
        r = requests.get(URL_ED, params=payload)
        r = r.json()
        list2 = []
        for i in r:
            item = types.InlineKeyboardButton(str(i['name']), callback_data='cat' + str(i['id']))
            list2.append(item)
        kbrd_cats.add(*list2)
        try:
            tb.delete_message(cmci, message_id=mid)  # message index to delete
        except:
            pass
        tb.send_message(cmci, "Выберите категорию: ", reply_markup=kbrd_cats)


# heandler for all call back
@tb.callback_query_handler(func=lambda call: True)
def show_inline(call):
    cmci = call.message.chat.id
    value_id = str(call.data)

    if 'cat' in value_id:
        data_products = {'type': 'products', 'token': config.token_ed}
        if 'offset' in value_id:
            # Was clicked on show more products
            value_params = value_id.split('|')
            cat_id = value_params[0].replace('cat', '')
            data_products['offset'] = value_params[1].replace('offset', '')
        else:
            # Was clicked on category
            cat_id = value_id.replace('cat', '')
        data_products['cat_id'] = cat_id
        kbrd_products = types.InlineKeyboardMarkup(row_width=2)
        r1 = requests.get(URL_ED, params=data_products)
        r1 = r1.json()
        for i in r1['products']:
            if i['weight'] != None:
                item = types.InlineKeyboardButton(f'{i["name"]}-{i["price"]}р./{i["weight"]}г.',
                                                  callback_data="prod" + str(i["id"]))
            else:
                item = types.InlineKeyboardButton(f'{i["name"]} - {i["price"]}р.', callback_data="prod" + str(i["id"]))
            kbrd_products.add(item)

        if 'next_offset' in r1:
            # Category has more products let's' show them
            kbrd_products.add(types.InlineKeyboardButton('Показать ещё ➡️',
                                                         callback_data='cat' + str(cat_id) + '|offset' + str(
                                                             r1['next_offset'])))
        kbrd_back_to_cat = types.InlineKeyboardButton('⬅️ В категории', callback_data='back_to_cat')
        kbrd_products.add(kbrd_back_to_cat)
        global mid
        mid = call.message.message_id
        tb.edit_message_text(chat_id=cmci, message_id=call.message.message_id,
                             text=f'\r\nТовары в категории:\r\n\r\n\r\n',
                             # *{namecat(value_id)} \r\n*_руб/кг(шт)_ ',
                             parse_mode='Markdown', reply_markup=kbrd_products)

    elif 'prod' in value_id:
        prod_id = value_id.replace('prod', '')
        data_addtocart = {'type': 'addtocart', 'chat_id': cmci, 'prod_id': prod_id, 'token': config.token_ed}
        r1 = requests.get(URL_ED, params=data_addtocart)
        r1 = r1.json()
        if 'new_product_id' not in r1:
            answer = 'Товар уже есть в корзине'
        else:
            answer = f"Добавлено в корзину. Сумма заказа: {r1['total_price']} р."
        tb.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                 text=answer)

    if call.data == 'offer':
        kbrd_getphone = types.ReplyKeyboardMarkup(resize_keyboard=1, one_time_keyboard=True)
        btn1_getphone = types.KeyboardButton('Поделиться ', request_contact=True)
        btn2_getphone = types.KeyboardButton('Назад')
        kbrd_getphone.add(btn2_getphone, btn1_getphone)
        tb.send_message(cmci, 'Поделитесь номером телефоном\n\n'
                              '_(Это нужно для уточнения деталей доставки)_', parse_mode='Markdown',
                        reply_markup=kbrd_getphone, )
        kbrd_start = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)


# start bot

tb.polling(none_stop=True)
