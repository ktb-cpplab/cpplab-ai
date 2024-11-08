# 이미지 변환 webp -> png
import os
from PIL import Image

# WebP 파일이 있는 폴더 경로
webp_folder = "./data/webp"
png_folder = "./data/png"

# 폴더 내 모든 WebP 파일을 PNG로 변환
cnt = 0
for filename in os.listdir(webp_folder):
    if filename.endswith(".webp"):
        # WebP 파일 열기
        webp_image = Image.open(os.path.join(webp_folder, filename))
        
        # PNG 파일로 저장
        png_filename = filename.replace(".webp", ".png")
        webp_image.save(os.path.join(png_folder, png_filename), "PNG")
        print(f'{filename} 변환 완료')
        cnt += 1
print(f'{cnt}개의 파일 변환 완료')
print('done!')