import os
import math
import random
import gpxpy
import gpxpy.gpx
from datetime import datetime, timedelta

def create_mock_gpx():

    print("Creating mock GPX data...")
    
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    
    # --- 기본 파라미터 설정 ---
    start_lat, start_lon = 37.548, 127.042 # 시작점: 서울숲 북쪽
    RIVER_BOUNDARY_LAT = 37.541            # 경로 생성 하한선 (강)
    
    total_duration = 1500  # 총 러닝 시간 (초)
    turn_point = total_duration // 2 # 반환점 (시간 기준)

    warmup_duration = 180  # 준비운동 시간 (초)
    cooldown_start = total_duration - 180 # 정리운동 시작 시간 (초)
    
    main_heading_rad = math.radians(random.uniform(0, 180)) # 시작 방향 (북쪽)
    current_heading_rad = main_heading_rad
    m_per_deg_lat = 111000 
    m_per_deg_lon = 88800

    start_time = datetime.now()
    lat, lon = start_lat, start_lon

    for i in range(total_duration):
        # --- 1. 동적 경로 생성 ---
        base_speed_mps = random.uniform(2.0, 2.5) 
        step_m = base_speed_mps + random.uniform(-0.5, 0.5)
        
        delta_lat = (step_m / m_per_deg_lat) * math.cos(current_heading_rad)
        delta_lon = (step_m / m_per_deg_lon) * math.sin(current_heading_rad)

        if lat + delta_lat < RIVER_BOUNDARY_LAT:
            current_heading_rad = math.radians(random.uniform(45, 135))
            delta_lat = abs(delta_lat)

        if i == turn_point:
            main_heading_rad += math.pi

        noise_rad = math.radians(random.uniform(-25, 25))
        current_heading_rad += noise_rad * 0.5
        current_heading_rad += (main_heading_rad - current_heading_rad) * 0.02
        
        lat += delta_lat
        lon += delta_lon
        
        # --- 2. 3단계 심박수 시뮬레이션 ---
        heart_rate = 0
        if i < warmup_duration:
            progress = i / warmup_duration
            base_hr = 100 + 40 * progress
            heart_rate = int(base_hr + random.randint(-2, 2))
        elif i > cooldown_start:
            progress = (i - cooldown_start) / (total_duration - cooldown_start)
            base_hr = 150 - 40 * progress
            heart_rate = int(base_hr + random.randint(-2, 2))
        else:
            base_hr = 155
            interval_variation = 15 * math.sin((i - warmup_duration) * (2 * math.pi / 300))
            short_variation = 5 * math.sin(i * 0.1)
            heart_rate = int(base_hr + interval_variation + short_variation + random.randint(-4, 4))
        
        # GPX 트랙포인트 생성
        point_time = start_time + timedelta(seconds=i)
        point = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lon, time=point_time)
        point.description = f"hr={heart_rate}"
        gpx_segment.points.append(point)

    # --- 3. GPX 파일 저장 ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    DATA_GPX_DIR = os.path.join(script_dir, "data", "gpx")
    
    os.makedirs(DATA_GPX_DIR, exist_ok=True)
    gpx_filename = os.path.join(DATA_GPX_DIR, "mock_run.gpx")

    with open(gpx_filename, "w") as f:
        f.write(gpx.to_xml())
    print(f"Mock GPX file created successfully: {gpx_filename}")

if __name__ == "__main__":
    create_mock_gpx()
