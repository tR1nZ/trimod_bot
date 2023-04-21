import telebot as tb
from telebot import types as tp
import bot_token
import bot_parameters as pm
import sqlite3
import datetime

klava_back = tp.ReplyKeyboardMarkup(resize_keyboard=True)
klava_back.add(tp.KeyboardButton(text=pm.back_btn))
klava_good_and_reg = tp.ReplyKeyboardMarkup(resize_keyboard=True)
klava_good_and_reg.add(tp.KeyboardButton(text='Как удалить регистрацию или изменить данные?'),
                       tp.KeyboardButton(text='Хорошо'))
bot = tb.TeleBot(bot_token.tk)

events = {}
users = {}


@bot.message_handler(commands=['start'])  # самое начало бота, когда пользователь только активирует его
def send_mes(message):  # функция, где есть привественный текст
    bot.send_message(message.chat.id, pm.welcome)
    klava(message)


def backe(message):
    if message.text == pm.back_btn:
        back(message)
        return True
    else:
        return False


def klava(message):  # клавиатура, где есть расписание мп и регистрация
    klava = tp.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    answ1 = tp.KeyboardButton(text=pm.how_to_use)
    answ2 = tp.KeyboardButton(text=pm.show_event)
    answ3 = tp.KeyboardButton(text=pm.for_create_ev_btn)
    answ4 = tp.KeyboardButton(text="Личный кабинет")
    if message.from_user.username in pm.host:
        answ5 = tp.KeyboardButton(text="Добавить админа")
        klava.add(answ1, answ2, answ3, answ4, answ5)
    else:
        klava.add(answ1, answ2, answ3, answ4)
    bot.send_message(message.chat.id, pm.main_menu, reply_markup=klava)


@bot.message_handler(func=lambda message: message.text == "Личный кабинет")
def user_info(message):
    conn = sqlite3.connect('sqlite3.db')
    cur = conn.cursor()
    if cur.execute(f"SELECT * FROM events_list WHERE manager_id=?",
                   (message.chat.id,)).fetchone() is None:
        bot.send_message(message.chat.id, "Вы не создавали мероприятие")
    else:
        created_events = ''
        for i in range(
                len(cur.execute(
                    f'SELECT name_event FROM events_list WHERE manager_id = {message.chat.id}').fetchall())):
            created_events += f"{cur.execute(f'SELECT name_event FROM events_list WHERE manager_id = {message.chat.id}').fetchall()[i][0]}" + ', количество пользователей: ' + f"{cur.execute(f'SELECT user_count FROM events_list WHERE manager_id = {message.chat.id}').fetchall()[i][0]}" + '\n'

        bot.send_message(message.chat.id, "Cозданные мероприятия: \n" + created_events)

    events = cur.execute("SELECT name_event FROM events_list ").fetchall()
    registered_events = ''
    for i in range(len(events)):
        registered_users = cur.execute(f"SELECT chat_id FROM event_{events[i][0]}").fetchall()
        for j in range(len(registered_users)):
            if str(message.chat.id) in registered_users[j]:
                registered_events += events[i][
                                         0] + ', количество пользователей: ' + f"{cur.execute(f'SELECT user_count FROM events_list WHERE name_event = ?', (events[i][0],)).fetchall()[i - 1][0]}" + '\n'
    if registered_events != '':
        bot.send_message(message.chat.id, "Мероприятия, на которые вы зарегистрированы: \n" + registered_events)
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы ни на одно мероприятие")
    conn.commit()


@bot.message_handler(func=lambda message: message.text == pm.how_to_use)
def how_use(message):
    klava_good_and_reg = tp.ReplyKeyboardMarkup(resize_keyboard=True)
    klava_good_and_reg.add(tp.KeyboardButton(text='Как удалить регистрацию или изменить данные?'),
                           tp.KeyboardButton(text='Хорошо'))
    l = bot.send_message(message.chat.id, pm.instruction, reply_markup=klava_good_and_reg)
    bot.register_next_step_handler(l, rereg_and_dell_info)


def rereg_and_dell_info(message):
    if message.text == 'Хорошо':
        klava(message)
    else:
        good_kl = tp.ReplyKeyboardMarkup(resize_keyboard=True)
        good_kl.add(tp.KeyboardButton(text='Хорошо'))
        l = bot.send_message(message.chat.id, pm.instruction_dell_and_rereg, reply_markup=good_kl)
        bot.register_next_step_handler(l, goody)


def goody(message):
    if message.text == 'Хорошо':
        klava(message)


@bot.message_handler(func=lambda message: pm.back_btn in message.text)  # кнопка назад
def back(message):
    klava(message)


@bot.message_handler(func=lambda message: message.text == pm.for_create_ev_btn)
def admin_create_event(message):
    conn = sqlite3.connect('sqlite3.db')
    cur = conn.cursor()
    admins = cur.execute(f"SELECT username FROM admins").fetchall()
    admins_list = []
    for i in range(len(admins)):
        admins_list.append(admins[i][0])
    if message.from_user.username not in admins_list:
        bot.send_message(message.chat.id, pm.not_enough_rules)
    else:
        event_spis = []
        events[message.chat.id] = event_spis
        l = bot.send_message(message.chat.id, 'Чтобы создать таблицу укажите название мероприятия',
                             reply_markup=klava_back)

        bot.register_next_step_handler(l, create_event_name)  # запрашиваем имя мп


