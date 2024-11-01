from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time  
import random
from insertDB import insert_data_embedding0


# Chrome 옵션 설정
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # 필요 시 헤드리스 모드 활성화

# 웹드라이버 초기화
driver = webdriver.Chrome(options=options)

# 대상 URL
urls = [
        "https://www.inflearn.com/courses/it-programming?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=1",
        "https://www.inflearn.com/courses/it-programming?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=2",
        "https://www.inflearn.com/courses/game-dev-all?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=1",
        "https://www.inflearn.com/courses/game-dev-all?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=2",
        "https://www.inflearn.com/courses/data-science?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=1",
        "https://www.inflearn.com/courses/data-science?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=2",
        "https://www.inflearn.com/courses/artificial-intelligence?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=1",
        "https://www.inflearn.com/courses/artificial-intelligence?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=2",
        "https://www.inflearn.com/courses/it?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=1",
        "https://www.inflearn.com/courses/it?isDiscounted=false&types=ONLINE&sort=POPULAR&page_number=2"
        ]

for original_url in urls:
    driver.get(original_url)

    # 요소가 로드될 때까지 대기
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-y21pja')))

    # 강의들의 뭉텅이 찾기
    ul_elements = driver.find_elements(By.CLASS_NAME, 'css-y21pja')

    # 뭉텅이에서 개별 강의 주소 찾기
    hrefs = []
    for ue in ul_elements:
        li_elements = ue.find_elements(By.TAG_NAME, 'li')

        # 모든 href를 리스트에 저장
        for li in li_elements:
            a_element = li.find_element(By.TAG_NAME, 'a')
            #강의 url 추출
            href = a_element.get_attribute('href')
            hrefs.append(href)
    hrefs.pop(0)
    # 개별 강의 주소를 방문
    for idx, href in enumerate(hrefs):
        driver.get(href)
        # 5초에서 10초 사이로 대기하며 크롤링으로 인한 차단 방지
        time.sleep(random.randint(3,5))
        
        # url 주소 
        url = href
        # 강의명
        title_element = driver.find_element(By.CLASS_NAME, 'mantine-17uv248')
        title = title_element.text.strip()

        print(f"{idx+1}번째 강의명 : {title}")

        class_element = driver.find_elements(By.CLASS_NAME, 'mantine-y6qn97')
        
        learning = []
        target = []
        for preIdx, ce in enumerate(class_element):
            #[0] 이런걸 배워요, [1] 학습 대상은 누구일까요, [2] 선수 지식 필요할까요 - 스킵
            if preIdx == 2:
                break

            text_elements = ce.find_elements(By.TAG_NAME, 'p')

            if preIdx == 0:
                for idx, te in enumerate(text_elements):
                    # 이런걸 배워요 같은 대분류는 텍스트에서 제외
                    if idx == 0:
                        continue
                    text = te.text.strip()
                    learning.append(text)
            if preIdx == 1:
                for idx, te in enumerate(text_elements):
                    # 이런걸 배워요 같은 대분류는 텍스트에서 제외
                    if idx == 0:
                        continue
                    text = te.text.strip()
                    target.append(text)


        level_element = driver.find_element(By.CLASS_NAME, 'mantine-1xk1rww')
        text_elements = level_element.find_elements(By.TAG_NAME, 'strong')

        difficulty = ""
        summary = ""
        for preIdx, te in enumerate(text_elements):
            if preIdx == 0:
                text = te.text.strip()
                difficulty = difficulty + text
            else:
                text = te.text.strip()
                text = text.lstrip('[')
                text = text.rstrip(']')
                summary = summary + text

        insert_data_embedding0(title, learning, target, difficulty, summary, href)

# 드라이버 종료
driver.quit()