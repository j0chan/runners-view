import os
from src.data_loader import DataLoader
from src.visualizer import Visualizer
from src.analyzer import ImageAnalyzer

GPX_FILE = "data/gpx/mock_run.gpx"
PHOTO_DIR = "data/photos"
OUTPUT_DIR = "output"
OUTPUT_FILE = "result_map_v2.html"

def main():
    if not os.path.exists(GPX_FILE):
        print("데이터 파일 없음.")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. GPX 로드
    print("--- [1/3] Loading GPX Data ---")
    loader = DataLoader(GPX_FILE)
    gpx_df = loader.load_gpx_data()

    # 2. 사진 분석 및 매핑
    print("--- [2/3] Analyzing Photos ---")
    analyzer = ImageAnalyzer(PHOTO_DIR)
    photo_df = analyzer.analyze_photos(gpx_df)
    
    if not photo_df.empty:
        print(f"매핑 성공: \n{photo_df[['filename', 'color', 'lat']]}")
    else:
        print("Error: 매핑된 사진이 없습니다.")

    # 3. 시각화
    print("--- [3/3] Generating Visualization ---")
    viz = Visualizer(gpx_df)
    # photo_df를 인자로 전달
    m = viz.create_map(photo_df=photo_df)

    save_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    m.save(save_path)
    print(f"결과 저장 완료: {save_path}")

if __name__ == "__main__":
    main()