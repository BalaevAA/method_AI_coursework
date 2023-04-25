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


@bot.message_handler(content_types=["text"])
def get_messages(message): 
    user_input = message.text
    preprocessed_input = preprocess(user_input)
    prediction = model.predict(preprocessed_input)
    convert_res = convert_result(prediction)
    bot.send_message(message.chat.id, convert_res)


if __name__ == '__main__':
     bot.infinity_polling()