# переменная с названием мп
def create_event_name(message):
    if backe(message) == False:
        if message.text.count(' ') > 0:
            events.get(message.chat.id).append(message.text.replace(' ', '_'))
        else:
            events.get(message.chat.id).append(message.text)
        l = bot.send_message(message.chat.id, 'Укажите имя создателя')
        bot.register_next_step_handler(l, create_event_manager)


# переменная с именем менеджера
def create_event_manager(message):
    if backe(message) == False:
        events.get(message.chat.id).append(message.text.title())
        events.get(message.chat.id).append(message.chat.id)
        l = bot.send_message(message.chat.id, 'Укажите почту создателя')
        bot.register_next_step_handler(l, create_event_manager_email)


# перемененная с почтой менеджера
def create_event_manager_email(message):
    if backe(message) == False:
        if "@" not in message.text:
            l = bot.send_message(message.chat.id, pm.fake_mail)  # проверка на фэйк почту
            bot.register_next_step_handler(l, create_event_manager_email)
        else:
            events.get(message.chat.id).append(message.text)
            l = bot.send_message(message.chat.id, 'Укажите время проведения мероприятия через -, например 27-03-2022')
            bot.register_next_step_handler(l, create_event_date)


# переменная с датой ивента
def create_event_date(message):
    if backe(message) == False:
        message.text = ''.join(message.text.split('-'))
        if datetime.datetime.strptime(message.text, "%d%m%Y") <= datetime.datetime.now():
            l = bot.send_message(message.chat.id,
                                 "Некоректная дата, пожалуйста укажите другую, убедитесь, что вы ввели все верно")  # проверка на фэйк почту
            bot.register_next_step_handler(l, create_event_date)
        else:
            events.get(message.chat.id).append(datetime.date.today())
            events.get(message.chat.id).append(message.text)
            events.get(message.chat.id).append(0)
            event_reg(message)


def event_reg(message):
    conn = sqlite3.connect('sqlite3.db')
    cur = conn.cursor()
    bot.send_message(message.chat.id, pm.blagodar)

    cur.execute(
        "INSERT INTO events_list (name_event, manager_name, manager_id, manager_email, date_register, event_date, user_count) VALUES (?, ?, ?, ?, ?, ?, ?);",
        events.get(message.chat.id))
    cur.execute(f"""CREATE TABLE IF NOT EXISTS event_{events.get(message.chat.id)[0]}(
    chat_id text,
    name text, 
    surname text,
    age int,
    email text
    )""")
    conn.commit()
    klava(message)


