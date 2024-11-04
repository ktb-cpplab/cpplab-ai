# png2txt.py
import requests
import os

api_key = os.getenv('UPSTAGE_API_KEY')

png_folder = "./data/png"
html_folder = "./data/html"
md_folder = "./data/md"
txt_folder = "./data/txt"

url = "https://api.upstage.ai/v1/document-ai/document-parse"
headers = {"Authorization": f"Bearer {api_key}"}

data = {
    "output_formats": "['html', 'text', 'markdown']",
    "ocr": "auto",
    "coordinates": "false"
}

cnt = 0
for filename in os.listdir(png_folder):
    if filename.endswith(".png"):
        files = {"document": open(os.path.join(png_folder, filename), "rb")}
        response = requests.post(url, headers=headers, files=files, data=data)
        
        h = response.json()['content']['html']
        m = response.json()['content']['markdown']
        t = response.json()['content']['text']
        
        html_filename = filename.replace(".png", ".html")
        with open(os.path.join(html_folder, html_filename), "w", encoding="utf-8") as file:
            file.write(h)
        print(f'{html_filename} 변환 완료')

        md_filename = filename.replace(".png", ".md")
        with open(os.path.join(md_folder, md_filename), "w", encoding="utf-8") as file:
            file.write(m)
        print(f'{md_filename} 변환 완료')

        txt_filename = filename.replace(".png", ".txt")
        with open(os.path.join(txt_folder, txt_filename), "w", encoding="utf-8") as file:
            file.write(t)
        print(f'{txt_filename} 변환 완료')

        cnt += 1
print(f'{cnt}개의 파일 변환 완료')
print('done!')