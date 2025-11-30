import gpxpy
import pandas as pd
import re
from datetime import datetime

class DataLoader:
    def __init__(self, gpx_path):
        self.gpx_path = gpx_path

    def load_gpx_data(self):
        """GPX -> DataFrame 변환""" 
        with open(self.gpx_path, 'r') as f:
            gpx = gpxpy.parse(f)

        data = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    # 기본 데이터
                    point_data = {
                        'time': point.time,
                        'lat': point.latitude,
                        'lon': point.longitude,
                        'elevation': point.elevation,
                        'heart_rate': None
                    }
                    
                    # 심박수 추출 (MVP: description 필드 파싱)
                    # 실제 환경: point.extensions 내부 XML 파싱 필요
                    if point.description and 'hr=' in point.description:
                        try:
                            # "hr=145" 형태에서 숫자 추출
                            hr_match = re.search(r'hr=(\d+)', point.description)
                            if hr_match:
                                point_data['heart_rate'] = int(hr_match.group(1))
                        except Exception as e:
                            print(f"Error parsing HR: {e}")
                            
                    data.append(point_data)
        
        df = pd.DataFrame(data)
        
        # 데이터 정제 (결측치 처리 등)
        if 'heart_rate' in df.columns:
            df['heart_rate'] = df['heart_rate'].ffill().bfill()
        
        print(f"데이터 로드 완료: {len(df)} points")
        return df