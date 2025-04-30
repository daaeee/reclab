import pandas as pd
import numpy as np
from tqdm import tqdm, trange

import pandas as pd    
data = pd.read_json(path_or_buf="kinopoisk.jsonl", lines=True)

# Pre-processing

import string
def remove_punctuation(text):
    return "".join([ch if ch not in string.punctuation else ' ' for ch in text])

def remove_numbers(text):
    return ''.join([i if not i.isdigit() else ' ' for i in text])

import re
def remove_multiple_spaces(text):
	return re.sub(r'\s+', ' ', text, flags=re.I)

import pymystem3
from nltk.stem import *
from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation
mystem = Mystem() 

russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['…', '«', '»', '...'])
def lemmatize_text(text):
    tokens = mystem.lemmatize(text.lower())
    tokens = [token for token in tokens if token not in russian_stopwords and token != " "]
    text = " ".join(tokens)
    return text

prep_text = [remove_multiple_spaces(remove_numbers(remove_punctuation(text.lower()))) for text in tqdm(data['content'])]
data['text_prep'] = prep_text



# Limmatize 

lemm_texts_list = []
for text in tqdm(data['text_prep']):
    #print(text)
    try:
        text_lem = mystem.lemmatize(text)
        tokens = [token for token in text_lem if token != ' ' and token not in russian_stopwords]
        text = " ".join(tokens)
        lemm_texts_list.append(text)
    except Exception as e:
        print(e)
    
data['text_lemm'] = lemm_texts_list


# Stemming

from nltk.stem.snowball import SnowballStemmer 
stemmer = SnowballStemmer("russian") 

russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['…', '«', '»', '...', 'т.д.', 'т', 'д'])

import nltk
from nltk import word_tokenize
nltk.download('punkt')

def remove_stop_words(text):
    tokens = word_tokenize(text) 
    tokens = [token for token in tokens if token not in russian_stopwords and token != ' ']
    return " ".join(tokens)


sw_texts_list = []
for text in tqdm(data['text_prep']):
    tokens = word_tokenize(text)    
    tokens = [token for token in tokens if token not in russian_stopwords and token != ' ']
    text = " ".join(tokens)
    sw_texts_list.append(text)

data['text_sw'] = sw_texts_list

from nltk import word_tokenize

stemmed_texts_list = []
for text in tqdm(data['text_sw']):
    tokens = word_tokenize(text)    
    stemmed_tokens = [stemmer.stem(token) for token in tokens if token not in russian_stopwords]
    text = " ".join(stemmed_tokens)
    stemmed_texts_list.append(text)

data['text_stem'] = stemmed_texts_list
data.to_csv('full.csv')