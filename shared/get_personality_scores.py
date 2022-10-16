from personality_prediction_model.util.linkedin_profile_extract import extract_profile_summary
from personality_prediction_model.util.preprocessor import preprocessor_v1, preprocessor_v2, preprocessor_v3
from personality_prediction_model.util.predictor import predictor_v5

def get_personality_scores(profile_summary):
    df = preprocessor_v1(profile_summary)
    vectors = preprocessor_v2(profile_summary)
    text = preprocessor_v3(profile_summary)
    result = predictor_v5(df, vectors, text)
    
            
    pOPN = result[0] if(type(result[0]) == float) else result[0].item()
    pCON = result[1] if(type(result[1]) == float) else result[1].item()
    pEXT = result[2] if(type(result[2]) == float) else result[2].item()
    pAGR = result[3] if(type(result[3]) == float) else result[3].item()
    pNEU = result[4] if(type(result[4]) == float) else result[4].item()
    
    pCOMPOUND = (pOPN * pCON * pEXT * pAGR * (100.0-pNEU)) / 100000000
            
    personality_scores = { "pOPN": pOPN, "pCON": pCON, "pEXT": pEXT, "pAGR": pAGR, "pNEU": pNEU, "pCOMPOUND": pCOMPOUND }
    
    return personality_scores