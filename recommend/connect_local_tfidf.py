import psycopg2
from embedding_text_vec import SentenceEmbedding
import os
from dotenv import load_dotenv
from tf_idf import extractKeywords, get_tf_idf, create_vectorizer

load_dotenv()

local_db_url = os.getenv("LOCAL_DB_URL")
local_db_name = os.getenv("LOCAL_DB_NAME")
local_db_user = os.getenv("LOCAL_DB_USER")
local_db_password = os.getenv("LOCAL_DB_PASSWORD")
local_db_port = os.getenv("LOCAL_DB_PORT")

db_url = os.getenv("DB_URL")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

def create_tfidf():
    try:
        connection = psycopg2.connect(
            host = db_url,
            database = db_name,
            user = db_user,
            password = db_password,
            port = db_port
        )
        
        cursor = connection.cursor()

        query = f"""
            CREATE TABLE IF NOT EXISTS tfidf (
            title TEXT,
            contents TEXT,
            url TEXT,
            vec VECTOR(1893)
            );
            """
        cursor.execute(query)
        connection.commit()

    except Exception as error:
        print("데이터베이스 생성 중 에러 발생:", error)
    
    finally:
        if connection:
            cursor.close()
            connection.close()

def insert_TFIDF():
    try:
        connection_local = psycopg2.connect(
            host = local_db_url,
            database = local_db_name,
            user = local_db_user,
            password = local_db_password,
            port = local_db_port
        )

        cursor_local = connection_local.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT title, learning, target, difficulty, tech, url
            FROM embedding0
            """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        for row in results_local:
            title = row[0]
            learning = row[1]
            target = row[2]
            difficulty = row[3]
            tech = row[4]
            url = row[5]

            contents = ""
            contents = contents + " " + title
            contents = contents + " " + difficulty
            for l in learning:
                contents = contents + " " + l
            for ta in target:
                contents = contents + " " + ta
            for te in tech:
                contents = contents + " " + te

            words = extractKeywords(contents)

            keywords = ""
            for word in words.split():
                if len(word) == 1:
                    if word == 'C' or word == '웹':
                        keywords = keywords + " " + word
                else:
                    keywords = keywords + " " + word


            query = """
                    INSERT INTO tfidf (title, contents, url)
                    VALUES (%s, %s, %s)
                    """            

            data_to_insert = (title, keywords, url)
            cursor_local.execute(query, data_to_insert)
            connection_local.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()    

def update_TFIDF():
    try:
        connection_local = psycopg2.connect(
            host = local_db_url,
            database = local_db_name,
            user = local_db_user,
            password = local_db_password,
            port = local_db_port
        )

        cursor_local = connection_local.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT title, contents
            FROM tfidf
            """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        titles = []
        contents = []
        for row in results_local:
            title = row[0]
            content = row[1]
            titles.append(title)
            contents.append(content)

        vectorizer = create_vectorizer(contents)
        print("vectorizer : ", vectorizer)
        print("type       : ", type(vectorizer))
        '''
        for idx in range(len(contents)):
            query = """
                    UPDATE tfidf
                    SET vec = %s
                    WHERE title = %s                
                """
            vec = get_tf_idf(vectorizer, [contents[idx]])
            
            data_to_insert = (vec, titles[idx])
            cursor_local.execute(query, data_to_insert)
            connection_local.commit()
        '''

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()    

def get_vectorizer():
    try:
        connection_local = psycopg2.connect(
            host = local_db_url,
            database = local_db_name,
            user = local_db_user,
            password = local_db_password,
            port = local_db_port
        )

        cursor_local = connection_local.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT title, contents
            FROM tfidf
            """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        titles = []
        contents = []
        for row in results_local:
            title = row[0]
            content = row[1]
            titles.append(title)
            contents.append(content)

        vectorizer = create_vectorizer(contents)
        
        return vectorizer

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()      

def search_tfidf(sentence):
    try:
        connection_local = psycopg2.connect(
            host = local_db_url,
            database = local_db_name,
            user = local_db_user,
            password = local_db_password,
            port = local_db_port
        )

        cursor = connection_local.cursor()
        vectorizer = get_vectorizer()
        vec = get_tf_idf(vectorizer, sentence)

        x = ['-', '=', '#', '+']

        for type in x:
            print(f"------------------------------ {type} ------------------------------")
            query = f"""
            SELECT title, vec <{type}> %s::vector AS similarity
            FROM tfidf
            ORDER BY similarity
            LIMIT 10;
            """
            cursor.execute(query, (vec, ))
            results = cursor.fetchall()
            
            for idx, row in enumerate(results):
                title = row[0]
                similarity = row[1]
                print(f"TOP{idx+1}")
                print("title      :", title)
                print("Similarity : ", similarity)
        
    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    
    finally:
        if connection_local:
            cursor.close()
            connection_local.close()
        else:
            print("데이터 베이스 연결에 실패했습니다")

#search_tfidf("윈도우 어플리케이션 개발 SW 개발 경험(C++,C#) Windows Application 개발 경험 Software Architecture 설계 경험 차량 제어기 검증 관련 툴 사용 경험(Vector/dSPACE/NI/ETAS 등) SW 검증 및 성능 관련 테스트 경험 협업 툴 사용 경험(Git, Jira, Jenkins 등)")