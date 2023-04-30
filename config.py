API_TOKEN = "6206288855:AAHnLFfNWO-4X-fiXb58CSGeFBkFVyz9Mj4"

COMMANDS = ['/start', '/all']

'''
import datetime

import telebot

import config
from db import add_order, get_all_orders, get_order_dates

bot = telebot.TeleBot(config.API_TOKEN)

# Declare global variables
date = None
time = None
address = None
acreage = None
phone_number = None


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Пожалуйста, выберите дату заказа.", reply_markup=generate_calendar())


@bot.message_handler(commands=['all'])
def all_orders(message):
    dates = get_order_dates()
    if dates:
        bot.send_message(message.chat.id, "Выберите дату для просмотра заказов:",
                         reply_markup=generate_dates_buttons(dates))
    else:
        bot.send_message(message.chat.id, "Заказов пока нет.")


def generate_dates_buttons(dates):
    markup = telebot.types.InlineKeyboardMarkup()
    for date in dates:
        markup.row(telebot.types.InlineKeyboardButton(date, callback_data=f"date_{date}"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith('date_'))
def handle_order_date(call):
    date = call.data.replace("date_", "")
    orders = get_all_orders(date)
    if orders:
        orders.sort(
            key=lambda x: x[2] if x[2] else "")  # Сортировка заказов по времени, None заменяется на пустую строку
        response = f"Список всех заказов на {date}:\n\n"
        for order in orders:
            response += f"ID: {order[0]}, Время: {order[2]}, Адрес: {order[3]}, Количество соток: {order[4]}, Номер телефона: {order[5]}\n"
        bot.send_message(call.message.chat.id, response)
    else:
        bot.send_message(call.message.chat.id, f"На {date} заказов нет.")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global date, time, acreage, address, phone_number
    try:
        if call.message:
            if call.data.startswith("acreage_"):
                acreage = call.data.replace("acreage_", "")
                bot.send_message(call.message.chat.id,
                                 f'Спасибо, ваш заказ принят. Дата заказа: {date}, время заказа: {time}, адрес: {address}, количество соток: {acreage}, номер телефона: {phone_number}')
                add_order(date, time, address, int(acreage), phone_number)
            elif call.data.startswith("time_"):
                time = call.data.replace("time_", "")
                bot.send_message(call.message.chat.id, "Что бы сделать заказ, пожалуйста, укажите адрес.")
                bot.register_next_step_handler(call.message, get_address)
            elif call.data.startswith("date_"):
                # обработка выбора даты при просмотре заказов реализована в функции handle_order_date
                return
            elif call.data:
                date = call.data
                bot.send_message(call.message.chat.id, "Пожалуйста, выберите время заказа.",
                                 reply_markup=generate_time_buttons(date))
    except Exception as e:
        bot.reply_to(call.message, 'Ошибка. Пожалуйста, попробуйте еще раз.')


def generate_time_buttons(selected_date):
    all_orders_on_date = get_all_orders(selected_date)
    booked_times = [order[2] for order in all_orders_on_date]

    markup = telebot.types.InlineKeyboardMarkup()
    time_slots = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
                  "19:00", "20:00", "21:00", "22:00", "23:00"]

    row = []
    for idx, time_slot in enumerate(time_slots):
        if time_slot not in booked_times:
            row.append(telebot.types.InlineKeyboardButton(time_slot, callback_data=f"time_{time_slot}"))
            if (idx + 1) % 4 == 0:
                markup.row(*row)
                row = []

    if row:
        markup.row(*row)

    return markup


def generate_acreage_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    for i in range(2, 16):
        markup.row(telebot.types.InlineKeyboardButton(str(i), callback_data=f"acreage_{i}"))
    return markup


def get_address(message):
    global address
    try:
        address = message.text
        bot.send_message(message.chat.id, 'Пожалуйста, введите номер телефона')
        bot.register_next_step_handler(message, get_phone_number)
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Пожалуйста, попробуйте еще раз.')


def get_phone_number(message):
    global phone_number
    try:
        phone_number = message.text
        bot.send_message(message.chat.id, 'Пожалуйста, выберите количество соток по адресу',
                         reply_markup=generate_acreage_buttons())
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Пожалуйста, попробуйте еще раз.')


def generate_calendar():
    markup = telebot.types.InlineKeyboardMarkup()
    now = datetime.datetime.now()
    for i in range(10):
        date = now + datetime.timedelta(days=i)
        text = date.strftime("%d.%m.%Y")
        markup.row(telebot.types.InlineKeyboardButton(text, callback_data=text))
    return markup

''''''
bot.polling()
'''