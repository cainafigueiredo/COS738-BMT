import re
import string
from unidecode import unidecode

def textPreprocessingFunc(text):
    # Removing accents
    text = unidecode(text)

    # Strip
    text = text.strip()

    # Removing special characters, numbers and break lines
    charsToRemove = string.punctuation + "\n" + "0123456789"
    text = re.sub(r"["+charsToRemove+"]", "", text)

    # Removing multiple white spaces and tabs
    text = re.sub(" +|\t", " ", text)

    # Uppercase
    text = text.upper()

    return text