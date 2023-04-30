import datetime
import threading

import telebot

import config
from db import *

bot = telebot.TeleBot(config.API_TOKEN)
CHANNEL_NAME = "@pahota_xi"
# Declare global variables
date = None
time = None
address = None
acreage = None
phone_number = None


def send_upcoming_order_notification(stop_event):
    while not stop_event.is_set():
        now = datetime.datetime.now()
        time_to_check = now + datetime.timedelta(minutes=34)
        orders = get_orders_by_date_and_time(time_to_check.date().strftime('%d.%m.%Y'), time_to_check.strftime('%H:%M'))

        for order in orders:
            order_id, date, order_time, address, acreage, phone_number = order
            notification_text = f"Следующий заказ в {order_time}, по адресу {address} и номер телефона {phone_number}."
            bot.send_message(CHANNEL_NAME, notification_text)

        stop_event.wait(60)  # Проверяем заказы каждую минуту


# Запускаем отправку уведомлений в фоновом потоке
stop_event = threading.Event()
notification_thread = threading.Thread(target=send_upcoming_order_notification, args=(stop_event,))
notification_thread.start()


# Выполните следующий код, чтобы остановить поток
# stop_event.set()
# notification_thread.join()
@bot.callback_query_handler(func=lambda call: call.data.startswith("completed_"))
def order_completed(call):
    order_id = int(call.data.replace("completed_", ""))
    try:
        delete_order(order_id)
        bot.answer_callback_query(call.id, "Заказ выполнен и удален из базы данных")
        bot.edit_message_text("Заказ выполнен и удален из базы данных", call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.answer_callback_query(call.id, "Ошибка. Пожалуйста, попробуйте еще раз.")


def generate_start_buttons():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    new_order_button = telebot.types.KeyboardButton("Новый заказ")
    all_orders_button = telebot.types.KeyboardButton("Все заказы")
    markup.add(new_order_button, all_orders_button)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=generate_start_buttons())


@bot.message_handler(func=lambda message: message.text == "Новый заказ")
def new_order(message):
    bot.send_message(message.chat.id, "Пожалуйста, выберите дату заказа.", reply_markup=generate_calendar())


def format_date_button(date_tuple):
    date_text = date_tuple[0]
    date_obj = datetime.datetime.strptime(date_text, "%d.%m.%Y")
    date_formatted = date_obj.strftime("%d %B - %A")
    date_localized = localize_day_and_month(date_formatted, date_obj)
    orders_count = date_tuple[1]
    return f"{date_localized} ({orders_count} заказов)"


def localize_day_and_month(date_formatted, date_obj):
    months = {
        "January": "января",
        "February": "февраля",
        "March": "марта",
        "April": "апреля",
        "May": "мая",
        "June": "июня",
        "July": "июля",
        "August": "августа",
        "September": "сентября",
        "October": "октября",
        "November": "ноября",
        "December": "декабря"
    }
    days = {
        "Monday": "понедельник",
        "Tuesday": "вторник",
        "Wednesday": "среда",
        "Thursday": "четверг",
        "Friday": "пятница",
        "Saturday": "суббота",
        "Sunday": "воскресенье"
    }

    for en_month, ru_month in months.items():
        date_formatted = date_formatted.replace(en_month, ru_month)

    for en_day, ru_day in days.items():
        date_formatted = date_formatted.replace(en_day, ru_day)

    return date_formatted


@bot.message_handler(func=lambda message: message.text == "Все заказы")
def all_orders(message):
    order_dates = get_order_dates_list()
    if order_dates:
        markup = telebot.types.InlineKeyboardMarkup()
        for date_tuple in order_dates:
            date_button_text = format_date_button(date_tuple)
            markup.row(
                telebot.types.InlineKeyboardButton(date_button_text, callback_data=f"order_date_{date_tuple[0]}"))
        bot.send_message(message.chat.id, "Выберите дату, чтобы увидеть заказы:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Заказов пока нет.")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global date, time, address, acreage, phone_number
    try:
        if call.message:
            if call.data.startswith("date_"):
                date = call.data.replace("date_", "")
                bot.send_message(call.message.chat.id, "Выберите время заказа",
                                 reply_markup=generate_time_buttons(date))
            elif call.data.startswith("time_"):
                time = call.data.replace("time_", "")
                bot.send_message(call.message.chat.id, "Что бы сделать заказ, пожалуйста, укажите адрес.")
                bot.register_next_step_handler(call.message, get_address)
            elif call.data.startswith("acreage_"):
                acreage = call.data.replace("acreage_", "")
                bot.send_message(call.message.chat.id,
                                 f'Спасибо, ваш заказ принят. Дата заказа: {date}, время: {time}, адрес: {address}, количество соток: {acreage}, номер телефона: {phone_number}')
                add_order(date, time, address, int(acreage), phone_number)
            elif call.data.startswith("order_date_"):
                handle_order_date(call)
            elif call.data.startswith("all"):
                handle_all_dates(call.message)
    except Exception as e:
        bot.reply_to(call.message, 'Ошибка. Пожалуйста, попробуйте еще раз.')


def handle_all_dates(message):
    dates = get_order_dates()
    dates.sort()
    markup = telebot.types.InlineKeyboardMarkup()
    for date in dates:
        markup.row(telebot.types.InlineKeyboardButton(date, callback_data=f"orders_{date}"))
    bot.send_message(message.chat.id, "Выберите дату для просмотра заказов:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("order_date_"))
def handle_order_date(call):
    selected_date = call.data.replace("order_date_", "")
    try:
        datetime.datetime.strptime(selected_date, '%d.%m.%Y')
    except ValueError:
        bot.send_message(call.message.chat.id, "Неверный формат даты")
        return

    orders = get_order_dates(selected_date)
    orders.sort(key=lambda x: x[2])  # Сортировка заказов по времени
    for order in orders:
        response = f"Заказ на {selected_date}:\n\n"
        response += f" Время: {order[2]}, Адрес: {order[3]}, Количество соток: {order[4]}, Номер телефона: <a href='tel:{order[5]}'>{order[5]}</a>\n"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("Заказ выполнен", callback_data=f"completed_{order[0]}"))
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='HTML')


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
        markup.row(telebot.types.InlineKeyboardButton(text, callback_data=f"date_{text}"))
    return markup


def generate_time_buttons(selected_date):
    markup = telebot.types.InlineKeyboardMarkup()
    available_time_slots = get_available_time_slots(selected_date)

    # Группировка кнопок времени по 4 в каждой строке
    for i in range(0, len(available_time_slots), 4):
        time_buttons = [telebot.types.InlineKeyboardButton(time_slot, callback_data=f"time_{time_slot}") for time_slot
                        in available_time_slots[i:i + 4]]
        markup.row(*time_buttons)

    return markup


def generate_acreage_buttons():
    markup = telebot.types.InlineKeyboardMarkup()

    # Группировка кнопок количества соток по 4 в каждой строке
    for i in range(2, 16, 4):
        acreage_buttons = [telebot.types.InlineKeyboardButton(str(j), callback_data=f"acreage_{j}") for j in
                           range(i, i + 4)]
        markup.row(*acreage_buttons)

    return markup


def get_available_time_slots(selected_date):
    all_time_slots = [
        "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00",
        "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30",
        "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00"
    ]

    orders = get_order_dates(selected_date)  # Получаем список заказов на выбранную дату
    booked_time_slots = [order[2] for order in orders]  # Получаем список забронированных временных слотов
    available_time_slots = [time_slot for time_slot in all_time_slots if
                            time_slot not in booked_time_slots]  # Отсеиваем занятые временные слоты

    return available_time_slots


bot.polling()
