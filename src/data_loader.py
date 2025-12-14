import gpxpy
import pandas as pd
import re
from datetime import datetime

class DataLoader:
    """
    GPX 파일을 읽어 Pandas DataFrame으로 변환하는 클래스.
    """
    def __init__(self, gpx_path):
        self.gpx_path = gpx_path

    def load_gpx_data(self):
        """
        GPX 파일을 파싱하여 시간, 좌표, 고도, 심박수 등의 데이터를 DataFrame으로 반환.
        """
        try:
            with open(self.gpx_path, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)
        except Exception as e:
            print(f"Error reading or parsing GPX file: {e}")
            return pd.DataFrame()

        data = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    point_data = {
                        'time': point.time,
                        'lat': point.latitude,
                        'lon': point.longitude,
                        'elevation': point.elevation,
                        'heart_rate': None
                    }
                    
                    # GPX 파일의 description 필드에서 심박수 정보를 추출. (예: "hr=145")
                    if point.description and 'hr=' in point.description:
                        try:
                            hr_match = re.search(r'hr=(\d+)', point.description)
                            if hr_match:
                                point_data['heart_rate'] = int(hr_match.group(1))
                        except Exception as e:
                            print(f"Error parsing heart rate: {e}")
                            
                    data.append(point_data)
        
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        
        # 심박수 데이터가 없는 경우, 이전/이후 데이터로 채워넣어 유효한 값으로 변환.
        if 'heart_rate' in df.columns:
            df['heart_rate'] = df['heart_rate'].ffill().bfill()
        
        print(f"Data loaded: {len(df)} points")
        return df