@bot.message_handler(func=lambda message: pm.show_event in message.text)
def spisok_registr(message):  # клавиатура, где есть расписание мп и регистрация
    lol = ['event', 'chat_id', 'name', 'surname', 'age', 'mail']
    users[message.chat.id] = lol
    users.get(message.chat.id)[0] = message.chat.id
    conn = sqlite3.connect('sqlite3.db')
    cur = conn.cursor()
    if cur.execute(f"SELECT * FROM events_list").fetchall() == []:
        bot.send_message(message.chat.id, "Нет доступных мероприятий")

    else:
        nearest_events = cur.execute("SELECT name_event FROM events_list").fetchall()
        date_nearest_events = cur.execute("SELECT event_date FROM events_list").fetchall()
        n_e = ''
        for i in range(len(nearest_events)):
            if datetime.datetime.strptime(date_nearest_events[i][0], "%d%m%Y") <= datetime.datetime.now():
                delete_event = cur.execute(f"SELECT * FROM events_list WHERE name_event = ?",
                                           (nearest_events[i][0],)).fetchone()
                cur.execute(
                    "INSERT INTO past_events_list (id, name_event, manager_name, manager_id, manager_email, user_count, date_register, event_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                    delete_event)
                cur.execute(f"DELETE FROM events_list WHERE name_event = ?", (nearest_events[i][0],))
            else:
                s = date_nearest_events[i][0][:2] + '-' + date_nearest_events[i][0][2:4] + '-' + date_nearest_events[i][
                                                                                                     0][4:]
                n_e += str(i + 1) + '. ' + nearest_events[i][0] + ", дата: " + s + '\n'
        bot.send_message(message.chat.id, pm.chose_event, reply_markup=klava_back)
        s = bot.send_message(message.chat.id, n_e)
        bot.register_next_step_handler(s, reg_name_event)
    conn.commit()


def reg_name_event(message):
    conn = sqlite3.connect('sqlite3.db')
    cur = conn.cursor()
    if backe(message) == False:
        nearest_events = cur.execute("SELECT id FROM events_list").fetchall()
        n_e = ''
        for i in range(len(nearest_events)):
            n_e += str(i + 1) + ' ' + str(nearest_events[i][0]) + '\n'

        if message.text in n_e:
            users.get(message.chat.id)[0] = message.text
            if cur.execute(
                    f"SELECT * FROM event_{cur.execute(f'SELECT name_event FROM events_list WHERE id = {message.text}').fetchone()[0]} WHERE chat_id=?",
                    (message.chat.id,)).fetchone() is not None:
                dell_and_upd = tp.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                dell_and_upd.add(tp.KeyboardButton(text=pm.dell), tp.KeyboardButton(text=pm.upd),
                                 tp.KeyboardButton(text=pm.back_btn))
                s = bot.send_message(message.chat.id, "Вы уже зарегистрированы", reply_markup=dell_and_upd)
                bot.register_next_step_handler(s, delete_and_edit_user)

            else:
                s = bot.send_message(message.chat.id, pm.take_name)

                bot.register_next_step_handler(s, for_name)
        else:
            bot.send_message(message.chat.id, "Нет такого мероприятия")


def for_name(message):
    if backe(message) == False:
        users.get(message.chat.id)[1] = message.chat.id
        users.get(message.chat.id)[2] = message.text.title()
        l = bot.send_message(message.chat.id, pm.take_surname)
        bot.register_next_step_handler(l, for_surname)


def for_surname(message):
    if backe(message) == False:
        users.get(message.chat.id)[3] = message.text.title()
        # в месседж тексте лежит фамилия юзера
        l = bot.send_message(message.chat.id, pm.take_age)  # тут будет фамилия юзера
        bot.register_next_step_handler(l, for_age)


def for_age(message):
    if backe(message) == False:
        if message.text.isdigit() is False:

            l = bot.send_message(message.chat.id, "Некорректный возраст")  # проверка на фэйк возраст
            bot.register_next_step_handler(l, for_age)
        else:
            l = bot.send_message(message.chat.id, pm.take_email)
            users.get(message.chat.id)[4] = message.text

            bot.register_next_step_handler(l, for_email)


def for_email(message):
    if backe(message) == False:
        if "@" not in message.text:
            l = bot.send_message(message.chat.id, pm.fake_mail)  # проверка на фэйк почту
            bot.register_next_step_handler(l, for_email)

        else:
            # в месседж тексте лежит почта юзера
            users.get(message.chat.id)[5] = message.text
            bot.send_message(message.chat.id, pm.blagodar)
            user_reg(message)


def user_reg(message):
    add_person = users.get(message.chat.id)[1:]
    conn = sqlite3.connect('sqlite3.db')
    cur = conn.cursor()
    if cur.execute(
            f"SELECT * FROM event_{cur.execute(f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[0]} WHERE chat_id=?",
            (message.chat.id,)).fetchone() is not None:
        cur.execute(
            f"DELETE FROM event_{cur.execute(f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[0]} WHERE chat_id=?",
            (message.chat.id,))
    cur.execute(
        f"INSERT INTO event_{cur.execute(f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[0]} (chat_id, name, surname, age, email) VALUES (?, ?, ?, ?, ?);",
        add_person)
    user_count = cur.execute(
        f"SELECT COUNT(*) FROM event_{cur.execute(f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[0]}").fetchone()[
        0]
    cur.execute(f"UPDATE events_list SET user_count = ? WHERE name_event = ?",
                (user_count, cur.execute(
                    f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[0]))
    conn.commit()
    klava(message)


def delete_and_edit_user(message):
    global reg_person
    if backe(message) == False:
        if message.text == pm.dell:
            conn = sqlite3.connect('sqlite3.db')
            cur = conn.cursor()
            cur.execute(
                f"DELETE FROM event_{cur.execute(f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[0]} WHERE chat_id=?",
                (message.chat.id,))
            user_count = cur.execute(
                f"SELECT COUNT(*) FROM event_{cur.execute(f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[0]}").fetchone()[
                0]
            cur.execute(f"UPDATE events_list SET user_count = ? WHERE name_event = ?",
                        (user_count, cur.execute(
                            f'SELECT name_event FROM events_list WHERE id = {users.get(message.chat.id)[0]}').fetchone()[
                            0]))
            s = bot.send_message(message.chat.id, "Удалено успешно")
            conn.commit()
        if message.text == pm.upd:
            s = bot.send_message(message.chat.id, pm.take_name)
            bot.register_next_step_handler(s, for_name)


@bot.message_handler(func=lambda message: message.text == "Добавить админа")
def add_admin(message):
    if backe(message) == False:
        s = bot.send_message(message.chat.id, "Введите username", reply_markup=klava_back)
        bot.register_next_step_handler(s, adding)


def adding(message):
    if backe(message) == False:
        conn = sqlite3.connect('sqlite3.db')
        cur = conn.cursor()
        cur.execute(f'INSERT INTO admins (username) VALUES (?)', (message.text,))
        conn.commit()
        klava(message)


@bot.message_handler(content_types=['text'])
def no_answer(message):
    bot.send_message(message.chat.id, pm.for_no_answer)


bot.infinity_polling()
