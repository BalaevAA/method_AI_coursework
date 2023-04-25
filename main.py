import telebot
import config
import numpy as np
import pickle
import nltk
import re
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer


token = '5908448826:AAFyiDCuk3Y3i1R-uoEZa1K6jKbjtXFaPAg'
bot = telebot.TeleBot(config.token)


with open('model_clf.pkl', 'rb') as fid:
    model = pickle.load(fid)


def preprocess(user_input):
    cv = CountVectorizer()
    lemm = WordNetLemmatizer()
    processed_text = []
    nltk.download('omw-1.4')
    text = re.sub('^a-zA-z',' ',user_input)
    words = text.split()
    words = [lemm.lemmatize(word) for word in words if word not in set(stopwords.words('russian'))]
    text_p = ' '.join(words)
    processed_text.append(text_p)
    return cv.fit_transform(processed_text).toarray()


def convert_result(res):
    d = {0: 'Это обычное сообщение. Оно не является ни спамом, ни новостью',
         1: 'Данное сообщение является новостным',
         2: 'Данное сообщение является спамом'}
    return d[res]


@bot.message_handler(content_types=["text"])
def get_messages(message): 
    user_input = message.text
    preprocessed_input = preprocess(user_input)
    prediction = model.predict(preprocessed_input)
    convert_res = convert_result(prediction)
    bot.send_message(message.chat.id, convert_res)


if __name__ == '__main__':
     bot.infinity_polling()
