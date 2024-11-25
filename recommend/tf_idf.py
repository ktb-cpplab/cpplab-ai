from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from konlpy.tag import Mecab
import os
from dotenv import load_dotenv

load_dotenv()

path = os.getenv("MECAB_PATH")

def extract_keywords(text):
    mecab = Mecab(dicpath = path)
    nouns = mecab.nouns(text)

    return nouns

def preprocessing_keywords(nouns):
    replace_dict = {
        "Python": "파이썬",
        "AI": "인공지능",
        "벡엔드": "백엔드",
        "Java": "자바",
        "Linux": "리눅스",
        "Window": "윈도우",
    }              
    
    keywords = ""
    for noun in nouns:
        if len(noun) == 1:
            if noun == 'C' or noun == '웹':
                keywords = keywords + " " + noun        
        else:
            if noun in replace_dict:
                noun = replace_dict[noun]
            keywords = keywords + " " + noun            

    return keywords

def get_keywords(text):
    nouns = extract_keywords(text)
    ret = preprocessing_keywords(nouns)

    return ret

def space_tokenizer(text):
    return text.split()

def create_vectorizer(data):
    vectorizer = TfidfVectorizer(tokenizer=space_tokenizer, lowercase=False)
    #metrix를 이용해 사전 행렬 정보 출력
    metrix = vectorizer.fit_transform(data)  
    print(metrix)

    return vectorizer  

def get_tf_idf(vectorizer, sentence):
    keywords = get_keywords(sentence)
    vec = vectorizer.transform([keywords])
    return vec.toarray().tolist()[0]