import telebot
from telebot import types
from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

def capture_text(message):
    user_text = message.text
    # Сохранение в БД
    markup = types.InlineKeyboardMarkup()
    btn_add_note = types.InlineKeyboardButton('Добавить задачу', callback_data="add_note")
    btn_notes_list = types.InlineKeyboardButton('Просмотр задач', callback_data="notes_list")
    markup.row(btn_add_note, btn_notes_list)
    bot.send_message(message.chat.id, "Задача сохранена", reply_markup=markup)