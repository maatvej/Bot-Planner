import time
from datetime import datetime
import threading
from extensions import bot

# глобальная переменная хранит в себе инфо о таймерах по ключу user_id)
timers = {}

# основная функция таймера
# принимает в себя id пользователя и время события и остановку события
def timer(user_id, set_time, stop_event):
    # цикл получения времени и расчет остаточного времени
    while not stop_event.is_set():
        # получение времени в данную секунду
        now = datetime.now()
        # разница между полученным увременем и сейчас
        difference_time = set_time - now

        # # если полученное время в секундах меньше или равно 0
        # if difference_time.total_seconds() <= 0:
        #     # бот присылает уведомление
        #     bot.send_message(user_id, 'Настало время события!')
        #     # программа заканчивается
        #     break

        # количество дней из переменной разницы во времени
        days = difference_time.days
        # секунды из этой же переменной
        sec = difference_time.seconds
        # количество полных часов из оставшихся секунд
        hour = sec // 3600
        # колиичество минут (// получаем целые минут и остаток, игнорирую полный час)
        minutes = (sec // 60) % 60
        # оставшиеся секунды
        seconds = sec % 60

        # сообщение пользователю с таймером
        time_message = f'Осталось {days} дней, {hour} часов,  {minutes} минут, {seconds} секунд.'

        # блок try отправляет сообщение пользователю
        try:
            bot.send_message(user_id, time_message)
        # except вызывает исключение в случае ошибки
        except Exception as e:
            print(f'Ошибка отправки сообщения: {e}')

        # как часто срабатывает таймер (каждые 60 сек)
        time.sleep(3600)



# следующий шаг после ввода
def input_time(message):
    # блок try обрабатывает сообщение с датой и временем
    try:
        # полученное время преобразовывается в объект datetime
        set_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
        # от юзера
        user_id = message.chat.id

        # если пользователя нет в таймерах, то создается новый поток
        if user_id not in timers:
            # Используем Event для завершения потока
            stop_event = threading.Event()
            # создание отдельного потока, функция таймер не будет мешать выполнению других задач
            timer_th = threading.Thread(target=timer, args=(user_id, set_time, stop_event))
            # запуск потока
            timer_th.start()
            # сохраняем по ключу в словаре (проверяет запущен ли таймер у пользователя)
            timers[user_id] = (timer_th, stop_event, set_time)
        # если пользователь существует, то выводит сообщение
        elif set_time.total_seconds() <= 0:
            bot.send_message(user_id, 'Настало время события!')
        else:
            bot.send_message(user_id, 'Вы уже запустили таймер.')

    # срабатывает, если введен неверный формат
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, используйте формат 'YYYY-MM-DD HH:MM:SS'.")

