# project READ.ME

### Detail Role

- simon.kim(김형민)
    - AI
    - 채용공고 데이터 수집, 가공 및 적재
    - RAG 기반 프로젝트 생성 및 재생성 기능 개발
    - BE-AI 부하테스트

### Languages

Python

### Technologies

Python, Langchain, Postgresql, Redis, FastAPI

## 🎁 결과물

<details>
    <summary>데이터 처리 파이프 라인</summary>
    <div markdown="1">
    
<img width="964" alt="데이터 처리 파이프 라인" src="https://github.com/user-attachments/assets/ce7cfcfe-2012-4ad3-9a43-7e4b58791210"/>
    
- 데이터 수집
    
    자소설닷컴, IT 직무(24.01 ~ 24.12)
    
- 데이터 가공(1)
    
    수집한 채용공고 데이터의 특징
    
    1. 이미지 파일(WebP) → OCR 필요
    2. 표 형식 → 구조 유지 필요
    
    → Upstage API(Document Parse): 이미지를 구조가 있는 텍스트(html, json, md)로 변환
    
- 데이터 가공(2)
    1. 채용공고마다 사용할 정보를 통일하기 위해 분류 및 태깅 작업 필요
    2. 사용할 정보는 직무명, 담당업무, 필요역량, 우대사항으로 정의
    
    → OpenAI API를 활용하여 분류 및 태깅 작업 자동화
    
- DB 적재
    1. 담당업무, 필요역량, 우대사항을 결합하여 임베딩(Open AI)
    2. PostgreSQL의 pgvector extension을 사용하여 적재
        
</details>
  
  
  
<details>
    <summary>RAG 활용 프로젝트 생성</summary>
    <div markdown="1">
<img width="843" alt="%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2024-12-23_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_7 19 47" src="https://github.com/user-attachments/assets/d946d90e-d0b9-4971-b679-8dfc42a8f599" />

- 프로젝트 생성
    - Retrieve
        1. 사용자 프로필 데이터를 파싱하여 검색 쿼리 생성
        2. 사용자 프로필과 유사한 20개의 채용공고 검색
    - Augment
        
        1. 사용자 희망 직무에 맞는 채용공고만 선택하여 요약
        
    - Generate
        
        1. 사용자 프로필과 요약된 채용공고를 활용하여 프로젝트 주제 및 주제 후보 생성
        
        2. 생성된 주제를 바탕으로 프로젝트 생성
        

- 프로젝트 재생성
    
    검색과 증강 과정을 생략하고 이전에 처리한 데이터를 다시 사용하는 것이 효율적
    
    기존에 추천 받은 프로젝트와 겹치지 않는 프로젝트를 추천해야 함
    
    → 세션의 필요성
    
    - Generate
        1. 사용자 프로필과 요약된 채용공고를 활용하여 프로젝트 주제 및 주제 후보 생성
        단, 추천 받았지만 선택하지 않은 주제를 같이 전달하여 추후 추천 프로젝트가 겹치지 않게 생성
        2. 선택한 주제를 바탕으로 프로젝트 생성
</details>


## 💎 왜 이 기술을 사용했는가?
<details>
    <summary>RAG</summary>
    <div markdown="1">
        
최신 채용공고를 활용하여 사용자 경험을 높일 수 있습니다. 그러나 새롭게 올라오는 채용공고를 반영하기 위해 매번 모델을 새로 만들고 학습시키는 건 효율적이지 않습니다. 대신, LLM에게 사용자에게 적합한 채용공고를 프롬프트에 컨텍스트로 전달하면 효율적으로 해당 지식을 반영하여 프로젝트를 생성할 수 있습니다.  

새로운 채용공고가 올라올 때마다 데이터를 처리하여 DB에 적재하면, 실시간으로 채용공고를 서비스에 반영할 수 있다는 장점이 있습니다.

</details>

<details>
    <summary>Langchain</summary>
    <div markdown="1">
    
저희 프로젝트는 직접 모델을 개발하고 배포하기엔 시간과 리소스 문제가 있기 때문에, 상용 LLM의 API를 사용하여 개발하였습니다. Langchain은 LLM 활용 애플리케이션을 개발하는데 유용한 툴을 미리 구현하여 제공하기 때문에, 개발 생산성을 높일 수 있었습니다.

Langsmith를 통해 LLM chain의 추적 및 관리를 용이하게 하였습니다. 또한, 원격 저장소를 통해 프롬프트를 관리하고, LLM chain을 업데이트하는 API를 개발하여 서버를 다시 배포하지 않아도 변경된 프롬프트를 반영할 수 있게 하였습니다.
</details>
    

<details>
    <summary>Redis</summary>
    <div markdown="1">
    
TTL (Time-To-Live) 관리: 사용자 세션 데이터의 유효기간을 설정하여, 오래된 세션 데이터를 자동으로 삭제하고 리소스 관리 효율성을 높이기 위함.

세션 관리: 프로젝트 재생성 과정에서 사용자의 이전 선택 데이터와 상태 정보를 신속히 조회하고 저장할 수 있도록 Redis를 활용.

빠른 속도: 인메모리 데이터 저장소로서 읽기/쓰기 속도가 빠르기 때문에, 실시간으로 사용자 요청에 응답하고 데이터를 처리할 수 있음.

캐싱: 반복적으로 조회되는 데이터를 캐싱하여 데이터베이스 요청 부하를 줄이고 전체 성능을 향상.

확장성: Redis는 수평적 확장이 가능하므로, 대규모 트래픽 상황에서도 안정적으로 데이터를 관리 가능.
</details>

## 🚀 리팩토링 & 성능 개선

<details>
    <summary>프롬프트 세분화</summary>
    <div markdown="1">

- 초기
    
    하나의 프롬프트에 지시사항, 채용 공고, 사용자 프로필을 전부 포함하여 답변 생성
        
    → 프롬프트가 길어지고 지시사항이 복잡해져서, 지시사항을 제대로 이행하지 못하는 문제
    
    프로젝트 생성 프롬프트: https://smith.langchain.com/hub/checkerboard/gen_prompt
    
- 최종
    
    주요 목적(채용공고 요약, 주제 생성, 태스크 생성)에 맞게 프롬프트를 분할하여 하나의 프롬프트에서 하나의 작업에 집중
    
    → 더 구체적인 답변 생성 가능
    
    채용 공고 요약 프롬프트: https://smith.langchain.com/hub/checkerboard/gen_summary
    
    주제 생성 프롬프트: https://smith.langchain.com/hub/checkerboard/gen_subject
    
    태스크 생성 프롬프트: https://smith.langchain.com/hub/checkerboard/gen_tasks
</details>
        

<details>
    <summary>성능 테스트(동기/비동기)</summary>
    <div markdown="1">    
    <img width="1271" alt="%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2024-12-23_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_7 28 06" src="https://github.com/user-attachments/assets/8e2bd765-652a-475a-b9ec-a4d08296a0d3" />


- 테스트 환경
    - Agent Spec: t3a.large / 8gb
    - OpenAI API 호출 비용 문제로 모든 호출을 sleep으로 대체
    - sleep 시간은 평균이 40, 표준편차가 10인 정규분포에서 샘플링(20초~60초 사이일 확률 95%)
    - 평균 응답 시간을 기준으로 다양한 응답 시간을 반영하고자 함

- 동기
    
    가상 사용자 100명에서 45%의 낮은 성공률
    
- 비동기
    
    한계 지점: 가상 사용자 2000명
</details>
