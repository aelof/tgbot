#
# -*- coding: utf-8 -*-
import telebot
from telebot import types

import json
import requests
import config
from config import kb_getphone, kb_start, ikb1,manual, short, startmessage

tb = telebot.TeleBot(config.token)
URL_ED = config.URL_ED

#

@tb.message_handler(commands=['start', 'short', 'clear',  'god'])
def start(message):
    mci = message.chat.id
    if message.text == '/start':
        tb.send_message(mci, startmessage, parse_mode='Markdown', reply_markup=kb_start,
                        disable_web_page_preview=True)
    elif message.text == '/short':
        tb.send_message(mci, short, parse_mode='Markdown', reply_markup=kb_start)
    elif message.text == '/clear':
        for i in range(100):
            try:
                tb.delete_message(message.chat.id, message.message_id - i)  # delete all msgs
            except:
                i += 1
    if message.text == '/god':
        tb.send_message(mci, '\r\n\r\n/clear Режим Бога активирован')

    # tracing new users / отследживание новых посетителей
    if message.chat.username:
        analitic = {'type': 'savelog', 'chat_id': mci, 'nic': message.chat.username,
                    'firstname': message.chat.first_name, 'token': config.token_ed}
        if mci not in [405529066, 239090651]:
            tb.send_message('@new_visit', f'new:{message.chat.first_name},{message.chat.username};id = {mci}')

    else:
        analitic = {'type': 'savelog', 'chat_id': mci, 'firstname': message.chat.first_name, 'token': config.token_ed}
        if mci not in [405529066, 239090651]:
            tb.send_message('@new_visit', f'new:{message.chat.first_name}:{mci}')
    anal = requests.get(URL_ED, params=analitic)


# heandler phome number /заправшивает номер клиента
@tb.message_handler(content_types=['contact', 'voice'])
def get_number(message):
    mci = message.chat.id
    global ttime
    global data_to_us
    if message.contact:
        ttime = message.date
        phone = message.contact.phone_number
        data_to_us = {'type': 'sendorder', 'chat_id': mci, 'phone': phone, 'token': config.token_ed}
        kbrd_voice = types.InlineKeyboardMarkup()
        btn1_voice = types.InlineKeyboardButton('Деталей нет', callback_data='pass_voice')
        kbrd_voice.add(btn1_voice)
        tb.send_message(mci, '*Отправьте голосовое с указанием деталей*\r\n\r\n'
                             '(можете сказать сколько грамм мяса или сыра Вам отрезать или убрать, по ошибке добавленный товар)'
                             '\r\n\r\n_Принимается только_ *первое* _голосовое сообщение_',
                        parse_mode='Markdown', reply_markup=kbrd_voice)
        tb.delete_message(mci, message.message_id)
    if message.voice:
        ttime2 = message.date
        try:
            if ttime2 > ttime:
                tb.forward_message("@deliiivery", mci, message.message_id)
                tb.send_message(message.chat.id,
                                '*Ваш заказ сформирован!\r\nМенеджер свяжется c Вами для уточнения деталей*',
                                reply_markup=kb_start, parse_mode='Markdown')
                tb.send_message(message.chat.id, 'Давайте вместе улучшим этот сервис!'
                                                 'Расскажите, что можно улучшить'
                                                 '\r\n https://t.me/joinchat/AAAAAElAAlQ_waJRJmk8LQ')
                # requests.post(URL_ED, params=data_to_us)
        except:
            tb.send_message(mci, manual, parse_mode='Markdown')



# pass_voice
@tb.callback_query_handler(func=lambda call: call.data == 'pass_voice')
def voice(call):
    cmci = call.message.chat.id
    if call.data == 'pass_voice':
        # tb.delete_message(cmci, call.message.message_id)
        tb.send_message(cmci, '*Ваш заказ сформирован!\r\nМенеджер свяжется c Вами для уточнения деталей*',
                        reply_markup=kb_start, parse_mode='Markdown')
        tb.send_message(cmci, 'Давайте вместе сделаем самую удобную доставку!\r\nРасскажите, что можно улучшить '
                              '\r\n https://t.me/joinchat/AAAAAElAAlQ_waJRJmk8LQ')
        tb.answer_callback_query(call.id, 'Ваш заказ оформлен!', show_alert=True)

        try:
            requests.post(URL_ED, params=data_to_us)
        except:
            pass


# erase shoping cart
@tb.callback_query_handler(func=lambda call: call.data == 'erase_cart')
def cart0(call):
    cmci = call.message.chat.id
    if call.data == 'erase_cart':
        tb.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                 text="Корзина очищается")

        tb.edit_message_text(chat_id=cmci, message_id=call.message.message_id,
                             text='Вы очистили корзину', reply_markup=None)
        data_erase_cart = {'type': 'clearcart', 'chat_id': cmci, 'token': config.token_ed}
        z = requests.post(URL_ED, params=data_erase_cart)


