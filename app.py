from flask import Flask, render_template_string, request, redirect, url_for, flash, send_from_directory
import yt_dlp
import re
import os
from supabase import create_client, Client
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

supabase_url = os.getenv('VITE_SUPABASE_URL', '')
supabase_key = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY', '')

supabase: Client = None
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)

def is_valid_youtube_url(url):
    pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    return re.match(pattern, url) is not None

def log_download(video_title, video_url, media_type, filename, file_size=None, status='completed'):
    if not supabase:
        return
    try:
        supabase.table('downloads').insert({
            'video_title': video_title,
            'video_url': video_url,
            'media_type': media_type,
            'filename': filename,
            'file_size': file_size,
            'status': status,
            'downloaded_at': datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Error logging download: {e}")

def get_recent_downloads(limit=10):
    if not supabase:
        return []
    try:
        response = supabase.table('downloads').select('*').order('downloaded_at', desc=True).limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching downloads: {e}")
        return []

def download_media(url, media_type):
    if media_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        }
        exts = ['webm', 'm4a', 'mp3', 'opus']
    else:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4'
        }
        exts = ['mp4', 'mkv', 'webm']
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            video_title = info.get('title', 'Unknown')
            file_size = info.get('filesize')

            for ext in exts:
                candidate = f"{base}.{ext}"
                if os.path.exists(candidate):
                    basename = os.path.basename(candidate)
                    file_size = os.path.getsize(candidate)
                    log_download(video_title, url, media_type, basename, file_size)
                    return basename

            basename = os.path.basename(filename)
            log_download(video_title, url, media_type, basename, file_size)
            return basename
    except Exception as e:
        print(f"An error occurred during download: {e}")
        return None

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>freeyt - YouTube Downloader</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #f8fafc; }
    .container { max-width: 600px; margin-top: 40px; margin-bottom: 40px; }
    .card { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .btn-primary { background: #d90429; border: none; }
    .btn-primary:hover { background: #a0031f; }
    .download-link { font-size: 1.1em; }
    .history-section { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; }
    .history-item { padding: 12px; background: #f1f5f9; border-radius: 4px; margin-bottom: 8px; font-size: 0.9em; }
    .history-title { font-weight: 500; color: #0f172a; }
    .history-meta { color: #64748b; font-size: 0.85em; margin-top: 4px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card p-4">
      <h2 class="mb-4 text-center text-danger">freeyt</h2>
      <form method="post" class="mb-3">
        <div class="input-group mb-2">
          <input type="text" name="url" class="form-control" placeholder="Enter YouTube video URL" required>
        </div>
        <div class="mb-3 text-center">
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="media_type" id="audio" value="audio" checked>
            <label class="form-check-label" for="audio">Audio</label>
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="media_type" id="video" value="video">
            <label class="form-check-label" for="video">Video</label>
          </div>
        </div>
        <div class="d-grid">
          <button type="submit" class="btn btn-primary">Download</button>
        </div>
      </form>
      {% if filename %}
        <div class="alert alert-success text-center">
          <span class="download-link">
            <strong>Download ready:</strong>
            <a href="{{ url_for('download_file', filename=filename) }}" class="link-success">{{ filename }}</a>
          </span>
        </div>
      {% endif %}
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-warning mt-3">
            <ul class="mb-0">
            {% for message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
            </ul>
          </div>
        {% endif %}
      {% endwith %}
      {% if recent_downloads %}
      <div class="history-section">
        <h5 class="mb-3">Recent Downloads</h5>
        {% for download in recent_downloads %}
          <div class="history-item">
            <div class="history-title">{{ download.video_title }}</div>
            <div class="history-meta">
              {{ download.media_type|capitalize }} • {{ download.downloaded_at[:10] }}
            </div>
          </div>
        {% endfor %}
      </div>
      {% endif %}
      <div class="text-center mt-4 text-muted" style="font-size:0.95em;">
        &copy; 2025 freeyt
      </div>
    </div>
  </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    filename = None
    if request.method == 'POST':
        url = request.form['url'].strip()
        media_type = request.form.get('media_type', 'audio')
        if not url:
            flash('No URL provided.')
        elif not is_valid_youtube_url(url):
            flash('Invalid YouTube URL.')
        else:
            filename = download_media(url, media_type)
            if filename:
                flash('Download ready! Click the link below to get your file.')
            else:
                flash('Download failed. Please check the URL or your internet connection.')
        recent_downloads = get_recent_downloads()
        return render_template_string(HTML, filename=filename, recent_downloads=recent_downloads)
    recent_downloads = get_recent_downloads()
    return render_template_string(HTML, filename=None, recent_downloads=recent_downloads)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)