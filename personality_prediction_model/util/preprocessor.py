import pandas
import numpy
import pickle
import re
import unidecode
import nltk
import emoji
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load("en_core_web_sm")

# Loading Doc2Vec pickle files
loc = '2022-014/personality_prediction_model/pickle_files/v3/'
with open(loc + 'model_opn_d2v.pickle', 'rb') as f:
    model_OPN_d2v = pickle.load(f)
with open(loc + 'model_con_d2v.pickle', 'rb') as f:
    model_CON_d2v = pickle.load(f)
with open(loc + 'model_ext_d2v.pickle', 'rb') as f:
    model_EXT_d2v = pickle.load(f)
with open(loc + 'model_agr_d2v.pickle', 'rb') as f:
    model_AGR_d2v = pickle.load(f)
with open(loc + 'model_neu_d2v.pickle', 'rb') as f:
    model_NEU_d2v = pickle.load(f)
    
# Preprocessor version 1 for PPF v2 and v2.1 (NLTK SentimentIntensityAnalyzer based approach)
def preprocessor_v1(text):
    # Preprocessing Linkedin profile summaries
    NEG_INDEX = 0
    POS_INDEX = 1
    NEU_INDEX = 2
    COMP_INDEX = 3
    
    text_data = []
    
    text_data.insert(NEG_INDEX, 0)
    text_data.insert(POS_INDEX, 0)
    text_data.insert(NEU_INDEX, 0)
    text_data.insert(COMP_INDEX, 0)
    
    sid = SentimentIntensityAnalyzer()
    """
    pos: positive
    neg: negative
    neu: neutral
    compound: aggregated score for the sentence
    """
    ss = sid.polarity_scores(text)
    text_data[NEG_INDEX] = ss["neg"]
    text_data[POS_INDEX] = ss["pos"]
    text_data[NEU_INDEX] = ss["neu"]
    text_data[COMP_INDEX] = ss["compound"]
    
    d = {'rowID': [0],
         'sentiNEG': [text_data[NEG_INDEX]],
         'sentiPOS': [text_data[POS_INDEX]],
         'sentiNEU': [text_data[NEU_INDEX]],
         'sentiCOMPOUND': [text_data[COMP_INDEX]],
         'cEXT': [0],
         'cNEU': [0],
         'cAGR': [0],
         'cCON': [0],
         'cOPN': [0]}
    text_df = pandas.DataFrame(data=d)
        
    return text_df

# Preprocessor version 2 for PPF v3 (Doc2Vec based approach)
def preprocessor_v2(text):
    # make global variables
    global nlp
    global model_OPN_d2v
    global model_CON_d2v
    global model_EXT_d2v
    global model_AGR_d2v
    global model_NEU_d2v
    
    # Handle foreign letters
    text = unidecode.unidecode(text)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Make the string lower-case
    text = text.lower()

    tokens = nlp(text)
    
    words = set(nltk.corpus.words.words())

    tokens = [ti for ti in tokens if ti.lower_ not in STOP_WORDS]
    tokens = [ti for ti in tokens if not ti.is_space]
    tokens = [ti for ti in tokens if not ti.is_punct]
    tokens = [ti for ti in tokens if not ti.like_num]
    tokens = [ti for ti in tokens if not ti.like_url]
    tokens = [ti for ti in tokens if not ti.like_email]
    tokens = [ti for ti in tokens if ti.lower_ in words]

    # lemmatize
    tokens = [ti.lemma_ for ti in tokens if ti.lemma_ not in STOP_WORDS]
    tokens = [ti for ti in tokens if len(ti) > 1]
    
    vectors_opn = model_OPN_d2v.infer_vector(tokens, epochs=20)
    vectors_con = model_CON_d2v.infer_vector(tokens, epochs=20)
    vectors_ext = model_EXT_d2v.infer_vector(tokens, epochs=20)
    vectors_agr = model_AGR_d2v.infer_vector(tokens, epochs=20)
    vectors_neu = model_NEU_d2v.infer_vector(tokens, epochs=20)
    
    vectors = {'vectors_opn': vectors_opn, 'vectors_con': vectors_con, 'vectors_ext': vectors_ext, 'vectors_agr':vectors_agr, 'vectors_neu': vectors_neu}
    
    return vectors

# Preprocessor version 3 for PPF v4 (fastText based approach)
def preprocessor_v3(text):
    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Make the string lower-case
    text = text.lower()
    
    return text
    
    