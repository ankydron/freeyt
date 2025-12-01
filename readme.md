# freeyt - YouTube Downloader

**freeyt** is a web application that allows users to download YouTube videos as audio or video files. Built with Flask and [yt-dlp](https://github.com/yt-dlp/yt-dlp), it features cloud-based download history tracking via Supabase.

## Features

- Download YouTube videos as audio (best quality)
- Download YouTube videos as video (best quality, MP4)
- Download history tracking with Supabase integration
- Clean, modern Bootstrap interface
- Real-time download status and file management
- Recent downloads display on dashboard

## Requirements

- Python 3.7+
- Flask
- yt-dlp
- supabase-py
- Supabase account (free tier available)

## Installation

1. **Clone or download this repository.**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or for development with virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   Create a `.env` file in the project root:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

   Get these values from your [Supabase project settings](https://app.supabase.com/).

## Usage

1. **Run the app locally:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://127.0.0.1:5000/
   ```

3. **To download:**
   - Paste a YouTube video URL
   - Choose Audio or Video format
   - Click Download
   - Wait for processing
   - Click the download link to save the file

4. **View download history:**
   - Recent downloads display on the dashboard
   - Automatically synced with Supabase

## Deployment

### Production with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Cloud Platforms

Deploy to platforms supporting Python:
- **Render**: https://render.com
- **Heroku**: https://heroku.com
- **PythonAnywhere**: https://pythonanywhere.com
- **Railway**: https://railway.app

## Database

The app uses Supabase PostgreSQL for download history:

### Schema

- `downloads` table stores:
  - Video title and URL
  - Download type (audio/video)
  - Filename and file size
  - Timestamp and status

### Security

- Row Level Security (RLS) enabled
- Public read access for download history
- Anonymous insertion for download logging

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_SUPABASE_URL` | Your Supabase project URL |
| `VITE_SUPABASE_SUPABASE_ANON_KEY` | Your Supabase anon public key |

## Notes

- Downloaded files are saved in the `downloads` folder
- Files are stored locally and served directly from the server
- For production, implement file cleanup policies
- Respect YouTube's Terms of Service when downloading content
- This app is for educational and personal use only

## License

MIT License

---

**Made with Flask and Supabase**