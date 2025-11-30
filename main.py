import os
from src.data_loader import DataLoader
from src.visualizer import Visualizer

# 설정
GPX_FILE = "data/gpx/mock_run.gpx"
OUTPUT_DIR = "output"
OUTPUT_FILE = "result_map.html"

def main():
    # 0. 사전 작업
    if not os.path.exists(GPX_FILE):
        print(f"오류: 데이터 파일 없음.")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. 데이터 로드
    print("running data loader...")
    loader = DataLoader(GPX_FILE)
    df = loader.load_gpx_data()

    # 2. 시각화 (지도 생성)
    print("generating map...")
    viz = Visualizer(df)
    m = viz.create_map()

    # 3. 저장
    save_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    m.save(save_path)
    print(f"지도 저장 완료: {save_path}")

if __name__ == "__main__":
    main()