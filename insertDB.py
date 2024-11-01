import psycopg2
from embedding import get_embedding, get_embedding_mean
from embedding2 import get_embedding2, get_embedding3, get_embedding4

def insert_vec():
    try:
        # 데이터베이스에 연결
        connection = psycopg2.connect(
            host="localhost",       # 데이터베이스 호스트 주소
            database="localTest",  # 데이터베이스 이름
            user="postgres",    # 사용자 이름
            password="tlatkd22@@" # 비밀번호
        )

        cursor = connection.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT title, learning, target, difficulty, tech
            FROM embedding0
            """
        cursor.execute(query)

        results = cursor.fetchall()

        for row in results:
            title = row[0]
            learning = row[1]
            target = row[2]
            difficulty = row[3]
            tech = row[4]

            contents = []
            contents.append(title)
            contents.append(difficulty)
            for l in learning:
                contents.append(l)
            for ta in target:
                contents.append(ta)
            for te in tech:
                contents.append(te)
        
            vec1 = get_embedding_mean(contents) 

            insert_query = """
                    INSERT INTO embedding3 (title, contents, vec1)
                    VALUES (%s, %s, %s)
                    """

            data_to_insert = (title, contents, vec1)

            # 데이터 삽입 실행
            cursor.execute(insert_query, data_to_insert)
            connection.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

def modify_summary():
    try:
        # 데이터베이스에 연결
        connection = psycopg2.connect(
            host="localhost",       # 데이터베이스 호스트 주소
            database="localTest",  # 데이터베이스 이름
            user="postgres",    # 사용자 이름
            password="psw" # 비밀번호
        )

        cursor = connection.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT title, summary
            FROM embedding0
            """
        cursor.execute(query)

        results = cursor.fetchall()

        for row in results:
            summary = row[1]
            title = row[0]

            query = f"""
                UPDATE embedding3
                SET summary = %s
                WHERE title = %s
                """
            cursor.execute(query, (summary, title))
            connection.commit()

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
modify_summary()


def insert_data(title, url, contents, summary):
    try:
        # 데이터베이스에 연결
        connection = psycopg2.connect(
            host="localhost",       # 데이터베이스 호스트 주소
            database="localTest",  # 데이터베이스 이름
            user="postgres",    # 사용자 이름
            password="tlatkd22@@" # 비밀번호
        )

        cursor = connection.cursor()

        # 테이블에 삽입할 데이터
        insert_query = """
        INSERT INTO embedding2 (title, summary, contents, url, vec)
        VALUES (%s, %s, %s, %s, %s)
        """

        vec = get_embedding(contents)
        data_to_insert = (title, summary, contents, url, vec)

        # 데이터 삽입 실행
        cursor.execute(insert_query, data_to_insert)

        # 변경 사항을 커밋
        connection.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            
def insert_data_embedding0(title, learning, target, difficulty, summary, url):
    try:
        # 데이터베이스에 연결
        connection = psycopg2.connect(
            host="localhost",       # 데이터베이스 호스트 주소
            database="localTest",  # 데이터베이스 이름
            user="postgres",    # 사용자 이름
            password="tlatkd22@@" # 비밀번호
        )

        cursor = connection.cursor()

        # 테이블에 삽입할 데이터
        insert_query = """
        INSERT INTO embedding0 (title, learning, target, difficulty, summary, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        data_to_insert = (title, learning, target, difficulty, summary, url)

        # 데이터 삽입 실행
        cursor.execute(insert_query, data_to_insert)

        # 변경 사항을 커밋
        connection.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

def insert_data_embedding4(title, learning, target, difficulty, summary, url):
    try:
        # 데이터베이스에 연결
        connection = psycopg2.connect(
            host="localhost",       # 데이터베이스 호스트 주소
            database="localTest",  # 데이터베이스 이름
            user="postgres",    # 사용자 이름
            password="tlatkd22@@" # 비밀번호
        )

        cursor = connection.cursor()

        # 테이블에 삽입할 데이터
        insert_query = """
        INSERT INTO embedding2 (title, learning, target, difficulty, summary, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        data_to_insert = (title, learning, target, difficulty, summary, url)

        # 데이터 삽입 실행
        cursor.execute(insert_query, data_to_insert)

        # 변경 사항을 커밋
        connection.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()