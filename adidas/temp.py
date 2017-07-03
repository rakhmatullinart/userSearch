# -*- coding: utf-8 -*- ?
import sqlite3 as sqlite
from distutils import dist
import config
import telebot
import const


# from adidas import bot


def type_finder(item_type):
    type = const.item_types[item_type]
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("SELECT id FROM items WHERE type = ?", (str(type)))
    temp_items = cur.fetchall()
    items = []
    for item in temp_items:
        items.append(item_finder(item[0]))
    return items


def item_finder(item_id):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?", (str(item_id)))
    item = Item()
    item.set_full_data(*cur.fetchone())
    print(item.get_data())
    return item


def isSeller(user_id):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    cur.execute('SELECT user_id FROM clients WHERE user_id = (?)', (str(user_id),))
    if cur.fetchone():
        return True
    else:
        return False


def add_user(message):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE user_id = (?)", (message.from_user.id,))
    except Exception as e:
        config.log(Error=e, Text="DBTESTING ERROR")
    if not cur.fetchone():
        try:
            cur.execute("INSERT INTO users (user_id, first_name, last_name, username) VALUES (?,?,?,?)", (
                message.from_user.id,
                message.from_user.first_name,
                message.from_user.last_name,
                message.from_user.username))
            config.log(Text="User successfully added",
                       user=str(message.from_user.first_name + " " + message.from_user.last_name))
        except Exception as e:
            config.log(Error=e, Text="USER_ADDING_ERROR")
        db.commit()
    else:
        config.log(Error="IN_THE_BASE_YET",
                   id=message.from_user.id,
                   info=str(message.from_user.last_name) + " " + str(message.from_user.first_name),
                   username=message.from_user.username)


def add_client(message):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    login = message.text[1:]
    try:
        cur.execute("SELECT * FROM clients WHERE user_id = (?)", (message.from_user.id,))
    except Exception as e:
        config.log(Error=e, Text="DBTESTING ERROR")
    if not cur.fetchone():
        try:
            cur.execute("INSERT INTO clients (user_id) VALUES (?)", (message.from_user.id,))
            config.log(Text="Client successfully added",
                       user=str(message.from_user.first_name + " " + message.from_user.last_name))
        except Exception as e:
            config.log(Error=e, Text="CLIENT_ADDING_ERROR")
        db.commit()
    else:
        config.log(Error="IN_THE_BASE_YET",
                   id=message.from_user.id,
                   info=str(message.from_user.last_name) + " " + str(message.from_user.first_name),
                   username=message.from_user.username)


class Item:
    id = None
    type = None
    name = None
    company = None
    description = None
    seller = None
    price = None
    url = None
    data_types = ['id', 'type', 'name', 'company', 'price', 'description', 'url']

    def get_data(self):  # возвращает список , состоящий из структуры данных типа Item.data_types
        args = (self.name,
                self.company,
                self.price,
                self.description,
                self.url
                )
        return args

    def set_data(self, *args):
        try:
            self.name = args[0]
            self.company = args[1]
            self.price = args[2]
            self.description = args[3]
            self.url = args[4]
        except Exception as e:
            config.log(Error=e, text="SET_DATA_ERROR_OCCURED")

    def set_full_data(self, *args):
        try:
            self.name = args[2]
            self.id = args[0]
            self.type = args[1]
            self.company = args[3]
            self.price = args[4]
            self.description = args[5]
            self.url = args[6]
            self.seller = args[8]
            print('seller is ' + str(self.seller))
        except Exception as e:
            config.log(Error=e, text="SET_DATA_ERROR_OCCURED")

    def get_desc(self):
        data = self.get_data()
        description = str(data[1] + ' \t ' + str(data[0]) +
                          '\nPrice: ' + str(data[2]) + '\n' +
                          config.shorten(str(data[4])) + '\nDescription : ' + str(data[3]))
        return description

    def get_desc2(self):
        data = self.get_data()
        markup = telebot.types.InlineKeyboardMarkup()
        btn_name = telebot.types.InlineKeyboardButton(text=data[1] + " " + data[0], callback_data='.')
        btn_price = telebot.types.InlineKeyboardButton(text=str(data[2]) + ".00 RUB", callback_data='$' + str(self.id))
        btn_buy = telebot.types.InlineKeyboardButton(text="Buy", callback_data=str(self.id))
        markup.row(btn_name)
        markup.row(btn_price)
        markup.row(btn_buy)
        return markup

    def swap_desc(self):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_name = telebot.types.InlineKeyboardButton(text=self.company + " " + self.name, callback_data='.')
        markup.row(btn_name)
        btn_desc = telebot.types.InlineKeyboardButton(text=self.description, callback_data='return')
        markup.row(btn_desc)
        # btn_size = telebot.types.InlineKeyboardButton(text='Size:39-45', callback_data='.')
        # markup.row(btn_size)
        btn_buy = telebot.types.InlineKeyboardButton(text='Buy', callback_data=str(self.id))
        markup.row(btn_buy)
        return markup

    def delete(self):
        self.id = None
        self.type = None
        self.id = None
        self.name = None
        self.company = None
        self.price = None
        self.description = None
        self.url = None
        self.seller = None


def add_item(item, user_id):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("SELECT * FROM items WHERE (name) = (?)", (item.get_name(),))
    print(cur.fetchone())
    if not cur.fetchone():
        try:
            cur.execute("INSERT INTO items "
                        "(type, name, company, price, description, url, hash, seller_name) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        (item.type, item.name, item.company, item.price, item.description, item.url, user_id,
                         item.seller))
            db.commit()
        except Exception as e:
            config.log(Error=e, Text='ADDING_NEW_ITEM_ERROR')


# типа хэш но нифига не хэш, а просто id владельца
def find_users_items(user_id):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("SELECT * FROM items WHERE hash = ?", (str(user_id),))
    result = cur.fetchall()
    return result
