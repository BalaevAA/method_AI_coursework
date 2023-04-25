import telegram
from telegram.ext import Updater, MessageHandler, Filters
import numpy as np
from keras.models import load_model
import pickle
import nltk
import re
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import CountVectorizer

# Load the pre-trained model
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

# Define the message handler
def message_handler(update, context):
    # Get the user's message
    user_input = update.message.text

    # Preprocess the user's input
    preprocessed_input = preprocess(user_input)

    # Feed the preprocessed input into the model
    prediction = model.predict(preprocessed_input)

    # Convert the prediction to text
    convert_res = convert_result(prediction)

    # Return the prediction to the user
    update.message.reply_text(convert_res)

# Set up the Telegram bot
updater = Updater('5908448826:AAFyiDCuk3Y3i1R-uoEZa1K6jKbjtXFaPAg', use_context=True)
dispatcher = updater.dispatcher

# Add the message handler
dispatcher.add_handler(MessageHandler(Filters.text, message_handler))

# Start the bot
updater.start_polling()
