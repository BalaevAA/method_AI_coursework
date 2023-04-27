import telebot
import pickle
from sklearn.feature_extraction.text import CountVectorizer


token = '5908448826:AAFyiDCuk3Y3i1R-uoEZa1K6jKbjtXFaPAg'
bot = telebot.TeleBot(token)


with open('./models/model_clf.pkl', 'rb') as fid:
    model_multNB = pickle.load(fid)

with open('./models/clf.pkl', 'rb') as fid:
    model_Adaboost = pickle.load(fid)

with open('./cv/cv.pk', 'rb') as fid:
    multiNB_cv = pickle.load(fid)

with open('./cv/cv_adaboost.pk', 'rb') as fid:
    adaboost_cv = pickle.load(fid)


def preprocess_multiNB(user_input):
    return multiNB_cv.transform([user_input])

def preprocess_adaboost(user_input):
    return adaboost_cv.transform([user_input])

preporocess = [preprocess_multiNB, preprocess_adaboost]
models = [(model_multNB, 'MultiNB'), (model_Adaboost, 'Adaboost')]
admins = [274400365, 465949389]

model = 0

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

@bot.message_handler(commands=["set_model"])
def set_model(message):
    if (message.chat.type == 'private' and message.chat.id in admins):
        global model
        split = message.text.split()
        model = int(split[1]) - 1
        bot.send_message(chat_id=message.chat.id, text=f'Модель изменена на {models[model][1]}')
    else:
         bot.send_message(chat_id=message.chat.id, text='Команда доступна только в личных сообщениях и только администратору')

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
    if (message.chat.type == 'group' or message.chat.type == 'supergroup'):
        preprocessed_input = preporocess[model](user_input)
        prediction = models[model][0].predict(preprocessed_input)
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
        res = ''
        for i in range(len(models)):
            prep = preporocess[i](user_input)
            prediction_multiNB = models[i][0].predict(prep)
            res += f'{models[i][1]}: {convert_result(prediction_multiNB)}\n\n'
        bot.send_message(message.chat.id, res)

if __name__ == '__main__':
     bot.infinity_polling()
