from telebot import types
from extensions import bot, capture_text
from timer import timers, input_time
from datetime import datetime


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn_vacation = types.InlineKeyboardButton('Отпуск', callback_data="vacation")
    btn_diary = types.InlineKeyboardButton('Ежедневник', callback_data="diary")
    markup.row(btn_vacation, btn_diary)
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.username}!  Выберите команду:", reply_markup=markup)
    

@bot.callback_query_handler(func=lambda callback: True)
def callback_start(callback):
    if callback.data == "vacation":
        bot.edit_message_text("Рекомендации: ", callback.message.chat.id, callback.message.message_id)

    if callback.data == "diary":
        markup = types.InlineKeyboardMarkup()
        btn_add_note = types.InlineKeyboardButton('Добавить задачу', callback_data="add_note")
        # btn_remove_note = types.InlineKeyboardButton('Удалить задачу', callback_data="remove_note")
        btn_notes_list = types.InlineKeyboardButton('Просмотр задач', callback_data="notes_list")
        markup.row(btn_add_note, btn_notes_list)
        bot.edit_message_text("Пожалуйста, выберите действие", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    if callback.data == "add_note":
        bot.edit_message_text("Введите задачу.", callback.message.chat.id, callback.message.message_id)
        bot.register_next_step_handler(callback.message, capture_text)

    if callback.data == "notes_list":
        notes_list = "" #Взятие из БД
        bot.send_message(callback.message.chat.id, notes_list, )


# Команда /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Полезная информация")


# обработка команды timer
@bot.message_handler(commands=['timer'])
# запрашивает у пользователя формат ввода даты и времени
def start_timer(message):
    bot.send_message(message.chat.id, "'Введите дату и время события в формате 'YYYY-MM-DD HH:MM:SS'.")
    # регистрирует следующий шаг
    bot.register_next_step_handler(message, input_time)


# обработчик команды, вызывающей таймер
@bot.message_handler(commands=['mytimer'])
def check_timer(message):
    # получаем id пользователя
    user_id = message.chat.id
    # проверяем есть ли активный таймер
    if user_id in timers:
        # если пользователь имеет таймер, то получаем данные: поток, событие остановки и время срабатывания
        thread, stop_event, set_time = timers[user_id]
        # получаем сейчас
        now = datetime.now()
        # вычисляем время до срабатывания
        difference_time = set_time - now
        # если оставшееся время больше 0
        if difference_time.total_seconds() > 0:
            # вычисляем все то же самое
            days = difference_time.days
            sec = difference_time.seconds
            hour = sec // 3600
            minutes = (sec // 60) % 60
            seconds = sec % 60

            # отправка сообщения
            time_message = f'Осталось {days} дней, {hour} часов, {minutes} минут, {seconds} секунд.'
            bot.send_message(user_id, time_message)
        # если настало время события
        else:
            # отправляем сообщение
            bot.send_message(user_id, "Настало время события!")
            # устанавливаем событие остановки потока
            stop_event.set()
            # удаляем из таймеров
            del timers[user_id]
    # если активного таймера нет, отправляем сообщение
    else:
        bot.send_message(user_id, "У вас нет активного таймера.")


# обработка команды удаления таймера
@bot.message_handler(commands=['deletetimer'])
def delete_timer(message):
    # получаем id пользователя
    user_id = message.chat.id
    # если пользователь существует
    if user_id in timers:
        # если пользователь имеет таймер, то получаем данные: поток, событие остановки и время срабатывания
        thread, stop_event, set_time = timers[user_id]
        # устанавливаем событие остановки потока
        stop_event.set()
        # удаляем таймер из словаря
        del timers[user_id]
        # отправляем сообщение
        bot.send_message(user_id, "Все ваши активные таймеры были удалены.")
    # если пользователя нет в таймерах
    else:
        bot.send_message(user_id, "У вас нет активных таймеров для удаления.")


# Включение бота
bot.polling(none_stop=True)

# bot.delete_message(callback.message.chat.id, callback.message.message_id)