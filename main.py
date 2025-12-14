import os
from src.data_loader import DataLoader
from src.visualizer import Visualizer
from src.analyzer import ImageAnalyzer

def generate_map(gpx_path, photo_dir):
    """
    GPX 파일과 사진 폴더 경로를 입력받아, Folium 지도 객체를 생성하여 반환
    """
    if not os.path.exists(gpx_path):
        print(f"Error: GPX file not found at {gpx_path}")
        return None
    
    # 1단계: GPX 데이터 로딩
    print("--- [1/3] Loading GPX Data ---")
    loader = DataLoader(gpx_path)
    gpx_df = loader.load_gpx_data()

    # 2단계: 사진 분석 및 GPX 경로에 매핑
    print("--- [2/3] Analyzing Photos ---")
    analyzer = ImageAnalyzer(photo_dir)
    photo_df = analyzer.analyze_photos(gpx_df)
    
    if not photo_df.empty:
        print(f"Photo mapping successful for {len(photo_df)} images.")
    else:
        print("No photos were mapped.")

    # 3단계: 지도 시각화
    print("--- [3/3] Generating Visualization ---")
    viz = Visualizer(gpx_df)
    folium_map = viz.create_map(photo_df=photo_df)

    return folium_map

def main():
    """
    명령줄에서 직접 실행할 때 사용되는 함수
    `data` 폴더의 기본 데이터를 사용하여 `output` 폴더에 결과 지도를 저장
    """
    # 스크립트의 실제 위치를 기준으로 경로를 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gpx_file = os.path.join(script_dir, "data", "gpx", "mock_run.gpx")
    photo_dir = os.path.join(script_dir, "data", "photos")
    output_dir = os.path.join(script_dir, "output")
    output_file = "result_map.html"

    print("--- Running in Command-Line Mode ---")
    os.makedirs(output_dir, exist_ok=True)
    
    # 지도 생성 함수 호출
    folium_map = generate_map(gpx_file, photo_dir)

    # 결과 저장
    if folium_map:
        save_path = os.path.join(output_dir, output_file)
        folium_map.save(save_path)
        print(f"Map saved successfully to: {save_path}")

if __name__ == "__main__":
    main()
