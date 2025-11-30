import os
import glob
import random
import pandas as pd
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

class ImageAnalyzer:
    def __init__(self, photo_dir):
        self.photo_dir = photo_dir
        
        print("Loading AI Model (OpenAI CLIP)...")
        model_id = "openai/clip-vit-large-patch14"
        self.model = CLIPModel.from_pretrained(model_id)
        self.processor = CLIPProcessor.from_pretrained(model_id, use_fast=True)
        
        # CLIP AI에게 제공하는 힌트 문장
        self.candidates = [
            # 건축물/빌딩/도심
            "busy downtown city street with store signs, billboards, commercial buildings, and traffic",
            # 아스팔트 도로
            "gray asphalt road surface and street markings",
            # 트랙
            "red rubber running track lanes in a stadium",
            # 흙길
            "brown dirt path, soil trail, and ground texture",
            # 숲
            "dense green forest, woods, and many trees",
            # 단풍
            "close-up of red and orange autumn maple leaves on a tree",
            # 잔디
            "green grass lawn in a park",
            # 설경
            "winter landscape with white snow and snow covering the ground and trees",
            # 강/바다/물
            "blue water surface of a river, lake, or ocean",
            # 맑은 하늘
            "empty clear blue sky with no objects, no trees, no buildings",
            # 노을
            "orange and purple sunset sky over the horizon",
            # 야경
            "night city street with neon lights and darkness"
        ]
        
        # 색상 및 라벨 매핑
        self.mapping = [
            ('#708090', 'City'),            # 0
            ('#36454F', 'Asphalt Road'),    # 1
            ('#DC143C', 'Red Track'),       # 2
            ('#8B4513', 'Dirt Trail'),      # 3
            ('#006400', 'Green Forest'),    # 4
            ('#FF4500', 'Autumn Maple'),    # 5
            ('#7CFC00', 'Park/Grass'),      # 6
            ('#E0FFFF', 'Snowy Winter'),    # 7
            ('#1E90FF', 'River/Sea/Water'), # 8
            ('#87CEEB', 'Blue Sky'),        # 9
            ('#FF8C00', 'Sunset'),          # 10
            ('#483D8B', 'Night/Lights')     # 11
        ]

    def predict_scene_and_color(self, img):
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
        photo_files = glob.glob(os.path.join(self.photo_dir, "*"))
        valid_exts = ['.jpg', '.jpeg', '.png', '.heic']
        photo_files = [f for f in photo_files if os.path.splitext(f)[1].lower() in valid_exts]
        
        print(f"{len(photo_files)}장의 사진 분석 중 (Final Tuned Prompts)...")
        
        results = []
        
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

                    print(f"매핑: {os.path.basename(fpath)} → {scene_desc}")

                    results.append({
                        'filename': os.path.basename(fpath),
                        'lat': target_point['lat'],
                        'lon': target_point['lon'],
                        'color': semantic_color,
                        'scene': scene_desc,
                        'time': target_point['time']
                    })
                    
            except Exception as e:
                print(f"Error {fpath}: {e}")

        return pd.DataFrame(results)