# shoping cart / Корзина
@tb.message_handler(func=lambda message: message.text == 'Корзина 🛒')
def shoping_cart(message):
    mci = message.chat.id
    kbrd_cart = types.InlineKeyboardMarkup()
    btn1_cart = types.InlineKeyboardButton("Очистить корзину", callback_data='erase_cart')
    btn2_cart = types.InlineKeyboardButton("Заказать!", callback_data='offer', )
    kbrd_cart.add(btn1_cart, btn2_cart)
    global r_cart
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


@tb.callback_query_handler(func=lambda call: call.data == 'offer')
def off_er(call):
    if r_cart['total_price'] > 1200:
        cmci = call.message.chat.id
        tb.answer_callback_query(callback_query_id=call.id, text='Данные для доставки ', show_alert=False)
        tb.send_message(cmci, '*Поделитесь номером телефона*\n\n'
                              'нажм. *Поделиться* на кливиатуре\n\n',
                        parse_mode='Markdown', reply_markup=kb_getphone, )
        global mpd  # message with  phone number delete
        mpd = call.message.message_id + 1
        # tb.delete_message(call.message.chat.id, mpd)
    else:
        cmci = call.message.chat.id
        tb.answer_callback_query(callback_query_id=call.id, text='Сумма заказа меньше 1200', show_alert=False)
        kb_cats = types.InlineKeyboardMarkup(row_width=3)
        kb_cats.add(*ikb1)
        tb.send_message(cmci, 'Добавьте ещё продуктов, чтобы сумма заказа была *от 1200 рублей*',
                        parse_mode='Markdown', reply_markup=kb_cats, )


@tb.message_handler(content_types='text')
def show_categories(message):
    mci = message.chat.id

    if message.text == 'Заказать продукты 🍽':
        global ms1
        ms1 = message.message_id
        kb_cats = types.InlineKeyboardMarkup(row_width=3)
        kb_cats.add(*ikb1)
        tb.send_message(mci, "Минимальная сумма заказа *1200 рублей.* \r\n\r\nВыберите категорию: \r\n  ",
                        parse_mode='Markdown', reply_markup=kb_cats)
    elif message.text == 'Инструкция 📙':
        tb.send_message(mci, manual, parse_mode='Markdown')
    elif message.text == 'Контакты 📱':
        tb.send_message(mci, contacts, parse_mode='Markdown', disable_web_page_preview=True)
    elif message.text == '< В меню':
        tb.send_message(mci, 'Вы перешли в главное меню\r\nТовары в корзине', reply_markup=kb_start)
    else:
        tb.send_message(mci, manual, parse_mode='Markdown')


# heandler for button "back to categories"
@tb.callback_query_handler(func=lambda call: call.data == 'back_to_cat')
def back_to_cat(call):
    cmci = call.message.chat.id
    if call.data == 'back_to_cat':
        tb.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Назад к категориям")
        kb_cats = types.InlineKeyboardMarkup(row_width=3)
        kb_cats.add(*ikb1)
        try:
            tb.delete_message(cmci, message_id=mid)  # message index to delete
        except:
            pass
        tb.send_message(cmci, "Выберите категорию: ", reply_markup=kb_cats)
        tb.answer_callback_query(call.id, 'Чат успешно очищен', show_alert=False)


# heandler for all call
@tb.callback_query_handler(func=lambda call: True)
def show_inline(call):
    cmci = call.message.chat.id
    value_id = str(call.data)

    if 'cat' in value_id:
        tb.answer_callback_query(callback_query_id=call.id, text='Загрузка товаров ', show_alert=False)
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
                item = types.InlineKeyboardButton(f'{i["name"]} - {i["price"]}р.',
                                                  callback_data="prod" + str(i["id"]))
            kbrd_products.add(item)

        if 'next_offset' in r1:
            # Category has more products let's' show them
            kb_showmore = types.InlineKeyboardButton('Показать ещё ➡',
                                                     callback_data='cat' + str(cat_id) + '|offset' + str(
                                                         r1['next_offset']))

        kbrd_back_to_cat = types.InlineKeyboardButton('⬅ В категории', callback_data='back_to_cat')
        try:
            kbrd_products.add(kbrd_back_to_cat, kb_showmore)
        except:
            kbrd_products.add(kbrd_back_to_cat)
        global mid
        mid = call.message.message_id
        tb.edit_message_text(chat_id=cmci, message_id=call.message.message_id,
                             text=f'Товары в категории:', reply_markup=kbrd_products)

    elif 'prod' in value_id:
        answer = f"Добавлено в корзину."  # Сумма заказа: {r1['total_price']} р."
        tb.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                 text=answer)
        prod_id = value_id.replace('prod', '')
        data_addtocart = {'type': 'addtocart', 'chat_id': cmci, 'prod_id': prod_id, 'token': config.token_ed}
        r1 = requests.get(URL_ED, params=data_addtocart)
        r1 = r1.json()
        answer1 = f"Сумма заказа: {r1['total_price']} р."

        tb.answer_callback_query(callback_query_id=call.id, show_alert=False, text=answer1)


# start bot
if __name__ == "__main__":
    tb.polling(none_stop=True)