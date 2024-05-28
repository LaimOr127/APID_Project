from pyrogram import Client, filters
from config import api_id, api_hash, bot_token
import Bot
import sqlite3

connect = sqlite3.connect('users_db')
cursor = connect.cursor()
plist = [*cursor.execute(f'SELECT channel_p FROM premium_channels').fetchall()]

for i in range(len(plist)):
    plist[i] = plist[i][0]

slist = [*cursor.execute(f'SELECT channel FROM standart_channels').fetchall()]
for i in range(len(slist)):
    slist[i] = slist[i][0]

connect.commit()

SOURCE_PUBLICS = slist + plist

app = Client("parser1", api_id=api_id, api_hash=api_hash, phone_number="+79687727684")


@app.on_message(filters.chat(SOURCE_PUBLICS))
def new_channel_post(client, message):
    post_id = add_post_to_db(message)
    Bot.send_post_to_modder(message, post_id)


def add_post_to_db(message):
    connect = sqlite3.connect('users_db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT id FROM post')
    new_id = len(cursor.fetchall()) + 1
    if message.chat.id != Bot.moderator_id:
        news = ''
        if message.text is not None:
            news = '@' + message.chat.username + '\n' + message.text
        elif message.caption is not None:
            news = '@' + message.chat.username + '\n' + message.caption

        cursor.execute(f'INSERT INTO post(id, message) VALUES(?,?);',
                       (new_id, news + '\n\n' + 'Id новости: ' + str(new_id)))
        connect.commit()
    else:
        print(1)
        cursor.execute(f'INSERT INTO post(id, message) VALUES(?,?);',
                       (new_id, message.text + '\n\n' + 'Id новости: ' + str(new_id)))
        connect.commit()

    return new_id


def post_request(message):
    try:
        post_id = message.text[:-1]
    except:
        post_id = message[:-1]
    connect = sqlite3.connect('users_db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT message FROM post WHERE id={post_id}')
    post = [*cursor.fetchone()][0]
    if post is None:
        Bot.bot.send_message(898568790, '`ERROR NO POST ID IN DB`')
        return
    try:
        Bot.send_post_to_users(post)
    except Exception as e:
        Bot.bot.send_message(898568790, f'`ERROR {e}`')
    connect.commit()


if __name__ == '__main__':
    print('Atempt to run telegrabber')
    app.run()
