import pickle
import fasttext

# Loading pickle files
# Models with the highest accuracy scores are used for each trait
loc_v2 = '2022-014/personality_prediction_model/pickle_files/v2.1/'
with open(loc_v2 + 'ppf_lr_opn.pickle', 'rb') as f:
    model_OPN_v2 = pickle.load(f)
with open(loc_v2 + 'ppf_gnb_con.pickle', 'rb') as f:
    model_CON_v2 = pickle.load(f)
with open(loc_v2 + 'ppf_knn_ext.pickle', 'rb') as f:
    model_EXT_v2 = pickle.load(f)
with open(loc_v2 + 'ppf_gnb_agr.pickle', 'rb') as f:
    model_AGR_v2 = pickle.load(f)
with open(loc_v2 + 'ppf_lr_neu.pickle', 'rb') as f:
    model_NEU_v2 = pickle.load(f)
    
loc_v3 = '2022-014/personality_prediction_model/pickle_files/v3/'
with open(loc_v3 + 'ppf_lr_opn.pickle', 'rb') as f:
    model_OPN_v3 = pickle.load(f)
with open(loc_v3 + 'ppf_lr_con.pickle', 'rb') as f:
    model_CON_v3 = pickle.load(f)
with open(loc_v3 + 'ppf_svm_ext.pickle', 'rb') as f:
    model_EXT_v3 = pickle.load(f)
with open(loc_v3 + 'ppf_rf_agr.pickle', 'rb') as f:
    model_AGR_v3 = pickle.load(f)
with open(loc_v3 + 'ppf_knn_neu.pickle', 'rb') as f:
    model_NEU_v3 = pickle.load(f)
    
loc_v4 = '2022-014/personality_prediction_model/pickle_files/v4/'
model_OPN_v4 = fasttext.load_model(loc_v4 + 'ppf_ft_opn.ftz')
model_CON_v4 = fasttext.load_model(loc_v4 + 'ppf_ft_con.ftz')
model_EXT_v4 = fasttext.load_model(loc_v4 + 'ppf_ft_ext.ftz')
model_AGR_v4 = fasttext.load_model(loc_v4 + 'ppf_ft_agr.ftz')
model_NEU_v4 = fasttext.load_model(loc_v4 + 'ppf_ft_neu.ftz')

def predictor_v1(df):
    # make models global variables
    global model_OPN_v2
    global model_CON_v2
    global model_EXT_v2
    global model_AGR_v2
    global model_NEU_v2
    
    cOPN = model_OPN_v2.predict(df.to_numpy()[:, 1:5])[0]
    cCON = model_CON_v2.predict(df.to_numpy()[:, 1:5])[0]
    cEXT = model_EXT_v2.predict(df.to_numpy()[:, 1:5])[0]
    cAGR = model_AGR_v2.predict(df.to_numpy()[:, 1:5])[0]
    cNEU = model_NEU_v2.predict(df.to_numpy()[:, 1:5])[0]
    
    return [cOPN, cCON, cEXT, cAGR, cNEU]

def predictor_v2(vectors):
    # make models global variables
    global model_OPN_v3
    global model_CON_v3
    global model_EXT_v3
    global model_AGR_v3
    global model_NEU_v3
    
    cOPN = model_OPN_v3.predict([vectors['vectors_opn']])[0]
    cCON = model_CON_v3.predict([vectors['vectors_con']])[0]
    cEXT = model_EXT_v3.predict([vectors['vectors_ext']])[0]
    cAGR = model_AGR_v3.predict([vectors['vectors_agr']])[0]
    cNEU = model_NEU_v3.predict([vectors['vectors_neu']])[0]
    
    return [cOPN, cCON, cEXT, cAGR, cNEU]

def predictor_v3(text):
    # make models global variables
    global model_OPN_v4
    global model_CON_v4
    global model_EXT_v4
    global model_AGR_v4
    global model_NEU_v4
    
    cOPN = 1 if model_OPN_v4.predict(text)[0][0] == '__label__1' else 0
    cCON = 1 if model_CON_v4.predict(text)[0][0] == '__label__1' else 0
    cEXT = 1 if model_EXT_v4.predict(text)[0][0] == '__label__1' else 0
    cAGR = 1 if model_AGR_v4.predict(text)[0][0] == '__label__1' else 0
    cNEU = 1 if model_NEU_v4.predict(text)[0][0] == '__label__1' else 0
    
    return [cOPN, cCON, cEXT, cAGR, cNEU]

def predictor_v4(df, vectors, text):
    # Predicting with highest accuracy models (from all the approaches combined) for each trait
    
    global model_OPN_v4 #fastText
    global model_CON_v4 #fastText
    global model_EXT_v2 #SVM + NLTK VADER Sentiment Intensity Analyzer
    global model_AGR_v4 #fastText
    global model_NEU_v3 #KNN + Doc2Vec
    
    # Getting probabilities form the fastText models    
    cOPN = 1 if model_OPN_v4.predict(text)[0][0] == '__label__1' else 0
    cCON = 1 if model_CON_v4.predict(text)[0][0] == '__label__1' else 0
    cEXT = int(model_EXT_v2.predict(df.to_numpy()[:, 1:5])[0])
    cAGR = 1 if model_AGR_v4.predict(text)[0][0] == '__label__1' else 0
    cNEU = model_NEU_v3.predict([vectors['vectors_neu']])[0]
    
    return [cOPN, cCON, cEXT, cAGR, cNEU]

def predictor_v5(df, vectors, text):
    # Predicting PROBABILITIES
    
    global model_OPN_v4 #fastText
    global model_CON_v4 #fastText
    global model_EXT_v2 #SVM + NLTK VADER Sentiment Intensity Analyzer
    global model_AGR_v4 #fastText
    global model_NEU_v3 #KNN + Doc2Vec
    
    # Getting probabilities form the fastText models
    prob_opn = round(model_OPN_v4.predict(text)[1][0], 4) * 100
    prob_con = round(model_CON_v4.predict(text)[1][0], 4) * 100
    prob_agr = round(model_AGR_v4.predict(text)[1][0], 4) * 100
    
    pOPN = prob_opn if model_OPN_v4.predict(text)[0][0] == '__label__1' else (100 - prob_opn)
    pCON = prob_con if model_OPN_v4.predict(text)[0][0] == '__label__1' else (100 - prob_opn)
    pEXT = round(model_EXT_v2.predict_proba(df.to_numpy()[:, 1:5])[0][1], 4) * 100
    pAGR = prob_agr if model_OPN_v4.predict(text)[0][0] == '__label__1' else (100 - prob_opn)
    pNEU = round(model_NEU_v3.predict_proba([vectors['vectors_neu']])[0][1], 4) * 100
    
    return [pOPN, pCON, pEXT, pAGR, pNEU]
    