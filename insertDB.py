import psycopg2
from embedding import get_embedding

def insert_data(title, url, contents):
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
        INSERT INTO embeddings (title, contents, url, vec)
        VALUES (%s, %s, %s, %s)
        """

        vec = get_embedding(contents)
        data_to_insert = (title, contents, url, vec)

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
            print("데이터베이스 연결이 종료되었습니다.")
