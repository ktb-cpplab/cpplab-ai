import psycopg2
from embedding_text_vec import SentenceEmbedding
from tf_idf import get_tf_idf, create_vectorizer
import os
import time
#from dotenv import load_dotenv

#load_dotenv()

db_url = os.getenv("DB_URL")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

def get_vectorizer():
    try:
        connection = psycopg2.connect(
            host = db_url,
            database = db_name,
            user = db_user,
            password = db_password,
            port = db_port
        )

        cursor = connection.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT contents
            FROM courseEntity
            """
        cursor.execute(query)
        results = cursor.fetchall()

        contents = []
        for row in results:
            contents.append(row[0])

        vectorizer = create_vectorizer(contents)

        return vectorizer

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()    

def search_db(sentence):
    try:
        print("서치 디비 시작")
        start_time = time.time()

        connection = psycopg2.connect(
            host = db_url,
            database = db_name,
            user = db_user,
            password = db_password,
            port = db_port
        )

        cursor = connection.cursor()
        print("벡터라이즈")
        vectorizer = get_vectorizer()
        print("버트 변환")
        embeddingModel = SentenceEmbedding() 
        bert_vec = embeddingModel.get_mean_embedding(sentence)  
        print("미캅 변환")
        tfidf_vec = get_tf_idf(vectorizer, ' '.join(sentence))

        query = f"""
        WITH tfidf AS (
            SELECT title, url, bert_vec, tfidf_vec <-> %s::vector AS similarity
            FROM courseEntity
            ORDER BY similarity
            LIMIT 20
        )
        SELECT title, url, bert_vec <#> %s::vector AS similarity
        FROM tfidf
        ORDER BY similarity
        LIMIT 3;
        """
        cursor.execute(query, (tfidf_vec, bert_vec))
        results = cursor.fetchall()

        ret = []
        for row in results:
            ret.append(row[0])
            ret.append(row[1])

        end_time = time.time()
        print(f"소요 시간 : {end_time - start_time:.6f}초")

        return ret

    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    
    finally:
        if connection:
            cursor.close()
            connection.close()
        else:
            print("데이터 베이스 연결에 실패했습니다")

def extend_pgvector():
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
        CREATE EXTENSION IF NOT EXISTS vector;
        """
        cursor.execute(query)
        connection.commit()

    except Exception as error:
        print("pgvector 확장 중 에러 발생:", error)
    
    finally:
        if connection:
            cursor.close()
            connection.close()

def create_db():
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
            drop table IF EXISTS courseEntity;
            CREATE TABLE IF NOT EXISTS courseEntity (
            title TEXT,
            contents TEXT,
            url TEXT,
            bert_vec VECTOR(768),
            tfidf_vec VECTOR(1950)
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

def insert_db():
    try:
        connection_server = psycopg2.connect(
            host = db_url,
            database = db_name,
            user = db_user,
            password = db_password,
            port = db_port
        )

        local_db_url = os.getenv("LOCAL_DB_URL")
        local_db_name = os.getenv("LOCAL_DB_NAME")
        local_db_user = os.getenv("LOCAL_DB_USER")
        local_db_password = os.getenv("LOCAL_DB_PASSWORD")
        local_db_port = os.getenv("LOCAL_DB_PORT")

        connection_local = psycopg2.connect(
            host = local_db_url,
            database = local_db_name,
            user = local_db_user,
            password = local_db_password,
            port = local_db_port
        )

        cursor_local = connection_local.cursor()
        cursor_server = connection_server.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT title, contents, url, bert_vec, tfidf_vec
            FROM total
            """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        for row in results_local:
            title = row[0]
            contents = row[1]
            url = row[2]
            bert_vec = row[3]
            tfidf_vec = row[4]

            query = """
                    INSERT INTO courseEntity (title, contents, url, bert_vec, tfidf_vec)
                    VALUES (%s, %s, %s, %s, %s)
                    """

            data_to_insert = (title, contents, url, bert_vec, tfidf_vec)

            # 데이터 삽입 실행
            cursor_server.execute(query, data_to_insert)
            connection_server.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()    
        
        if connection_server:
            cursor_server.close()
            connection_server.close()    