import json 
from bson.json_util import dumps
import numpy as np

def get_ranked_list(cursor, skill_priority, personality_priority, language, no_of_candidates):
    
    serialized_results = dumps(cursor)
    r = serialized_results.replace("'",'')
    data = json.loads(r)
    
    tsrm_priority = 0.7
    tsuam_priority = 0.3
    x1 = skill_priority * 100
    y1 = personality_priority * 100
    
    for candidate in data:
        print(candidate)
        if (candidate['tsrmScore'] is not None and language in candidate['tsrmScore']):
            x_tsrm = tsrm_priority * float(candidate['tsrmScore'][language])
        else:
            x_tsrm = 0
        if (candidate['tsuamScore'] is not None and language in candidate['tsuamScore']):
            x_tsuam = tsuam_priority * float(candidate['tsuamScore'][language])
        else:
            x_tsuam = 0
        sCompoundScore = x_tsrm + x_tsuam
        finalSkillScore = skill_priority * sCompoundScore
        if ('ppmScore' in candidate):
            finalPersonalityScore = personality_priority * float(candidate['ppmScore']['pCOMPOUND'])
        else:
            finalPersonalityScore = 0
            
        x2 =  finalSkillScore
        y2 = finalPersonalityScore
    
        eDistance = np.sqrt(np.square(x1 - x2) + np.square(y1 - y2))
        candidate[language] = {}
        candidate[language]['eDistance'] = eDistance
    
    data.sort(key=lambda x: x[language]["eDistance"])
    data = data[0:no_of_candidates]
    
    return data;