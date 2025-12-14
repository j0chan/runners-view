import os
import glob
import random
import pandas as pd
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

class ImageAnalyzer:
    """
    CLIP 모델을 사용하여 이미지의 장면을 분석하고,
    미리 정의된 색상 및 라벨과 매핑하는 클래스
    """
    def __init__(self, photo_dir):
        self.photo_dir = photo_dir
        
        print("Loading AI Model (OpenAI CLIP)...")
        model_id = "openai/clip-vit-large-patch14"
        self.model = CLIPModel.from_pretrained(model_id)
        self.processor = CLIPProcessor.from_pretrained(model_id, use_fast=True)
        
        # CLIP 모델이 이미지를 분류할 때 참고하는 텍스트 후보 목록.
        self.candidates = [
            "busy downtown city street with store signs, billboards, commercial buildings, and traffic", # 도시
            "gray asphalt road surface and street markings", # 도로
            "red rubber running track lanes in a stadium", # 트랙
            "brown dirt path, soil trail, and ground texture", # 흙길
            "dense green forest, woods, and many trees", # 숲
            "close-up of red and orange autumn maple leaves on a tree", # 단풍
            "green grass lawn in a park", # 잔디
            "winter landscape with white snow and snow covering the ground and trees", # 설경
            "blue water surface of a river, lake, or ocean", # 강/바다
            "empty clear blue sky with no objects, no trees, no buildings", # 하늘
            "orange and purple sunset sky over the horizon", # 노을
            "night city street with neon lights and darkness" # 야경
        ]
        
        # 분석된 장면에 따라 매핑될 색상(Hex)과 라벨 이름
        self.mapping = [
            ('#708090', 'City'),
            ('#36454F', 'Asphalt Road'),
            ('#FF0000', 'Red Track'),
            ('#A0522D', 'Dirt Trail'),
            ('#00A000', 'Green Forest'),
            ('#FF5733', 'Autumn Maple'),
            ('#7CFC00', 'Park/Grass'),
            ('#F0F8FF', 'Snowy Winter'),
            ('#0077FF', 'River/Sea/Water'),
            ('#00BFFF', 'Blue Sky'),
            ('#FF6347', 'Sunset'),
            ('#8A2BE2', 'Night/Lights')
        ]

    def predict_scene_and_color(self, img):
        """
        주어진 이미지 한 장을 CLIP 모델로 분석하여 가장 유사한 장면의 색상과 라벨을 반환
        """
        try:
            inputs = self.processor(
                text=self.candidates, 
                images=img, 
                return_tensors="pt", 
                padding=True
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probs = outputs.logits_per_image.softmax(dim=1)
            best_idx = probs.argmax().item()
            confidence = probs[0][best_idx].item()
            
            color, label = self.mapping[best_idx]
            
            return color, f"{label} ({confidence*100:.0f}%)"

        except Exception as e:
            print(f"AI Prediction Error: {e}")
            return '#808080', "Unknown"

    def analyze_photos(self, gpx_df):
        """
        사진 폴더 내의 모든 이미지를 분석하고, 각 사진을 GPX 경로의 특정 지점에 매핑.
        """
        if not self.photo_dir or not os.path.exists(self.photo_dir):
            return pd.DataFrame()

        photo_files = glob.glob(os.path.join(self.photo_dir, "*"))
        valid_exts = ['.jpg', '.jpeg', '.png', '.heic']
        photo_files = [f for f in photo_files if os.path.splitext(f)[1].lower() in valid_exts]
        
        if not photo_files:
            return pd.DataFrame()

        print(f"Analyzing {len(photo_files)} photos...")
        
        results = []
        
        # GPX 경로상에서 사진을 배치할 지점을 랜덤으로 선택.
        if len(gpx_df) < len(photo_files):
            indices = random.choices(range(len(gpx_df)), k=len(photo_files))
        else:
            indices = sorted(random.sample(range(len(gpx_df)), len(photo_files)))
        
        for i, fpath in enumerate(photo_files):
            try:
                with Image.open(fpath) as img:
                    semantic_color, scene_desc = self.predict_scene_and_color(img)
                    
                    target_idx = indices[i]
                    target_point = gpx_df.iloc[target_idx]

                    print(f"Mapping: {os.path.basename(fpath)} -> {scene_desc}")

                    results.append({
                        'filename': os.path.basename(fpath),
                        'filepath': fpath,
                        'lat': target_point['lat'],
                        'lon': target_point['lon'],
                        'color': semantic_color,
                        'scene': scene_desc,
                        'time': target_point['time']
                    })
            except Exception as e:
                print(f"Error processing {fpath}: {e}")

        return pd.DataFrame(results)