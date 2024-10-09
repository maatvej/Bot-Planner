from telebot import types
from extensions import *
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


# обработка команды /timer
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
            # вычисляем дни, часы, минуты, секунды
            days = difference_time.days
            sec = difference_time.seconds
            hour = sec // 3600
            minutes = (sec // 60) % 60
            seconds = sec % 60

            # отправка сообщения
            time_message = f'Осталось {days} дней, {hour} часов, {minutes} минут, {seconds} секунд.'
            bot.send_message(user_id, time_message)
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


# Команда /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Полезная информация")


@bot.callback_query_handler(func=lambda callback: True)
def callback_start(callback):
    if callback.data == "diary":
        markup = types.InlineKeyboardMarkup()
        btn_add_note = types.InlineKeyboardButton('Добавить заметку', callback_data="add_note")
        btn_view_note = types.InlineKeyboardButton('Просмотреть заметку', callback_data="view_note")
        btn_delete_note = types.InlineKeyboardButton('Удалить заметку', callback_data="delete_note")
        markup.row(btn_add_note, btn_view_note, btn_delete_note)
        btn_categories_list = types.InlineKeyboardButton('Просмотр категорий', callback_data="categories_list")
        btn_categories_filter = types.InlineKeyboardButton('Задачи по категориям', callback_data="categories_filter")
        markup.row(btn_categories_list, btn_categories_filter)
        bot.edit_message_text("Пожалуйста, выберите действие", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    if callback.data == "add_note":
        chat_id = callback.message.chat.id
        notes_data[chat_id] = {}
        bot.send_message(chat_id, "Введите заголовок заметки:")
        bot.register_next_step_handler(callback.message, process_caption_step)

    if callback.data == "view_note":
        chat_id = callback.message.chat.id
        bot.send_message(chat_id, "Введите заголовок заметки для просмотра:")
        bot.register_next_step_handler(callback.message, process_view_note)

    if callback.data == "categories_list":
        chat_id = callback.message.chat.id
        categories = get_categories_list()
        if categories:
            categories_str = "\n".join(categories)
            bot.send_message(chat_id, f"Список категорий:\n{categories_str}")
        else:
            bot.send_message(chat_id, "Категорий пока нет.")

    if callback.data == "delete_note":
        chat_id = callback.message.chat.id
        bot.send_message(chat_id, "Введите заголовок заметки для удаления:")
        bot.register_next_step_handler(callback.message, process_delete_note)

    if callback.data == "categories_filter":
        chat_id = callback.message.chat.id
        bot.send_message(chat_id, "Введите категорию для получения заметок:")
        bot.register_next_step_handler(callback.message, send_notes_by_category)

    if callback.data == "vacation":
        markup = types.InlineKeyboardMarkup()
        btn_accept_add = types.InlineKeyboardButton('Поехали!', callback_data="accept_add")
        btn_decision_process = types.InlineKeyboardButton('Ещё подумаю', callback_data="decision_process")
        markup.row(btn_accept_add, btn_decision_process)
        bot.edit_message_text("Рекомендации: ", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    if callback.data == "accept_add":
        markup = types.InlineKeyboardMarkup()
        btn_vp_yes = types.InlineKeyboardButton('Да', callback_data="vacation_prepare_yes")
        btn_vp_no = types.InlineKeyboardButton('Нет', callback_data="vacation_prepare_no")
        markup.row(btn_vp_yes, btn_vp_no)
        bot.edit_message_text("Приступим к подготовке", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    if callback.data == "decision_process":
        markup = types.InlineKeyboardMarkup()
        btn_dp_yes = types.InlineKeyboardButton('Да', callback_data="decison_process_yes")
        btn_dp_no = types.InlineKeyboardButton('Нет', callback_data="decison_process_no")
        markup.row(btn_dp_yes, btn_dp_no)
        bot.edit_message_text("Вы уже выбрали место?", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    if callback.data == "vacation_prepare_yes":
        markup = types.InlineKeyboardMarkup()
        btn_employer_aware = types.InlineKeyboardButton('Да', callback_data="employer_aware")
        btn_employer_unaware = types.InlineKeyboardButton('Нет', callback_data="employer_unaware")
        markup.row(btn_employer_aware, btn_employer_unaware)
        bot.edit_message_text("Вы уже предупредили работодателя?", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    if callback.data == "vacation_prepare_no":
        bot.send_message(callback.message.chat.id, "Приятного отдыха!")

    if callback.data == "decison_process_yes":
        markup = types.InlineKeyboardMarkup()
        btn_hot_true = types.InlineKeyboardButton('Да', callback_data="hot_true")
        btn_hot_false = types.InlineKeyboardButton('Нет', callback_data="hot_false")
        markup.row(btn_hot_true, btn_hot_false)
        bot.edit_message_text("Там будет жарко??", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    if callback.data == "decison_process_no":
        markup = types.InlineKeyboardMarkup()
        btn_chose_place = types.InlineKeyboardButton('Да', callback_data="chose_place")
        btn_chose_place_not = types.InlineKeyboardButton('Нет', callback_data="chose_place_not")
        markup.row(btn_chose_place, btn_chose_place_not)
        bot.edit_message_text("Вот что сейчас подходит: В зависимости от сезона будет список стран РЕКЛАМА!!!", callback.message.chat.id, callback.message.message_id, reply_markup=markup)


# Включение бота
bot.polling(none_stop=True)