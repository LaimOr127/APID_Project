import telebot
from telebot import types
import config
import sqlite3
import parser2

bot = telebot.TeleBot(config.bot_token)

sub_links = ["Cbpub", "lentadna", "oldlentach", "breakingmash", "msk_live", "varlamov_news", "Reddit",
             "spb_smi", "moscowtimes_ru", "newsparserchannel"]
# Список предлагаемых каналов
sub_list = ["КБ", "Лента дня", "Лентач", "Mash", "Москва Live", "Varlamov News", "Reddit",
            "SPB Live", "The Moscow Times", "test", "✅Подтвердить выбор"]

moderator_id = 898568790
support_id = 788259192
administartor_id = 898568790


@bot.message_handler(commands=["create_db"])
def create_db(message):
    if message.chat.id == administartor_id:
        connect = sqlite3.connect('users_db')
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS user(
                   id INTEGER,
                   channels TEXT,
                   premium INTEGER,
                   registration INTEGER
               )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS standart_channels(
                       id TEXT,
                       channel TEXT,
                       name TEXT
                   )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS premium_channels(
                           id_p TEXT,
                           channel_p TEXT
                       )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS post(
                       id TEXT,
                       message TEXT
                   )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS support(
                       id INTEGER,
                       history TEXT
                   )""")
        for i in range(len(sub_links)):
            cursor.execute(f'INSERT INTO standart_channels(id, channel, name) VALUES(?,?,?);',
                           (i, sub_links[i], sub_list[i]))
        bot.send_message(administartor_id, f'База данных создана')

        connect.commit()


@bot.message_handler(commands=["start"])
def start(message):
    if (message.chat.id not in [moderator_id, support_id]) or message.chat.id == administartor_id:
        connect = sqlite3.connect('users_db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM user WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        if data is None:
            cursor.execute(f'INSERT INTO user(id, channels, premium, registration) VALUES(?,?,?,?);',
                           (message.chat.id, "", 0, 0))

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard1 = types.KeyboardButton(text="Регистрация")
            markup.add(keyboard1)

            bot.send_message(message.chat.id, f"{message.chat.first_name}, добро пожаловать в NewsFlow!\n"
                                              f"Наш бот позволяет вам просматривать новости "
                                              f"из разных источников в одной ленте.\n"
                                              f"Хотите зарегистрироваться?", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Вы уже авторизованы\nДля того чтобы увидеть список команд введите"
                                              f" /list")
        connect.commit()
    elif message.chat.id == moderator_id:
        connect = sqlite3.connect('users_db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM user WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        if data is None:
            cursor.execute(f'INSERT INTO user(id, channels, premium, registration) VALUES(?,?,?,?);',
                           (message.chat.id, "", 0, 0))
        connect.commit()
        moder_help()
    else:
        connect = sqlite3.connect('users_db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM user WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        if data is None:
            cursor.execute(f'INSERT INTO user(id, channels, premium, registration) VALUES(?,?,?,?);',
                           (message.chat.id, "", 0, 0))
        connect.commit()
        support_help()

@bot.message_handler(commands=['list'])
def list(message):
    com_list = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.chat.id not in [moderator_id, support_id] or administartor_id:

        connect = sqlite3.connect("users_db")
        cursor = connect.cursor()
        cursor.execute(f"SELECT premium FROM user WHERE id = {message.chat.id}")
        prem = [*cursor.fetchone()][0]


        if not prem:
            keyboard1 = types.KeyboardButton(text="Купить подписку")
            com_list.append(keyboard1)
        else:
            keyboard1 = types.KeyboardButton(text="Отменить подписку")
            com_list.append(keyboard1)
        keyboard2 = types.KeyboardButton(text="Добавить каналы")
        com_list.append(keyboard2)
        keyboard3 = types.KeyboardButton(text="Сменить выбор каналов")
        com_list.append(keyboard3)
        keyboard7 = types.KeyboardButton(text="Список каналов")
        com_list.append(keyboard7)
        if prem:
            keyboard4 = types.KeyboardButton(text="Добавить свои каналы")
            keyboard6 = types.KeyboardButton(text="Изменить свои каналы")
            keyboard8 = types.KeyboardButton(text="Список своих каналов")
            com_list.append(keyboard4)
            com_list.append(keyboard6)
            com_list.append(keyboard8)
        keyboard5 = types.KeyboardButton(text="Поддержка и предложения")
        com_list.append(keyboard5)
        if message.chat.id == administartor_id:
            keyboard9 = types.KeyboardButton(text="Удаление из БД(Админ)")
            com_list.append(keyboard9)
            keyboard10 = types.KeyboardButton(text="/create_db")
            com_list.append(keyboard10)
            keyboard11 = types.KeyboardButton(text="test")
            com_list.append(keyboard11)
        connect.commit()
    elif message.chat.id == moderator_id or administartor_id:
        keyboard12 = types.KeyboardButton(text="Помощь модератору")
        com_list.append(keyboard12)
    elif message.chat.id == support_id or administartor_id:
        keyboard13 = types.KeyboardButton(text="Помощь поддержке")
        com_list.append(keyboard13)
    markup.add(*com_list)
    bot.send_message(message.chat.id, f'Список команд', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def text(message):
    chat_id = message.chat.id
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    if message.text in sub_list:
        cursor.execute(f"SELECT premium FROM user WHERE id = {chat_id}")
        premium_from_db = [*cursor.fetchone()][0]
        cursor.execute(f"SELECT channels FROM user WHERE id = {chat_id}")
        channels = []
        channels[:] = [*cursor.fetchone()][0].split()
        cursor.execute(f"SELECT registration FROM user WHERE id = {chat_id}")
        reg = [*cursor.fetchone()][0]
        if len(channels) != 5 or premium_from_db:
            if message.chat.type == 'private':

                for i in range(10):
                    sub = [*cursor.execute(f"SELECT name FROM standart_channels WHERE id = {i}").fetchone()][0]
                    if message.text == sub:
                        if channels.count(str(i)) == 0:
                            channels.append(f"{i}")
                            bot.send_message(chat_id, f"Канал {sub} добавлен")
                        else:
                            bot.send_message(chat_id, f"Канал {sub} уже добавлен")

                if (len(channels) == 5 and premium_from_db == 0) or len(
                        channels) == 9 or message.text == '✅Подтвердить выбор':
                    if not reg:
                        cursor.execute(f'UPDATE user set registration=1 WHERE id = {chat_id}')
                        connect.commit()
                        bot.send_message(chat_id, f"Регистрация завершена\nСкоро здесь появятся посты, из выбранных "
                                                  f"вами источников\nДля того чтобы увидеть список команд "
                                                  f"напишите /list", reply_markup=types.ReplyKeyboardRemove())
                    else:
                        bot.send_message(chat_id, f"Выбор подтвержден\nИзменения скоро вступят в силу",
                                         reply_markup=types.ReplyKeyboardRemove())
                        bot.send_message(chat_id, f'Хотите вернуться к списку команд? /list')
                enter_channels_in_db(message, channels)
        else:
            bot.send_message(chat_id, f"В бесплатной версии действует ограничение на количество каналов - 5")
    else:
        if message.text == 'Регистрация':
            bot.send_message(chat_id, f"Для того чтобы начать пользоваться ботом выберите интересующие "
                                      f"вас новостные каналы\n"
                                      f"В бесплатной версии бота вам доступно 5 каналов")
            add_channels(message)
        elif message.text == 'Купить подписку':
            subscription(message)
        elif message.text == 'Отменить подписку':
            cursor.execute(f'UPDATE user set premium=0 WHERE id = {chat_id}')
            cursor.execute(f'DELETE FROM premium_channels WHERE id_p = {chat_id}')
            cursor.execute(f"SELECT channels FROM user WHERE id = {chat_id}")
            channels = []
            channels[:] = [*cursor.fetchone()][0].split()
            connect.commit()
            bot.send_message(chat_id, f'Подписка успешно отменена\nВы можете заново ее подключить в любое время',
                             reply_markup=types.ReplyKeyboardRemove())
            if len(channels) > 5:
                bot.send_message(chat_id, f'Так как вы подписаны на более чем 5 каналов, доступных в бесплатной '
                                          f'версии бота вам необходимо решить какие каналы оставить')
                change_channel_choice(message)
            else:
                bot.send_message(chat_id, f'Хотите вернуться к списку команд? /list')
        elif message.text == 'Да':
            cursor.execute(f'UPDATE user set premium=1 WHERE id = {chat_id}')
            connect.commit()
            bot.send_message(chat_id, f'Поздравляем с приобретением подписки!',
                             reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id, f'Хотите вернуться к списку команд? /list')
        elif message.text == 'Нет':
            bot.send_message(chat_id, f'Вы можете купить премиум в любое время',
                             reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id, f'Хотите вернуться к списку команд? /list')
        elif message.text == 'Добавить каналы':
            add_channels(message)
        elif message.text == 'Сменить выбор каналов':
            change_channel_choice(message)
        elif message.text == 'Список каналов':
            show_channels(message, 0)
        elif message.text == 'Поддержка и предложения':
            bot.send_message(message.chat.id, f'Введите ваш вопрос или предлложение в формате:\n\n'
                                              'Поддержка\n'
                                              '"Ваш вопрос или предложение"')
            bot.send_message(message.chat.id, f'Если вы хотите пожаловаться на новость обязательно укажите ее Id в '
                                              f'конце сообщения')
        elif message.text.split()[0] == 'Поддержка':
            support(message)
        elif message.text == 'Добавить свои каналы':
            add_premium_channels(message)
        elif message.text == 'Изменить свои каналы':
            cursor.execute(f'DELETE FROM premium_channels WHERE id_p = {chat_id}')
            connect.commit()
            add_premium_channels(message)
        elif message.text == 'Список своих каналов':
            show_channels(message, 1)
        elif message.text.split()[0].count('https://t.me/') == 1:
            cnt_entered_channels = len(message.text.split())
            entered_channels = message.text.split()
            cursor.execute(f'SELECT premium FROM user WHERE id = {chat_id}')
            data = [*cursor.fetchone()][0]
            if data == 1:
                if cnt_entered_channels > 5:
                    bot.send_message(message.chat.id, f'Вы указали более 5 каналов\n'
                                                      f'Введите список состоящий из менее 6 каналов')
                else:
                    cnt = len(cursor.execute(
                        f'SELECT channel_p FROM premium_channels WHERE id_p = {message.chat.id}').fetchall())
                    if 5 - cnt < cnt_entered_channels:
                        bot.send_message(message.chat.id, f'Вы можете добавить еще {5 - cnt} каналов\n'
                                                          f'Введите новый список')
                    else:
                        for link in entered_channels:
                            cursor.execute(f'INSERT INTO premium_channels(id_p, channel_p) VALUES(?,?);',
                                           (message.chat.id, link[13::]))

                        bot.send_message(message.chat.id, f'Ваши каналы добавлены\nИзменения скоро вступят в силу')
                        bot.send_message(message.chat.id, f'Хотите вернуться к списку команд? /list')
            else:
                bot.send_message(message.chat.id, f'У вас нет доступа к этой функции\n'
                                                  f'Вы можете приобрести премиум подписку выбрав соответсвующий раздел'
                                                  f' в меню /list')
            connect.commit()
        elif message.text == 'Удаление из БД(Админ)' and message.chat.id == administartor_id:
            del_from_db_admin()
        elif message.chat.id == moderator_id and (message.text[:-1]).isdigit() and message.text[-1] == '+':
            parser2.post_request(message)
        elif message.text.split()[0].count('@') and message.chat.id == moderator_id:
            post_id = parser2.add_post_to_db(message)
            parser2.post_request(str(post_id) + '+')
        elif message.text.split()[0] == 'Ответ' and message.chat.id == support_id:
            support_answer(message)
        elif message.text.split()[0] == 'Закрыть' and message.chat.id == support_id:
            support_close(message)
        elif message.text.split()[0] == 'Модератор' and message.chat.id == support_id:
            bot.send_message(moderator_id, f'Жалоба на пост:\n{message.text[message.text.find('\n'):]}')
        elif message.chat.id in [administartor_id, moderator_id, support_id] and message.text == "Помощь модератору":
            moder_help()
        elif message.chat.id in [administartor_id, moderator_id, support_id] and message.text == "Помощь поддержке":
            support_help()
        elif message.chat.id == moderator_id and message.text.split()[0] == "Получить":
            cursor.execute(f'SELECT message FROM post WHERE id={message.text.split()[1]}')
            post = [*cursor.fetchone()][0]
            bot.send_message(moderator_id, post)
            connect.commit()
        else:
            bot.send_message(message.chat.id, f'Я не знаю такой команды\nПопробуйте еще раз!')


def support_help():
    bot.send_message(support_id, f'Специалист поддержки должен отвечать на вопросы пользователей и сообщать '
                                 f'администратору о существующих проблемах в работе бота\n\nДля того чтобы ответить '
                                 f'на вопрос пользователя необходимо ввести сообщение следующего вида:\nОтвет\n'
                                 f'12345678(ID пользователя который выводится вместе с вопросом)\n'
                                 f'"Ответ поддержки"\n\nДля того чтобы направить жалобу на новость модератору '
                                 f'необходимо ввести сообщение следующего вида:\n Модератор\n"Скопированная жалоба '
                                 f'пользователя вместе с его id"\n\nДля того чтобы закрыть вопрос пользователя '
                                 f'необходимо отправить "Закрыть\nid пользователя')
def moder_help():
    bot.send_message(moderator_id, f'В обязанности модератора входит проверка постов и их редактирование '
                                   f'по необходимости\n\nДля того, чтобы одобрить пост необходимо написать id '
                                   f'новости+\nПример: 123+\n\nДля того чтобы отредактировать новость необходимо '
                                   f'скопировать сообщение, внести изменения и отправить без id\n\nМодератору могут '
                                   f'приходить жалобы на новости от техничсекой поддержки.\nДля того, чтобы внести '
                                   f'изменение в пост необходимо получить новость из базы данных, скопировать ее без id,'
                                   f' внести изменения и отправить\nДля того, чтобы получить новость необходимо '
                                   f'отправить "Получить id новости"\nПример: Получить 123')
def add_channels(message):
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    cursor.execute(f"SELECT premium FROM user WHERE id = {message.chat.id}")
    premium = [*cursor.fetchone()][0]
    cursor.execute(f"SELECT channels FROM user WHERE id = {message.chat.id}")
    channels = []
    channels[:] = [*cursor.fetchone()][0].split()
    markup_channels = []
    if ((premium or len(channels) < 5) and len(channels) != 9):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(9):
            sub = [*cursor.execute(f"SELECT name FROM standart_channels WHERE id = {i}").fetchone()][0]
            if channels.count(str(i)) == 0:
                markup_channels.append(types.KeyboardButton(text=f"{sub}"))

        markup_channels.append(types.KeyboardButton(text="✅Подтвердить выбор"))
        markup.add(*markup_channels)
        bot.send_message(message.chat.id, f'Выберите каналы на которые хотите подписаться', reply_markup=markup)
    elif premium and len(channels) == 9:
        bot.send_message(message.chat.id, f'Вы уже подписаны на все каналы')
    else:
        bot.send_message(message.chat.id, f'Вы уже подписаны на максимальное количество каналов '
                                          f'бесплатной версии бота')
    connect.commit()


def add_premium_channels(message):
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    idp = message.chat.id
    cnt = len(cursor.execute(f'SELECT channel_p FROM premium_channels WHERE id_p = {idp}').fetchall())

    if cnt < 5:
        bot.send_message(message.chat.id, f'Введите список каналов, на которые хотите подписаться '
                                          f'в формате:\n'
                                          f'https://t.me/Channel1\n'
                                          f'https://t.me/Channel2\n'
                                          f'https://t.me/Channel3\n'
                                          f'https://t.me/Channel4\n'
                                          f'https://t.me/Channel5\n')
        bot.send_message(message.chat.id, f'Вы можете добавить {5 - cnt} каналов')
    else:
        bot.send_message(message.chat.id, f'Вы уже добавили максимальное количество своих каналов\n'
                                          f'Если хотите поменять свой выбор воспользуйтесь функцией "Изменить '
                                          f'свои каналы" в разделе /list')
    connect.commit()


def subscription(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard1 = types.KeyboardButton(text="Да")
    keyboard2 = types.KeyboardButton(text="Нет")
    markup.add(keyboard1, keyboard2)

    bot.send_message(message.chat.id, f'Премиум статус снимает ограничение количества доступных каналов и '
                                      f'позволяет вам добавить 5 телеграмм каналов по своему вкусу\n'
                                      f'Вы действительно хотите приобрести подписку?', reply_markup=markup)


def change_channel_choice(message):
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    cursor.execute(f'UPDATE user set channels="" WHERE id = {message.chat.id}')
    connect.commit()
    bot.send_message(message.chat.id, f'Все подписки отменены\nВы можете выбрать новые каналы')
    add_channels(message)


def enter_channels_in_db(message, sub_channels):
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    cursor.execute(f'UPDATE user set channels="{" ".join(sub_channels)}" WHERE id = "{message.chat.id}"')
    connect.commit()


def support(message):
    connect = sqlite3.connect('users_db')
    cursor = connect.cursor()
    user = cursor.execute(f"SELECT id FROM support WHERE id = {message.chat.id}").fetchone()
    question = ' '.join(message.text.split()[1:])
    if user is None:
        cursor.execute(f'INSERT INTO support(id, history) VALUES(?,?);',
                       (message.chat.id, 'user: ' + question + '\n\n'))
        bot.send_message(support_id, str(message.chat.id) + '\nuser: ' + question + '\n\n')
        connect.commit()

    else:
        history = [*cursor.execute(f"SELECT history FROM support WHERE id = {message.chat.id}").fetchone()][0]
        try:
            cursor.execute(f'UPDATE support set history="{history + 'user: ' + question + '\n\n'}" WHERE id = "{message.chat.id}"')
        except TypeError as e:
            print(e)

        bot.send_message(support_id, str(message.chat.id) + '\n' + history + 'user: ' + question + '\n\n')
        connect.commit()

    bot.send_message(message.chat.id, f'Ваш запрос принят\nВ скором времени вы получите ответ в этом чате')
    bot.send_message(message.chat.id, f'Хотите вернуться к списку команд? /list')

def support_answer(message):
    user_id = message.text.split()[1]
    answer = ' '.join(message.text.split()[2:])
    connect = sqlite3.connect('users_db')
    cursor = connect.cursor()
    history = [*cursor.execute(f"SELECT history FROM support WHERE id = {user_id}").fetchone()][0]
    cursor.execute(f'UPDATE support set history="{history + 'support: ' + answer + '\n\n'}" WHERE id = {user_id}')
    bot.send_message(user_id, history + 'support: ' + answer + '\n\n')
    bot.send_message(support_id, f'Ответ отправлен')
    connect.commit()

def support_close(message):
    connect = sqlite3.connect('users_db')
    cursor = connect.cursor()
    cursor.execute(f'DELETE FROM support WHERE id={int(message.text.split()[1])}')
    connect.commit()
def show_channels(message, prem):
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    show_list = []
    if not prem:
        cursor.execute(f"SELECT channels FROM user WHERE id = {message.chat.id}")
        channels = []
        channels[:] = [*cursor.fetchone()][0].split()
        for idc in channels:
            sub = [*cursor.execute(f"SELECT name FROM standart_channels WHERE id = {int(idc)}").fetchone()][0]
            show_list.append(sub)
    else:
        show_list = cursor.execute(f'SELECT channel_p FROM premium_channels WHERE id_p = {message.chat.id}').fetchall()
        for i in range(len(show_list)): show_list[i] = show_list[i][0]
    if len(show_list):
        bot.send_message(message.chat.id, f'Список своих каналов, на которые вы подписаны:\n' + "\n".join(show_list))
    else:
        bot.send_message(message.chat.id, f'Вы не добавили ни одного канала')
    connect.commit()

def del_from_db_admin():
    bot.send_message(administartor_id, f'Запись администратора удалена из базы данных')
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    cursor.execute(f"DELETE FROM user WHERE id = {administartor_id}")
    connect.commit()


def send_post_to_users(message):
    connect = sqlite3.connect("users_db")
    cursor = connect.cursor()
    channel = message.split()[0][1::]
    if channel in sub_links:
        channel_id = [*cursor.execute(f'SELECT id FROM standart_channels WHERE channel = "{channel}"').fetchone()][0]
        sub_user_list = [*cursor.execute(f'SELECT id, channels FROM user').fetchall()]
        for i in range(len(sub_user_list)):
            if str(channel_id) in sub_user_list[i][1].split():
                bot.send_message(int(sub_user_list[i][0]), message)
    else:
        sub_user_list = [*cursor.execute(f'SELECT id_p FROM premium_channels WHERE channel_p = "{channel}"').fetchall()]
        for i in range(len(sub_user_list)):
            bot.send_message(int(sub_user_list[i][0]), message)
    connect.commit()


def send_post_to_modder(message, post_id):
    news, source, db_id = '', '', ''
    if message.text is not None:
        news, source, db_id = message.text, message.chat.username, post_id
    elif message.caption is not None:
        news, source, db_id = message.caption, message.chat.username, post_id
    bot.send_message(moderator_id, f'@{source}\n{news}\n\nId новости: {post_id}')

if __name__ == '__main__':
    bot.polling()


#в видосе нет отправки сообщения модеру от техподдержки
#не реализовано удаление из бд истории переписки с пользователем
#не реализовано удаление новостей из бд при достижении определенного количества
