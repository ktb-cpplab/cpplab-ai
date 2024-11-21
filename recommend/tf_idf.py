from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from konlpy.tag import Mecab
import os
from dotenv import load_dotenv

load_dotenv()

path = os.getenv("MECAB_PATH")

def extractKeywords(text):
    mecab = Mecab(dicpath = path)
    nouns = mecab.nouns(text)
    print("nouns : ", nouns)
    ret = ' '.join(nouns)

    return ret    

def mecab_tokenizer(text):
    mecab = Mecab(dicpath=path)
    ret = mecab.nouns(text)
    print(ret)

    return ret

def space_tokenizer(text):
    return text.split()

def create_vectorizer(data):
    vectorizer = TfidfVectorizer(tokenizer=space_tokenizer, lowercase=False)
    vectorizer.fit_transform(data)  
    return vectorizer  

def get_tf_idf(vectorizer, sentence):
    keywords = extractKeywords(sentence)
    vec = vectorizer.transform([keywords])
    print("keywords : ", keywords)
    return vec.toarray().tolist()[0]