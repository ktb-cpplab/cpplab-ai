import psycopg2
import os
import time
import ast
import numpy as np
from dotenv import load_dotenv
from tf_idf import get_keywords, get_tf_idf, create_vectorizer
from embedding_text_vec import SentenceEmbedding
from sklearn.decomposition import TruncatedSVD

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
            SELECT contents
            FROM tfidf
            """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        contents = []
        for row in results_local:
            content = row[0]
            contents.append(content)

        vectorizer = create_vectorizer(contents)
        
        return vectorizer

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()    

def get_tsvd():
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
            SELECT tfidf_vec
            FROM total
            """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        matrix = []
        for row in results_local:
            tfidf_vec = ast.literal_eval(row[0])
            matrix.append(tfidf_vec)

        tsvd = TruncatedSVD(n_components = 10)
        tsvd.fit(matrix)
        
        return tsvd

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()    

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
            drop table IF EXISTS tfidf;
            CREATE TABLE IF NOT EXISTS tfidf (
            title TEXT,
            contents TEXT,
            url TEXT,
            tfidf_vec VECTOR(1900)
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

def insert_tfidf():
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

            keywords = get_keywords(contents)     

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

def update_tfidf():
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

        for idx in range(len(contents)):
            query = """
                    UPDATE tfidf
                    SET tfidf_vec = %s
                    WHERE title = %s                
                """
            
            vec = get_tf_idf(vectorizer, contents[idx])
            data_to_insert = (vec, titles[idx])
            cursor_local.execute(query, data_to_insert)
            connection_local.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()      

def search_tfidf(sentence):
    try:
        start_time = time.time()

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

        query = f"""
        SELECT title, vec <-> %s::vector AS similarity
        FROM tfidf
        ORDER BY similarity
        LIMIT 20;
        """
        cursor.execute(query, (vec, ))
        results = cursor.fetchall()
        
        for idx, row in enumerate(results):
            title = row[0]
            similarity = row[1]
            print(f"TOP{idx+1}")
            print("title      :", title)
            print("Similarity : ", similarity)
        
        end_time = time.time()
        print(f"소요 시간 : {end_time - start_time:.6f}초")

    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    
    finally:
        if connection_local:
            cursor.close()
            connection_local.close()
        else:
            print("데이터 베이스 연결에 실패했습니다")

def insert_total():
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

        vectorizer = get_vectorizer()

        for row in results_local:
            title = row[0]
            learning = row[1]
            target = row[2]
            difficulty = row[3]
            tech = row[4]
            url = row[5]

            contents = []
            contents.append(title)
            contents.append(difficulty)
            for l in learning:
                contents.append(l)
            for ta in target:
                contents.append(ta)
            for te in tech:
                contents.append(te)

            embeddingModel = SentenceEmbedding() 
            bert_vec = embeddingModel.get_mean_embedding(contents)
            keywords = get_keywords(' '.join(contents))
            tfidf_vec = get_tf_idf(vectorizer, keywords) 

            query = """
                    INSERT INTO total (title, contents, url, bert_vec, tfidf_vec)
                    VALUES (%s, %s, %s, %s, %s)
                    """            
            
            data_to_insert = (title, keywords, url, bert_vec, tfidf_vec)
            cursor_local.execute(query, data_to_insert)
            connection_local.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()     

def search_svd(sentence):
    try:
        start_time = time.time()

        connection_local = psycopg2.connect(
            host = local_db_url,
            database = local_db_name,
            user = local_db_user,
            password = local_db_password,
            port = local_db_port
        )

        cursor = connection_local.cursor()
        vectorizer = get_vectorizer()
        tfidf_vec = get_tf_idf(vectorizer, sentence)

        matrix = np.array(tfidf_vec).reshape(1,-1)

        tsvd = get_tsvd()
        data_tsvd = tsvd.transform(matrix).tolist()[0]


        embeddingModel = SentenceEmbedding() 
        bert_vec = embeddingModel.get_mean_embedding([sentence])

        query = f"""
        WITH tfidf AS (
            SELECT title, bert_vec, tfidf_vec <-> %s::vector AS similarity
            FROM svd
            ORDER BY similarity
            LIMIT 20
        )
        SELECT title, bert_vec <#> %s::vector AS similarity
        FROM tfidf
        ORDER BY similarity
        LIMIT 3;
        """
        cursor.execute(query, (data_tsvd, bert_vec))
        results = cursor.fetchall()
        
        for idx, row in enumerate(results):
            title = row[0]
            similarity = row[1]
            print(f"TOP{idx+1}")
            print("title      :", title)
            print("Similarity : ", similarity)

        end_time = time.time()
        print(f"search svd 소요 시간 : {end_time - start_time:.6f}초")

    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    
    finally:
        if connection_local:
            cursor.close()
            connection_local.close()
        else:
            print("데이터 베이스 연결에 실패했습니다")

def search_total(sentence):
    try:
        start_time = time.time()

        connection_local = psycopg2.connect(
            host = local_db_url,
            database = local_db_name,
            user = local_db_user,
            password = local_db_password,
            port = local_db_port
        )

        cursor = connection_local.cursor()
        vectorizer = get_vectorizer()
        tfidf_vec = get_tf_idf(vectorizer, sentence)
        embeddingModel = SentenceEmbedding() 
        bert_vec = embeddingModel.get_mean_embedding([sentence])

        query = f"""
        WITH tfidf AS (
            SELECT title, bert_vec, tfidf_vec <-> %s::vector AS similarity
            FROM total
            ORDER BY similarity
            LIMIT 20
        )
        SELECT title, bert_vec <#> %s::vector AS similarity
        FROM tfidf
        ORDER BY similarity
        LIMIT 3;
        """
        cursor.execute(query, (tfidf_vec, bert_vec))
        results = cursor.fetchall()
        
        for idx, row in enumerate(results):
            title = row[0]
            similarity = row[1]
            print(f"TOP{idx+1}")
            print("title      :", title)
            print("Similarity : ", similarity)

        end_time = time.time()
        print(f"search total 소요 시간 : {end_time - start_time:.6f}초")

    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    
    finally:
        if connection_local:
            cursor.close()
            connection_local.close()
        else:
            print("데이터 베이스 연결에 실패했습니다")

search_total("AI 개발자 초급 Python TensorFlow Pandas Numpy AI 기반 교통 혼잡 예측 시스템 개발 이 프로젝트는 AI 기술을 활용하여 교통 혼잡을 예측하는 시스템을 개발합니다. 다양한 데이터 소스를 사용하여 정확한 예측 모델을 구축하고, 사용자에게 유용한 정보를 제공합니다.")
search_total("백엔드 개발자 중급 Redis Java Spring Boot MySQL 중급 비즈니스 로직 개발 프로젝트 본 프로젝트는 고급 비즈니스 로직을 구현하기 위해 Redis를 활용한 데이터 캐싱 및 API 설계를 포함합니다. 복잡한 데이터 흐름을 효율적으로 처리하고, 비즈니스 요구 사항을 충족시키는 시스템을 구축합니다.")
search_total("윈도우 어플리케이션 개발자 hadoop recoil redux 중급 웹 애플리케이션 성능 최적화 프로젝트 이 프로젝트는 웹 애플리케이션의 성능을 개선하기 위해 데이터 처리 및 상태 관리를 최적화하는 것을 목표로 합니다. Hadoop을 활용한 데이터 처리, Recoil 및 Redux를 통한 상태 관리 최적화 등을 통해 사용자 경험을 향상시킵니다.")


def truncate_data():
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
            SELECT title, contents, url, bert_vec, tfidf_vec
            FROM total
            """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        matrix = []
        for row in results_local:
            tfidf_vec = ast.literal_eval(row[4])
            matrix.append(tfidf_vec)

        matrix = np.array(matrix)
        tsvd = TruncatedSVD(n_components = 10)
        tsvd.fit(matrix)
        data_tsvd = tsvd.transform(matrix)

        for idx,row in enumerate(results_local):
            title = row[0]
            contents = row[1]
            url = row[2]
            bert_vec = row[3]
            truncated_vec = data_tsvd[idx].tolist()

            query = """
                    INSERT INTO svd (title, contents, url, bert_vec, tfidf_vec)
                    VALUES (%s, %s, %s, %s, %s)
                    """            
            
            data_to_insert = (title, contents, url, bert_vec, truncated_vec)
            cursor_local.execute(query, data_to_insert)
            connection_local.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()     