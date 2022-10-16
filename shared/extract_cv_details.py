from pdfminer.high_level import extract_text
import pybase64
import re
import datetime

def extract_cv_details(path, firstName, lastName, language, base64String):
    fileName = firstName.lower() + "_" + lastName.lower() + "_" + language.lower() + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"
    with open(path + fileName , "wb") as f:
        f.write(pybase64.b64decode(base64String.split(",")[1:2][0]))

    detail_str = extract_text(path + fileName)
    cv_details = {}
    langArr = []
    regex = r'\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b'
    regexPhone = r'(?:\+\d{2})?\d{3,4}\D?\d{3}\D?\d{3}'
    
    cv_details['fileName'] = fileName
    links = re.findall(regex, detail_str)
    phone = re.findall(regexPhone, detail_str)
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', detail_str)
    if (match != None):
        cv_details['email'] = match.group(0)
    
    for value in links:
        if (value != 'gmail.com'):
            langArr.append(value)
        if 'linkedin' in value:
            linkedin = value
            url = linkedin
            url=url.replace('http://','')
            url=url.replace('https://','')
            url=url.replace('www.','')
            url=url.replace('linkedin.com/in/','')
            cv_details['linkedin_username'] = url
        if 'github' in value:
            github = value
            url = github
            url=url.replace('http://','')
            url=url.replace('https://','')
            url=url.replace('www.','')
            url=url.replace('github.com/','')
            cv_details['github_username'] = url
    return cv_details