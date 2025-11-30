import os
import math
import random
import gpxpy
import gpxpy.gpx
import piexif
from datetime import datetime, timedelta
from PIL import Image

# 경로 설정
DATA_GPX_DIR = "data/gpx"
DATA_PHOTO_DIR = "data/photos"

# 폴더가 없으면 생성
os.makedirs(DATA_GPX_DIR, exist_ok=True)
os.makedirs(DATA_PHOTO_DIR, exist_ok=True)

def create_mock_data():
    print("🔄 Mock Data 생성을 시작합니다...")
    
    # --- 1. GPX 생성 ---
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    
    # 기준점 (서울 경복궁 인근)
    start_lat, start_lon = 37.5796, 126.9770
    start_time = datetime.now()
    
    # 약 20분(1200초)간의 러닝 데이터 생성
    for i in range(1200):
        # 나선형 경로 생성
        angle = i * (2 * math.pi / 600)
        radius = 0.002 + (i * 0.000002)
        delta_lat = radius * math.sin(angle)
        delta_lon = radius * math.cos(angle) * 1.1 # 위도 보정
        
        point_time = start_time + timedelta(seconds=i)
        
        # 심박수 시뮬레이션 (Sine wave + Random noise)
        # 파란색(저심박) <-> 붉은색(고심박) 테스트를 위해 변동 폭을 크게 줌
        base_hr = 140
        hr_variation = 30 * math.sin(i * 0.02)
        noise = random.randint(-2, 2)
        heart_rate = int(base_hr + hr_variation + noise)
        
        # Point 생성
        point = gpxpy.gpx.GPXTrackPoint(
            latitude=start_lat + delta_lat,
            longitude=start_lon + delta_lon,
            time=point_time
        )
        
        # 확장 데이터로 심박수 추가 (Garmin 포맷 string injection 방식)
        # gpxpy 객체 구조상 바로 넣기 까다로워 추후 파싱 단계에서 가공하거나
        # 여기서는 단순화를 위해 comment로 값을 남기거나, 별도 매핑 테이블을 만드는 게 낫지만
        # MVP 단계에서는 extensions 태그 구조를 흉내내지 않고
        # **description** 필드에 임시로 저장해서 파싱 테스트를 진행한다.
        point.description = f"hr={heart_rate}" 
        
        gpx_segment.points.append(point)

    gpx_filename = os.path.join(DATA_GPX_DIR, "mock_run.gpx")
    with open(gpx_filename, "w") as f:
        f.write(gpx.to_xml())
    print(f"GPX 생성 완료: {gpx_filename}")

    # --- 2. 사진 생성 ---
    # 테스트 케이스: [시간(초), R, G, B, 파일명]
    # 3분(180초), 10분(600초), 17분(1020초) 지점
    photo_scenarios = [
        (180, 34, 139, 34, "forest_green.jpg"),   # 숲 (Green)
        (600, 30, 144, 255, "river_blue.jpg"),    # 강 (Blue)
        (1020, 255, 69, 0, "sunset_red.jpg")      # 노을 (Red-Orange)
    ]

    for seconds, r, g, b, fname in photo_scenarios:
        # 단색 이미지 생성
        img = Image.new('RGB', (400, 300), color=(r, g, b))
        
        # Exif에 촬영 시간 주입
        photo_time = start_time + timedelta(seconds=seconds)
        time_str = photo_time.strftime("%Y:%m:%d %H:%M:%S")
        
        exif_dict = {
            "0th": {},
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: time_str.encode('utf-8')
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        
        save_path = os.path.join(DATA_PHOTO_DIR, fname)
        img.save(save_path, exif=exif_bytes)
        print(f"사진 생성 완료: {save_path} ({time_str})")

if __name__ == "__main__":
    create_mock_data()