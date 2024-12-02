from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from konlpy.tag import Mecab
import os
from keywords import KEYWORDS, REPLACE_DICT
#from dotenv import load_dotenv

#load_dotenv()

path = os.getenv("MECAB_PATH")

def extract_noun_keywords(text):
    mecab = Mecab(dicpath = path)
    nouns = mecab.nouns(text)

    return nouns

def extract_eng_keywords(text):
    mecab = Mecab(dicpath = path)
    tagging = mecab.pos(text.lower())

    eng = []
    for word, pos in tagging:
        if pos == "SL":
            if word in KEYWORDS:
                eng.append(word)

    return eng

def preprocessing_keywords(nouns, engs):
    keywords = ""
    for noun in nouns:
        if len(noun) == 1:
            if noun in ['웹', '깃']:
                keywords += " " + noun
        else:
            keywords += " " + noun

    for eng in engs:
        if eng in REPLACE_DICT:
            eng = REPLACE_DICT[eng]

        keywords = keywords + " " + eng    

    return keywords

def get_keywords(text):
    nouns = extract_noun_keywords(text)
    engs = extract_eng_keywords(text)
    ret = preprocessing_keywords(nouns, engs)

    return ret

def space_tokenizer(text):
    return text.split()

def create_vectorizer(data):
    vectorizer = TfidfVectorizer(tokenizer=space_tokenizer, lowercase=False)
    metrix = vectorizer.fit_transform(data)  
    #print(' '.join(vectorizer.get_feature_names_out()))
    #print(metrix)

    return vectorizer  

def get_tf_idf(vectorizer, sentence):
    keywords = get_keywords(sentence)
    vec = vectorizer.transform([keywords])
    return vec.toarray().tolist()[0]