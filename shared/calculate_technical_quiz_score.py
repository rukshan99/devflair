import pandas as pd
import numpy as np
import nltk
import re
import gensim
import string
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from gensim.models.doc2vec import TaggedDocument
from tqdm import tqdm
import multiprocessing
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
stopwords = stopwords.words("english")
import nltk
nltk.download("stopwords")
from sklearn import utils

def clean_data(text):
    text = ''.join([ele for ele in text if ele not in string.punctuation])
    text = text.lower()
    text = ' '.join([ele for ele in text.split() if ele not in stopwords])
    return text

def prepare_answers(model_answers, candidate_answers):
    arr = []
    no_answers = len(candidate_answers)
    for x in range (no_answers):
        arr.append(candidate_answers[x]['answer'])
    for x in range (no_answers):
        arr.append(model_answers[x]['modelAnswer'])
    return arr

def calculate_technical_quiz_score(data, quiz_length):
    data = list(map(clean_data, data))
    
    tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(data)]
    
    #Building a vocabulary
    model = gensim.models.doc2vec.Doc2Vec(vector_size=30, min_count=2, epochs=80)
    model.build_vocab([x for x in tqdm(tagged_data)])
    
    model.train(tagged_data, total_examples=model.corpus_count, epochs=80)
    
    total_score = 0
    quiz_size = quiz_length ##-> No of questions in the quiz
    
    for x in range (quiz_size):
        y = x+quiz_size
        similarity = model.dv.similarity(x , y)
        total_score = total_score + similarity
    
    final_score = (total_score/quiz_size) * 100
    return final_score

def get_quiz_score(model_answers, candidate_answers):
    arr = prepare_answers(model_answers, candidate_answers)
    quiz_length = len(candidate_answers)
    score = calculate_technical_quiz_score(arr, quiz_length)
    return score