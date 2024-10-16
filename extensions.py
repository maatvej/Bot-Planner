import telebot
from config import API_TOKEN
from sqlalchemy.orm import Session
from dbcreate import Note, engine
import time
from telebot import types
from datetime import datetime

bot = telebot.TeleBot(API_TOKEN)

# Переменная для временного хранения данных заметки
notes_data = {}

# Функция для сохранения заметки
def save_note(caption, category, body):
    with Session(autoflush=False, bind=engine) as db:
        note = db.query(Note).filter(Note.caption == caption).first()

        if note:
            note.category = category
            note.body = body
            print(f'Запись "{caption}" обновлена.')
        else:
            new_note = Note(caption=caption, category=category, body=body)
            db.add(new_note) 
            print(f'Запись "{caption}" добавлена.')

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f'Ошибка при сохранении заметки: {e}')


# Функция для удаления заметки
def delete_note(caption):
    with Session(autoflush=False, bind=engine) as db:
        note = db.query(Note).filter(Note.caption == caption).first()
        
        if note:
            db.delete(note)
            try:
                db.commit()
                print(f'Запись "{caption}" удалена.')
                return True
            except Exception as e:
                db.rollback()
                print(f'Ошибка при удалении заметки: {e}')
                return False
        else:
            print(f'Запись "{caption}" не найдена.')
            return False
        

# Функция для просмотра заметки
def view_note(caption):
    with Session(autoflush=False, bind=engine) as db:
        note = db.query(Note).filter(Note.caption == caption).first()
        return note


# Получение списка категорий 
def get_categories_list():
    with Session(autoflush=False, bind=engine) as db:
        categories = db.query(Note.category).distinct().all()
        cat_list = [category[0] for category in categories]
        return cat_list
    

# Получение заметок по категории    
def get_notes_by_category(category):
    with Session(autoflush=False, bind=engine) as db:
        notes = db.query(Note).filter(Note.category == category).all()
        return notes
    

def process_caption_step(message):
    chat_id = message.chat.id
    notes_data[chat_id]['caption'] = message.text
    bot.send_message(chat_id, "Теперь введите текст заметки:")
    bot.register_next_step_handler(message, process_body_step)


def process_body_step(message):
    chat_id = message.chat.id
    notes_data[chat_id]['body'] = message.text
    bot.send_message(chat_id, "Введите категорию заметки:")
    bot.register_next_step_handler(message, process_category_step)


def process_category_step(message):
    chat_id = message.chat.id
    notes_data[chat_id]['category'] = message.text
    # Сохраняем заметку в базу данных
    save_note(
        caption=notes_data[chat_id]['caption'],
        body=notes_data[chat_id]['body'],
        category=notes_data[chat_id]['category']
    )
    del notes_data[chat_id]
    bot.send_message(chat_id, "Заметка сохранена успешно")


def send_notes_by_category(message):
    chat_id = message.chat.id
    category = message.text
    notes = get_notes_by_category(category)
    
    if notes:
        notes_text = "\n\n".join([f"Заголовок: {note.caption}\nТекст: {note.body}" for note in notes])
        bot.send_message(chat_id, f"Заметки в категории '{category}':\n\n{notes_text}")
    else:
        bot.send_message(chat_id, f"В категории '{category}' заметок не найдено.")


def process_delete_note(message):
    chat_id = message.chat.id
    caption = message.text
    if delete_note(caption):
        bot.send_message(chat_id, f'Заметка "{caption}" успешно удалена.')
    else:
        bot.send_message(chat_id, f'Заметка "{caption}" не найдена.')


def process_view_note(message):
    chat_id = message.chat.id
    caption = message.text
    note = view_note(caption)
    
    if note:
        bot.send_message(chat_id, f"{note.caption}\n{note.body}")
    else:
        bot.send_message(chat_id, f'Заметка "{caption}" не найдена.')

def input_date(message):
    try:
        # Проверяем, что дата введена в правильном формате
        planned_date = datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
        bot.send_message(message.chat.id, f'Вы запланировали отдых на {planned_date.date()}.')
        time.sleep(2)
        markup_time_start = types.InlineKeyboardMarkup()
        btn_yes_start = types.InlineKeyboardButton('Да', callback_data='yes_time')
        btn_no_start = types.InlineKeyboardButton('Нет', callback_data='no_time')
        markup_time_start.row(btn_yes_start, btn_no_start)
        bot.send_message(message.chat.id, f'Начнем отсчет?', reply_markup=markup_time_start)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД ЧЧ:MM:СС.')
        bot.register_next_step_handler(message, input_date)