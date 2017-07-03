# -*- coding: utf-8 -*-?
import config
import os
import sqlite3
import telebot
import time
import urllib.request as urllib

import requests.exceptions as r_exceptions
from requests import ConnectionError

import const, base, markups, files, temp

bot = telebot.TeleBot(config.token)
uploaded_items = {}


# Обработка /start команды - ветвление пользователей на покупателя и продавца
@bot.message_handler(commands=['start'])
def start(message):
    base.add_user(message)
    if base.is_seller(message.from_user.id):
        bot.send_message(message.chat.id, const.welcome_celler, reply_markup=markups.start())
    else:
        bot.send_message(message.chat.id, const.welcome_client, reply_markup=markups.show_types(message.chat.id))


# Выдача меню с типами товаров
@bot.message_handler(regexp='Меню')
def client_panel(message):
    bot.send_message(message.chat.id,'Выберите категорию:', reply_markup=markups.show_types(message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == 'client_panel')
def client_panel(call):
    bot.edit_message_text(const.welcome_client, chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markups.show_types(call.message.chat.id))

# Запуск обработчика продавцов
@bot.callback_query_handler(func=lambda call: call.data == 'celler_panel')
def celler_panel(call):
    bot.edit_message_text('[Отправьте нам xls-файл с вашими товарами.\n'
                          'Руководство: ][Link](http://telegra.ph/Kak-otpravlyat-vashi-tovary-cherez-xls-fajl-01-21)',
                          call.message.chat.id, call.message.message_id,
                          parse_mode='Markdown', reply_markup=markups.edit())
    # config.goRegister = True


# Отображение товаров и занесение их в кэш
@bot.callback_query_handler(func=lambda call: call.data in base.give_menu())
def show_items(call):
    for item in base.type_finder(call.data):
        key = item.get_desc2()
        # callback_button = telebot.types.InlineKeyboardButton(text='Buy', callback_data=str(item.id))
        uploaded_items[str(item.id)] = 0
        print(uploaded_items)
        # key.row(callback_button)

        try:
            url = item.url
            photo = open("temp.jpg", 'w')  # Инициализация файла
            photo.close()
            photo = open("temp.jpg", 'rb')
            urllib.urlretrieve(url, "temp.jpg")
            bot.send_photo(chat_id=call.message.chat.id, photo=photo)
            photo.close()
            os.remove("temp.jpg")
        except Exception:
            bot.send_message(call.message.chat.id, 'К сожалению, фотография отсутствует')
        bot.send_message(call.message.chat.id, item.description, reply_markup=key, disable_web_page_preview=True)
    bot.send_message(call.message.chat.id, "Удачных покупок!", reply_markup=markups.make_bill())


# Отображение текущей корзины и вопрос о совершении транзакции
@bot.message_handler(regexp="Оформить заказ")
def make_bill(message):
    res = ""
    items = uploaded_items.copy()
    f = False
    while items:
        next_item = items.popitem()
        if next_item[1] > 0:
            f = True
            item = base.item_finder(int(next_item[0]))
            print(item)
            res = str(item.company + " " + str(item.name) + "\nPrice: " + str(
                item.price) + "\nKol-vo: " + str(next_item[1]))
    if not f:
        bot.send_message(message.chat.id, "У вас пока нет покупок..",
                         reply_markup=markups.show_types(message.chat.id))
    else:
        bot.send_message(const.admin_id, "Жулик, не воруй!")
        # bot.send_message(const.admin_id, res + '\n'
        #                                      'from user : @'
        #                 + message.from_user.username)
        bot.send_message(message.chat.id, res)
        bot.send_message(message.chat.id, 'Confirm transaction?', reply_markup=markups.concern())


# Запуск обработки транзакции


@bot.callback_query_handler(func=lambda call: call.data == '#Yes')
def transaction(call):
    message = "К ожалению, онлайн-системы оплаты пока что находятся в разработке.\n" \
              "Вместо этого, вы можете обсудить средства перевода денег с продавцом товаров\n"
    print(uploaded_items)
    items = uploaded_items
    while items:
        print('processing names...')
        item = items.popitem()
        if item[1] > 0:
            it = base.item_finder(item[0])
            message += str(it.company) + str(it.name) + ' : ' + '@' + str(it.seller)
            bot.send_invoice(call.message.chat.id, it.name, it.description)
            bot.send_invoice()
    bot.edit_message_text(message, call.message.chat.id, call.message.message_id)



    # transactions.get_transaction_link(uploaded_items)
    # try:
    #
    # except Exception as e:
    #    config.log(Error=e, Text='TRANSACTION_ERROR_OCCURED')


# Обработка первой покупки товара
@bot.callback_query_handler(func=lambda call: call.data in uploaded_items)
def callback_handler(call):
    uploaded_items[str(call.data)] += 1
    print('uploaded_items : ' + str(uploaded_items))
    print('callback_handler.call.data = ' + str(call.data))
    markup = markups.add(call.data)
    numb = telebot.types.InlineKeyboardButton(str(uploaded_items.get(call.data)), callback_data='.')
    markup.add(numb)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


# Добавление ещё одной еденицы товара в корзину


@bot.callback_query_handler(func=lambda call: str(call.data[0]) == '+')
def handle_plus(call):
    try:
        uploaded_items[str(int(call.data[1:]))] += 1
    except KeyError as e:
        config.log(Error=e, text='WRONG_KEY')
    markup = markups.add(call.data[1:])
    numb = telebot.types.InlineKeyboardButton(str(uploaded_items.get(str(int(call.data[1:])))), callback_data='.')
    markup.row(numb)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    print('uploaded items = ' + str(uploaded_items))


# Удаление единицы товара из корзины


@bot.callback_query_handler(func=lambda call: str(call.data[0]) == '-')
def handle_minus(call):
    try:
        if uploaded_items[str(int(call.data[1:]))]:
            uploaded_items[str(int(call.data[1:]))] -= 1
    except KeyError as e:
        config.log(Error=e, text='WRONG_KEY')
    if uploaded_items[str(int(call.data[1:]))] == 0:
        key = (base.item_finder(call.data[1:])).get_desc2()

        key.row_width = 1
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=key)
        return
    markup = markups.add(call.data[1:])
    numb = telebot.types.InlineKeyboardButton(str(uploaded_items.get(str(int(call.data[1:])))), callback_data='.')
    markup.row(numb)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    print('uploaded items = ' + str(uploaded_items))
    return


