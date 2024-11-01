# upstage document parse api 활용
import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ['UPSTAGE_API_KEY']

png_folder = "./data/png"
html_folder = "./data/html"
md_folder = "./data/md"
txt_folder = "./data/txt"
print(os.getcwd())

url = "https://api.upstage.ai/v1/document-ai/document-parse"
headers = {"Authorization": f"Bearer {api_key}"}

data = {
    "output_formats": "['html', 'text', 'markdown']",
    "ocr": "auto",
    "coordinates": "false"
}

# 폴더 내 모든 png 파일을 html, md, txt로 변환
cnt = 0
for filename in os.listdir(png_folder):
    if filename.endswith(".png"):
        files = {"document": open(os.path.join(png_folder, filename), "rb")}
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        h = response.json()['content']['html']
        m = response.json()['content']['markdown']
        t = response.json()['content']['text']
        
        # html 파일 저장
        html_filename = filename.replace(".png", ".html")
        with open(os.path.join(html_folder, html_filename), "w", encoding="utf-8") as file:
            file.write(h)
        print(f'{html_filename} 변환 완료')

        # md 파일 저장
        md_filename = filename.replace(".png", ".md")
        with open(os.path.join(md_folder, md_filename), "w", encoding="utf-8") as file:
            file.write(m)  # h에 Markdown 형식의 내용이 담겨 있어야 합니다.
        print(f'{md_filename} 변환 완료')

        # 텍스트 파일로 저장
        txt_filename = filename.replace(".png", ".txt")
        with open(os.path.join(txt_folder, txt_filename), "w", encoding="utf-8") as file:
            file.write(t)  # h에 텍스트 내용이 담겨 있어야 합니다.
        print(f'{txt_filename} 변환 완료')

        cnt += 1
print(f'{cnt}개의 파일 변환 완료')
print('done!')