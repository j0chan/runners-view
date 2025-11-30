import folium
import branca.colormap as cm
import pandas as pd

class Visualizer:
    def __init__(self, df):
        self.df = df
        self.center = [df['lat'].mean(), df['lon'].mean()]

    def create_map(self, photo_df=None):
        m = folium.Map(location=self.center, zoom_start=15, tiles='CartoDB positron')

        # 1. 경로 그리기 (심박수 데이터)
        points = self.df[['lat', 'lon']].values.tolist()
        if 'heart_rate' in self.df.columns:
            heart_rates = self.df['heart_rate'].tolist()
            vmin = min(heart_rates) if heart_rates else 60
            vmax = max(heart_rates) if heart_rates else 180
        else:
            heart_rates = [140] * len(points)
            vmin, vmax = 60, 180
        
        # 색상: Cyan -> Magenta (네온 스타일)
        colormap = cm.LinearColormap(
            colors=["#04FF00", "#F7E308", "#FFA500", "#FF0000"],
            vmin=vmin,
            vmax=vmax,
            caption='Heart Rate (bpm)'
        )

        folium.ColorLine(
            positions=points,
            colors=heart_rates,
            colormap=colormap,
            weight=4,
            opacity=0.7
        ).add_to(m)
        m.add_child(colormap)

        # 2. 사진 마커 추가
        if photo_df is not None and not photo_df.empty:
            for _, row in photo_df.iterrows():
                popup_html = f"""
                <div style="font-family: sans-serif; color: black; min-width: 150px;">
                    <b>{row['filename']}</b><br>
                    Result: <b>{row['scene']}</b>
                </div>
                """
                
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=8,                # 고정 크기
                    color=row['color'],      # 분류된 색상
                    weight=2,
                    fill=True,
                    fill_color=row['color'],
                    fill_opacity=1.0,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{row['scene']}"
                ).add_to(m)

        return m