# Отображение типов товаров пользователю


# @bot.callback_query_handler(func=lambda call: call.data == '&Yes')
# def handle_not_admin(call):
#     bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.show_types())





@bot.message_handler(content_types=['document'])
def handle_xl(message):
    files.get_xls_data(bot.get_file(message.document.file_id), message.from_user.id, message.from_user.username)


# Добавление категории
@bot.callback_query_handler(func=lambda call: call.data == 'add_kat')
def handle_add_kat(call):
    sent = bot.send_message(call.message.chat.id, "Введите название категории", reply_markup=markups.return_to_menu())
    bot.register_next_step_handler(sent, base.add_kat)


# Удаление категории
@bot.callback_query_handler(func=lambda call: call.data == 'delete_kat')
def handle_delete_kat(call):
    bot.edit_message_text("Выберите категорию для удаления", call.message.chat.id,
                          call.message.message_id, reply_markup=markups.delete_kat())


@bot.callback_query_handler(func=lambda call: call.data[0] == '?')
def handle_delete_this_kat(call):
    db = sqlite3.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("DELETE FROM categories WHERE name = ?", (str(call.data[1:]),))
    db.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_kat())

    print('deleted')


# дальше идет какое-то дерьмо


# Добавление товара.


# Выбор типа товара
@bot.callback_query_handler(func=lambda call: call.data == 'add_item')
def handle_add_item_type(call):
    new_item = temp.Item()
    const.new_items_user_adding.update([(call.message.chat.id, new_item)])
    sent = bot.send_message(call.message.chat.id, "Выберите тип товара:", reply_markup=markups.add_item())
    bot.register_next_step_handler(sent, base.add_item_kategory)
    const.user_adding_item_step.update([(call.message.chat.id, "Enter name")])


# Ввод наименования товара
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Enter name")
def handle_add_item_name(message):
    sent = bot.send_message(message.chat.id, "Введите наименование товара")
    bot.register_next_step_handler(sent, base.add_item_name)
    const.user_adding_item_step[message.chat.id] = "Enter company"


# Ввод компании
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Enter company")
def handle_add_item_company(message):
    sent = bot.send_message(message.chat.id, "Введите компанию")
    bot.register_next_step_handler(sent, base.add_item_company)
    const.user_adding_item_step[message.chat.id] = "Enter price"


# Ввод цены
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Enter price")
def handle_add_item_price(message):
    sent = bot.send_message(message.chat.id, "Введите цену")
    bot.register_next_step_handler(sent, base.add_item_price)
    const.user_adding_item_step[message.chat.id] = "Enter description"


# Ввод описания
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Enter description")
def handle_add_item_description(message):
    sent = bot.send_message(message.chat.id, "Введите описание")
    bot.register_next_step_handler(sent, base.add_item_description)
    const.user_adding_item_step[message.chat.id] = "Enter URL"


# Ввод URL
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Enter URL")
def handle_add_item_url(message):
    sent = bot.send_message(message.chat.id, "Введите URL картинки")
    bot.register_next_step_handler(sent, base.add_item_url)
    const.user_adding_item_step[message.chat.id] = "End"
    # const.user_adding_item_step.pop(message.chat.id)


# Конец добавления товара
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "End")
def handle_add_item_end(message):
    bot.send_message(message.chat.id, "Добавлено!\n Меню:", reply_markup=markups.show_types(message.chat.id))
    const.user_adding_item_step.pop(message.chat.id)


# Удаление товара
@bot.callback_query_handler(func=lambda call: call.data == 'delete_item')
def handle_delete_item(call):
    bot.edit_message_text("Выберите товар для удаления", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_item(call.message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data[0] == '^')
def handle_delete_from_db(call):
    db = sqlite3.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (str(call.data[1:])))
    db.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_item(call.message.chat.id))
    print('deleted')


# Сохранение PayPal логина продавца


@bot.message_handler(content_types=['text'], func=lambda message: message.text[0] == '%' and config.goRegister == True)
def handle_paypal_login(message):
    if not base.is_seller(message.from_user.id):
        base.add_client(message)


@bot.callback_query_handler(func=lambda call: call.data[0] == '$')
def give_desc(call):
    # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=item.swap_desc())
    bot.edit_message_text("Здесь текст", call.message.chat.id, call.message.message_id, )


# Запуск бота


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except ConnectionError as expt:
        config.log(Exception='HTTP_CONNECTION_ERROR', text=expt)
        print('Connection lost..')
        time.sleep(30)
        continue
    except r_exceptions.Timeout as exptn:
        config.log(Exception='HTTP_REQUEST_TIMEOUT_ERROR', text=exptn)
        time.sleep(5)
        continue
