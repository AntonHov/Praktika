import redminelib
import telebot
from redminelib import Redmine
from telebot import types
import datetime
import sqlite3

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu_return(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(f"Просмотр трудозатрат"))
    markup.add(types.KeyboardButton(f"/start"))
    bot.send_message(chat_id=message.chat.id, text=f"Вернуться в:", reply_markup=markup)

bot = telebot.TeleBot('7218092054:AAGm4gF-5mbtCvinMNuXEGpyD5MvNkEH1E0')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
REDMINE_URL = "http://localhost:3000/"
API_KEY = "6f6573a5e6f5fd7e83dc95e98fd2b3cdceb40535"
redmine = redminelib.Redmine(REDMINE_URL, key=API_KEY)
project = redmine.project.get('test1')
issues = ''
user_time_entries = ''
rm_id = ''
idchat = ''
name = ''

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(f"Просмотр трудозатрат"))
    markup.add(types.KeyboardButton(f"Заполнение трудозатрат"))
    bot.send_message(chat_id=message.chat.id, text=f"Пользователь {message.from_user.first_name}, добро пожаловать!\nВыберите, что хотите сделать:\nПросмотр трудозатрат\nЗаполнение трудозатрат", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Просмотр трудозатрат")  # Обработка команды для старта
def chose_issue(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    users = redmine.user.all()
    for user in users:
        if int(user.custom_fields[0]['value']) == int(message.chat.id):
            rm_id = user.id


    bot.send_message(chat_id=message.from_user.id, text=f"Пользователь {message.from_user.first_name}, выберите дату для просмотра трудозатрат (01 01 2024):",reply_markup=markup)


    bot.register_next_step_handler(message, message_input_step, rm_id = rm_id)


@bot.message_handler(func=lambda message: message.text == "Заполнение трудозатрат")  # Обработка команды для старта
def chose_issue(message):


    users = redmine.user.all()
    for user in users:
        if int(user.custom_fields[0]['value']) == int(message.chat.id):
            rm_id = user.id

    issues = redmine.issue.filter(project_id='test1', assigned_to_id=rm_id)

    bot.send_message(chat_id=message.from_user.id, text=f"Пользователь {message.from_user.first_name}, напишите id задачи, дату и кол-во часов для заполнения трудозатрат(1,01 01 2024,10):")

    for issue in reversed(issues):
        subject = issue.subject
        bot.send_message(chat_id=message.from_user.id, text=f"{subject} id: {issue.id}")

    bot.register_next_step_handler(message, message_create, rm_id = rm_id)

@bot.message_handler(content_types=['text'])  #Создаём новую функцию ,реагирующую на любое сообщение
def message_input_step(message, rm_id):
    try:
        text_message = str(message.text).split()

        if len(text_message) != 3:
            date_st = datetime.date(int(text_message[2]), int(text_message[1]), int(text_message[0]))
            date_end = datetime.date(int(text_message[6]), int(text_message[5]), int(text_message[4]))
            user_time_entries = redmine.time_entry.filter(user_id=rm_id, from_date=date_st, to_date= date_end)
        else:
            date = datetime.date(int(text_message[2]), int(text_message[1]), int(text_message[0]))
            user_time_entries = redmine.time_entry.filter(user_id=rm_id, spent_on=date)
        total_hours = 0

        if not user_time_entries:
            text = f"Пользователь {message.from_user.first_name} не заполнил трудозатраты."
            bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=types.ReplyKeyboardRemove())
        else:
            for time_entry in user_time_entries:
                total_hours += int(time_entry.hours)
            text = f"Общее затраченное время за период {message.text}: {total_hours} ч."
            bot.send_message(chat_id=message.from_user.id, text=text,reply_markup=types.ReplyKeyboardRemove())

            #bot.send_message(chat_id=message.chat.id, text='Вы ввели некорректный текст!')
        menu_return(message)
    except:
        bot.send_message(chat_id=message.from_user.id, text=f'Вы ввели некорректные данные!')
        menu_return(message)

def message_create(message, rm_id):
    try:
        text_message = str(message.text).split(',')
        print(text_message)
        create_date = text_message[1].split()
        time_entry = redmine.time_entry.create(
            issue_id=text_message[0],
            spent_on=datetime.date(int(create_date[2]), int(create_date[1]), int(create_date[0])),
            hours=text_message[2],
            user_id=rm_id,
            comments='hello'
        )
        bot.send_message(chat_id=message.from_user.id, text=f'Трудозатраты успешно добавлены!')
        menu_return(message)
    except:
        bot.send_message(chat_id=message.from_user.id, text=f'Некорректные данные!')
        menu_return(message)


if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)
    except Exception as r:
        print("Непридвиденная ошибка: ", r)
    finally:
        print("Здесь всё закончилось")