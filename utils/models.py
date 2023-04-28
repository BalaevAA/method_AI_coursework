import pickle
from configuration import cv_path, multiNB_path, adaboost_path, catboost_path


def get_models(model_path):
    with open(model_path, 'rb') as fid:
            return pickle.load(fid)
    
cv = get_models(cv_path)

def preprocess(user_input):
    return cv.transform([user_input])

models = [(get_models(multiNB_path), 'MultiNB'), (get_models(adaboost_path), 'Adaboost'), (get_models(catboost_path), 'catboost')]
