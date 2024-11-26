from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from konlpy.tag import Mecab
import os
from dotenv import load_dotenv

load_dotenv()

path = os.getenv("MECAB_PATH")

def extract_noun_keywords(text):
    mecab = Mecab(dicpath = path)
    nouns = mecab.nouns(text)

    return nouns

def extract_eng_keywords(text):
    mecab = Mecab(dicpath = path)
    tagging = mecab.pos(text)
    
    keywords = [
        "Java", "JavaScript", "AI", 
        "RAG", "GPT", "Spring", 
        "React", "SQL", "LLM", 
        "HTML", "CSS", "Python", 
        "Window", "Linux", "HTTP", 
        "Flutter", "Docker", "API", 
        "AWS", "CI", "CD"
    ]

    eng = []
    for word, pos in tagging:
        if pos == "SL":
            if word in keywords:
                eng.append(word)

    return eng

def preprocessing_keywords(nouns, engs):
    replace_dict = {
        "Python": "파이썬", 
        "AI": "인공지능", 
        "벡엔드": "백엔드",
        "Java": "자바", 
        "Linux": "리눅스", 
        "Window": "윈도우",
        "JavaScript": "자바스크립트", 
        "Spring": "스프링", 
        "React": "리액트",
    }              
    
    keywords = ""
    for noun in nouns:
        if len(noun) == 1:
            if noun == '웹':
                keywords += " " + noun
        else:
            keywords += " " + noun

    for eng in engs:
        if eng in replace_dict:
            eng = replace_dict[eng]

        keywords = keywords + " " + eng    

    return keywords

def get_keywords(text):
    nouns = extract_noun_keywords(text)
    engs = extract_eng_keywords(text)
    ret = preprocessing_keywords(nouns, engs)

    print("ret : ", ret)

    return ret

def space_tokenizer(text):
    return text.split()

def create_vectorizer(data):
    vectorizer = TfidfVectorizer(tokenizer=space_tokenizer, lowercase=False)
    metrix = vectorizer.fit_transform(data)  
    #metrix를 이용해 사전 행렬 정보 출력
    #print(metrix)

    return vectorizer  

def get_tf_idf(vectorizer, sentence):
    keywords = get_keywords(sentence)
    vec = vectorizer.transform([keywords])
    return vec.toarray().tolist()[0]