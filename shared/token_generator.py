import hashlib

# Generating SHA1 hash token based on user details
def generate_token(user_dict):
    user_str = str(user_dict)
    user_byte = bytes(user_str, encoding='utf-8')
    m = hashlib.sha1()
    m.update(user_byte)
    token = m.hexdigest()
    
    return token
    