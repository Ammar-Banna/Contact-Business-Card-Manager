import re

def is_arabic(text):
    return re.search(r'[\u0600-\u06FF]', text) is not None