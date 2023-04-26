import telebot
import pickle
from sklearn.feature_extraction.text import CountVectorizer


token = '5908448826:AAFyiDCuk3Y3i1R-uoEZa1K6jKbjtXFaPAg'
bot = telebot.TeleBot(token)


with open('model_clf.pkl', 'rb') as fid:
    model = pickle.load(fid)

with open('cv.pk', 'rb') as fid:
    cv = pickle.load(fid)


def preprocess(user_input):
    return cv.transform([user_input])


def convert_result(res):
    d = {0: 'Это обычное сообщение. Оно не является ни спамом, ни новостью',
         1: 'Данное сообщение является новостным',
         2: 'Данное сообщение является спамом'}
    return d[res[0]]

d = {}
help_msg="""Привет. Я чат-бот, призванный бороться со спамом!
Пока что я умею отличать только три `типа разных сообщений:
1) **Спам-сообщения**, за такое ты можешь быть исключен из группы
2) **Новостные сообщения**, такие сообщения приветсвуются, за них я всегда благодарю
3) **Обычные сообщения**, я никак не отреагирую на него в групповом чате, но точно скажу тебе в личке, что это не новость и не спам:)"""


@bot.message_handler(content_types=["new_chat_members"])
def new_user(message):
    bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, привет, здесь банят за спам и очень ждут актуальных новостей от тебя!')

@bot.message_handler(commands=["start", "help"])
def help(message):
    if (message.chat.type == 'private'):
        bot.send_message(chat_id=message.chat.id, 
                        text=help_msg)
        
@bot.message_handler(content_types=["text"])
def get_messages(message): 
    user_input = message.text
    preprocessed_input = preprocess(user_input)
    prediction = model.predict(preprocessed_input)
    if (message.chat.type == 'group' or message.chat.type == 'supergroup'):
        if(prediction == 2):
            if(message.from_user.id not in d.keys()):
                d[message.from_user.id]=1
                bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username} написал спам!')
            elif(d[message.from_user.id] == 1):
                d[message.from_user.id] += 1
                bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, последнее предупреждение!')
            else:
                bot.ban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
                bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username} забанен!')
                bot.unban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        elif(prediction == 1):
            bot.send_message(chat_id=message.chat.id, text=f'@{message.from_user.username}, спасибо за актуальные новости!')
    else:
        convert_res = convert_result(prediction)
        bot.send_message(message.chat.id, convert_res)

if __name__ == '__main__':
     bot.infinity_polling()
