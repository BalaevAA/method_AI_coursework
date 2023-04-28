import telebot
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import sqlite3
from database.db import database
from configuration import token
from utils.strings import convert_result, help_msg
from utils.models import models, preprocess

bot = telebot.TeleBot(token)
db = database('models.db')

@bot.message_handler(commands=["set_model"])
def set_model(message):
    db.new_chat(chat_id = message.chat.id)
    split = message.text.split()
    if(message.chat.type == 'private'):
        bot.send_message(chat_id=message.chat.id, text='Команда доступна только в чатах')
    else:
        status = bot.get_chat_member(message.chat.id, message.from_user.id).status
        if(status != 'member'):
                db.change_model(chat_id=message.chat.id, model_id=int(split[1]) - 1)
                try:

                    bot.send_message(chat_id=message.chat.id, text=f'Модель сменена на {models[int(split[1]) - 1][1]}')
                except:
                    bot.send_message(chat_id=message.chat.id, text=f'Напишите число от 1 до {len(models)} после команды /set_model')
        else:
            bot.send_message(chat_id=message.chat.id, text=f'Вы не администратор в этой группе. У вас нет прав:(')

@bot.message_handler(content_types=["new_chat_members"])
def new_user(message):
    bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, привет, здесь банят за спам и очень ждут актуальных новостей от тебя!')


@bot.message_handler(commands=["start", "help"])
def help(message):
    bot.send_message(chat_id=message.chat.id, 
                        text=help_msg)

@bot.message_handler(content_types=["text"])
def get_messages(message): 
    user_input = message.text
    if (message.chat.type == 'group' or message.chat.type == 'supergroup'):
        model_local = db.get_model_id(message.chat.id)
        preprocessed_input = preprocess(user_input)
        prediction = models[model_local][0].predict(preprocessed_input)
        if(prediction == 2):
            status = bot.get_chat_member(message.chat.id, message.from_user.id).status
            bans = db.get_ban_counts(chat_id=message.chat.id, user_id=message.from_user.id)
            if(status != 'member'):
                bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username} написал спам, но он администратор\nЕму можно')
                return
            if(bans == 0):
                db.set_ban_counts(chat_id=message.chat.id, user_id=message.from_user.id, number_of_ban=1)
                bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username} написал спам!')
            elif(bans == 1):
                db.set_ban_counts(chat_id=message.chat.id, user_id=message.from_user.id, number_of_ban=2)
                bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, последнее предупреждение!')
            else:
                bot.ban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
                bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username} забанен!')
                bot.unban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        elif(prediction == 1):
            bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, спасибо за актуальные новости!')
    else:
        res = ''
        for i in range(len(models)):
            prep = preprocess(user_input)
            prediction_multiNB = models[i][0].predict(prep)
            res += f'{models[i][1]}: {convert_result(prediction_multiNB)}\n\n'
        bot.send_message(message.chat.id, res)


if __name__ == '__main__':
     bot.infinity_polling()


# @bot.message_handler(commands=["set_model"])
# def set_model(message):
#     if (message.chat.type == 'private' and message.chat.id in admins):
#         try:
#             global model
#             split = message.text.split()
#             model = int(split[1]) - 1
#             bot.send_message(chat_id=message.chat.id, text=f'Модель изменена на {models[model][1]}')
#         except:
#             bot.send_message(chat_id=message.chat.id, text=f'Напишите число от 1 до {len(models)} после команды /set_model')
#     else:
#          bot.send_message(chat_id=message.chat.id, text='Команда доступна только в личных сообщениях и только администратору')

# @bot.message_handler(content_types=["text"])
# def get_messages(message): 
#     user_input = message.text
#     if (message.chat.type == 'group' or message.chat.type == 'supergroup'):
#         preprocessed_input = preporocess[model](user_input)
#         prediction = models[model][0].predict(preprocessed_input)
#         if(prediction == 2):
#             if(message.from_user.id not in d.keys()):
#                 d[message.from_user.id]=1
#                 bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username} написал спам!')
#             elif(d[message.from_user.id] == 1):
#                 d[message.from_user.id] += 1
#                 bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, последнее предупреждение!')
#             else:
#                 bot.ban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
#                 bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username} забанен!')
#                 bot.unban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
#             bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

#         elif(prediction == 1):
#             bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, спасибо за актуальные новости!')
#     else:
#         res = ''
#         for i in range(len(models)):
#             prep = preporocess[i](user_input)
#             prediction_multiNB = models[i][0].predict(prep)
#             res += f'{models[i][1]}: {convert_result(prediction_multiNB)}\n\n'
#         bot.send_message(message.chat.id, res)


# def create(con):
#     try:
#         con.execute("create table models(chat_id int, model_id int)")
#     except:
#         pass

# def new_chat(con, chat_id):
#     cur = con.cursor()
#     cur.execute(f"insert into models(chat_id, model_id) values({chat_id}, 1)")
#     con.commit()

# def change_model(con, chat_id, model_id):
#     cur = con.cursor()
#     cur.execute(f"update models set model_id={model_id} where chat_id={chat_id}")
#     con.commit()

# def get_model_id(con, chat_id):
#     cur = con.cursor()
#     try:
#         res = cur.execute(f"select model_id from models where chat_id={chat_id}").fetchone()[0]
#     except:
#         new_chat(con, chat_id)
#         return 1
#     return res