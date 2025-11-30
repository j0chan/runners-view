import folium
import branca.colormap as cm
import pandas as pd

class Visualizer:
    def __init__(self, df):
        self.df = df
        # 지도의 중심 좌표 계산
        self.center = [df['lat'].mean(), df['lon'].mean()]

    def create_map(self):
        """심박수 기반 경로가 포함된 Folium 지도 객체 생성"""
        
        # 1. 지도 초기화 (CartoDB Positron: 깔끔한 배경)
        m = folium.Map(location=self.center, zoom_start=15, tiles='CartoDB positron')

        # 2. 좌표 리스트 추출
        # folium.ColorLine은 [[lat, lon], ...] 형태와 [value, ...] 형태가 필요
        points = self.df[['lat', 'lon']].values.tolist()
        heart_rates = self.df['heart_rate'].tolist()

        # 3. 컬러맵 생성 (Blue -> Red)
        min_hr = min(heart_rates) if heart_rates else 60
        max_hr = max(heart_rates) if heart_rates else 180
        
        colormap = cm.LinearColormap(
            colors=['blue', 'yellow', 'red'], # 파랑 -> 노랑(중간) -> 빨강
            vmin=min_hr,
            vmax=max_hr,
            caption='Heart Rate (bpm)'
        )

        # 4. 경로 그리기 (ColorLine)
        # weight: 선 두께, opacity: 투명도
        folium.ColorLine(
            positions=points,
            colors=heart_rates,
            colormap=colormap,
            weight=5,
            opacity=0.8
        ).add_to(m)

        # 범례 추가
        m.add_child(colormap)
        
        return m