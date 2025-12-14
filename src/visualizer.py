import folium
import branca.colormap as cm
import pandas as pd
import base64

# Hex 코드를 Folium 아이콘 색상명으로 변환하는 기능 (현재 DivIcon 사용으로 직접 사용되지는 않음)
def hex_to_folium_color(hex_color):
    """
    분석된 Hex 색상 코드를 folium.Icon이 지원하는 기본 색상명으로 근사 변환.
    """
    color_map = {
        '#708090': 'gray',
        '#36454F': 'darkblue',
        '#DC143C': 'red',
        '#8B4513': 'darkred',
        '#006400': 'darkgreen',
        '#FF4500': 'orange',
        '#7CFC00': 'lightgreen',
        '#E0FFFF': 'lightblue',
        '#1E90FF': 'blue',
        '#87CEEB': 'lightblue',
        '#FF8C00': 'orange',
        '#483D8B': 'darkpurple',
    }
    return color_map.get(hex_color.upper(), 'gray')


class Visualizer:
    def __init__(self, df):
        self.df = df
        self.center = [df['lat'].mean(), df['lon'].mean()]

    def create_map(self, photo_df=None):
        # 지도 생성 시 기본 확대/축소 컨트롤을 비활성화
        m = folium.Map(
            location=self.center, 
            zoom_start=15, 
            tiles='CartoDB positron',
            zoom_control=False
        )

        # 경로(ColorLine)를 지도에 추가
        if 'heart_rate' in self.df.columns and not self.df['heart_rate'].dropna().empty:
            points = self.df[['lat', 'lon']].values.tolist()
            heart_rates = self.df['heart_rate'].tolist()
            vmin = self.df['heart_rate'].min()
            vmax = self.df['heart_rate'].max()
            
            spectral_colors = ['#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000']
            
            colormap = cm.LinearColormap(
                colors=spectral_colors, vmin=vmin, vmax=vmax, caption='Heart Rate (bpm)')

            folium.ColorLine(
                positions=points, colors=heart_rates, colormap=colormap, weight=4, opacity=0.7
            ).add_to(m)
            m.add_child(colormap)

        # 사진 데이터를 기반으로 마커를 추가
        if photo_df is not None and not photo_df.empty:
            for _, row in photo_df.iterrows():
                encoded = ""
                try:
                    with open(row['filepath'], 'rb') as f:
                        encoded = base64.b64encode(f.read()).decode('utf-8')
                except (FileNotFoundError, TypeError):
                    pass
                
                tooltip_html = f'<img src="data:image/jpeg;base64,{encoded}" style="width:150px;">' if encoded else "이미지"
                
                image_html = f'<img src="data:image/jpeg;base64,{encoded}" style="width:100%; max-width:250px;">' if encoded else '<p style="color:red;">Image not found</p>'
                popup_html = f"""
                <div style="font-family: sans-serif; color: black;">
                    {image_html}<br>
                    <p style="margin: 5px 0 0 0;">
                        <b>{row.get('filename', 'N/A')}</b><br>
                        Result: <b>{row.get('scene', 'N/A')}</b>
                    </p>
                </div>
                """

                # 부드러운 아우라 이펙트를 동심원으로 구현
                aura_steps = 100
                max_radius = 120
                base_opacity = 0.025

                for i in range(aura_steps, 0, -1):
                    folium.Circle(
                        location=[row['lat'], row['lon']],
                        radius=(i / aura_steps) * max_radius,
                        color=row['color'],
                        weight=0,
                        fill=True,
                        fill_color=row['color'],
                        fill_opacity=(base_opacity / aura_steps) * (aura_steps - i + 1)
                    ).add_to(m)

                # 그림자가 없는 커스텀 핀 아이콘을 생성.
                pin_html = f"""
                    <div style="
                        background-color:{row['color']};
                        width: 14px; height: 14px;
                        border-radius: 50% 50% 50% 0;
                        border: 2px solid white;
                        transform: rotate(-45deg);
                        box-shadow: none !important;
                    ">
                    </div>
                """
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    icon=folium.DivIcon(html=pin_html, icon_size=(15, 15), icon_anchor=(7, 15)),
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=tooltip_html
                ).add_to(m)

        return m