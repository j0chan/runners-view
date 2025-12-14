import os
import uuid
from flask import Flask, request, render_template, render_template_string
from werkzeug.utils import secure_filename
from main import generate_map

app = Flask(__name__)

# --- 경로 설정 ---
project_root = os.path.dirname(os.path.abspath(__file__))
GPX_SAVE_DIR = os.path.join(project_root, 'data', 'gpx')
TEMP_UPLOAD_DIR = os.path.join(project_root, 'data', 'uploads') # 사진 임시 업로드 폴더

# 서버 시작 시 폴더 생성
os.makedirs(GPX_SAVE_DIR, exist_ok=True)
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_and_display():
    """
    GET: 파일 업로드 페이지 렌더링.
    POST: 업로드된 GPX와 사진 파일 처리 후 지도 시각화 결과 반환.
    """
    if request.method == 'POST':
        if 'gpx_file' not in request.files:
            return "GPX 파일 없음", 400
        
        gpx_file = request.files['gpx_file']
        photo_files = request.files.getlist('photo_files')

        if gpx_file.filename == '':
            return "GPX 파일이 선택되지 않음", 400

        # 1. GPX 파일 저장
        gpx_filename = "mock_run.gpx"
        gpx_path = os.path.join(GPX_SAVE_DIR, gpx_filename)
        gpx_file.save(gpx_path)

        # 2. 사진 파일 저장 (세션별 임시 폴더)
        session_id = str(uuid.uuid4())
        photo_session_dir = os.path.join(TEMP_UPLOAD_DIR, session_id)
        os.makedirs(photo_session_dir, exist_ok=True)

        for photo in photo_files:
            if photo and photo.filename != '':
                basename, extension = os.path.splitext(photo.filename)
                
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.heic']
                if not extension or extension.lower() not in allowed_extensions:
                    continue

                safe_basename = secure_filename(basename)
                if not safe_basename:
                    safe_basename = str(uuid.uuid4())
                
                final_filename = f"{safe_basename}{extension}"
                save_path = os.path.join(photo_session_dir, final_filename)
                photo.save(save_path)
        
        # 3. 지도 생성 로직 호출
        folium_map = generate_map(gpx_path, photo_session_dir)

        if folium_map is None:
            return "지도 생성 실패. GPX 파일 확인 필요.", 500

        # 4. 결과 HTML 페이지 렌더링
        map_html = folium_map._repr_html_()
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Runner's View</title>
                <style>
                    body { font-family: sans-serif; margin: 0; }
                    .container { display: flex; flex-direction: column; height: 100vh; }
                    .header { 
                        background-color: #f8f9fa; padding: 0 20px; border-bottom: 1px solid #dee2e6;
                        position: fixed;
                        top: 0;
                        width: 100%;
                        z-index: 1001;
                        box-sizing: border-box;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        height: 60px;
                    }
                    .header h1 {
                        font-size: 1.5em;
                        margin: 0;
                    }
                    .header .back-button {
                        background-color: white; padding: 8px 12px; border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-decoration: none; color: black;
                        font-weight: bold;
                    }
                    .header .back-button:hover {
                        background-color: #f0f0f0;
                    }
                    .header-placeholder { /* 제목 중앙 정렬을 위한 빈 공간 */
                        width: 120px;
                    }
                    .map-container { 
                        flex-grow: 1; 
                        margin-top: 60px; /* 고정된 헤더 높이만큼 마진 추가 */
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <a href="/" class="back-button"> &larr; 다시 업로드</a>
                        <h1>Runner's View</h1>
                        <div class="header-placeholder"></div>
                    </div>
                    <div class="map-container">
                        {{ map_html|safe }}
                    </div>
                </div>
            </body>
            </html>
        """, map_html=map_html)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
