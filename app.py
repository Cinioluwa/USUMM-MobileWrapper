import os
import time
import random
import html
from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# --- CLI STYLE IMPORTS (LATEST SDK) ---
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Configuration & Setup
load_dotenv()
app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# --- THE CLI STYLE INITIALIZATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Use the stable 2025 model ID to fix the 404 error
# Note: Ensure your API key has 'YouTube' access enabled in AI Studio.
MODEL_ID = "gemini-2.5-flash-lite" 

# OAuth Setup
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv("YOUTUBE_CLIENT_ID"),
    client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/youtube.readonly'
    }
)

# --- Helper Functions ---

def get_authorized_service():
    token = session.get('google_token')
    if not token:
        return None
    creds = Credentials(
        token=token['access_token'],
        refresh_token=token.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET")
    )
    return build("youtube", "v3", credentials=creds)

# --- Routes ---

@app.route('/download_feed')
def download_feed():
    token = session.get('google_token')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    youtube = get_authorized_service()
    if not youtube:
        return jsonify({'error': 'No YouTube service'}), 401
    sub_response = youtube.subscriptions().list(
        part="snippet",
        mine=True,
        maxResults=20
    ).execute()
    videos = []
    video_ids = []
    for sub in sub_response.get('items', []):
        channel_avatar = sub['snippet']['thumbnails']['default']['url']
        channel_id = sub['snippet']['resourceId']['channelId']
        uploads_id = "UU" + channel_id[2:]
        playlist_res = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_id,
            maxResults=1
        ).execute()
        for item in playlist_res.get('items', []):
            vid_id = item['contentDetails']['videoId']
            videos.append({
                'video_id': vid_id,
                'title': html.unescape(item['snippet']['title']),
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'channelTitle': item['snippet']['channelTitle'],
                'channel_avatar': channel_avatar,
                'description': html.unescape(item['snippet']['description']),
                'published_at': item['snippet']['publishedAt']
            })
            video_ids.append(vid_id)
    # Fetch Stats (Likes/Comments) in Batch
    if video_ids:
        stats_response = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()
        stats_map = {s['id']: s['statistics'] for s in stats_response.get('items', [])}
        for v in videos:
            v_stats = stats_map.get(v['video_id'], {})
            v['like_count'] = v_stats.get('likeCount', '0')
            v['comment_count'] = v_stats.get('commentCount', '0')
    videos = sorted(videos, key=lambda x: x['published_at'], reverse=True)
    return jsonify(videos)
@app.route('/')
def index():
    token = session.get('google_token')
    if not token:
        return render_template('login.html')

    youtube = get_authorized_service()
    if not youtube:
        return redirect(url_for('login'))

    # Fetch User Subscriptions
    sub_response = youtube.subscriptions().list(
        part="snippet",
        mine=True,
        maxResults=20 # Reduced from 100 for faster page loads
    ).execute()

    videos = []
    video_ids = []
    
    for sub in sub_response.get('items', []):
        channel_avatar = sub['snippet']['thumbnails']['default']['url']
        channel_id = sub['snippet']['resourceId']['channelId']
        uploads_id = "UU" + channel_id[2:] 

        # Get the latest video for each channel
        playlist_res = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_id,
            maxResults=1
        ).execute()

        for item in playlist_res.get('items', []):
            vid_id = item['contentDetails']['videoId']
            videos.append({
                'video_id': vid_id,
                'title': html.unescape(item['snippet']['title']),
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'channelTitle': item['snippet']['channelTitle'],
                'channel_avatar': channel_avatar,
                'description': html.unescape(item['snippet']['description']),
                'published_at': item['snippet']['publishedAt']
            })
            video_ids.append(vid_id)
    
    # Fetch Stats (Likes/Comments) in Batch
    if video_ids:
        stats_response = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()

        # Map stats to video IDs to ensure correct matching
        stats_map = {s['id']: s['statistics'] for s in stats_response.get('items', [])}
        for v in videos:
            v_stats = stats_map.get(v['video_id'], {})
            v['like_count'] = v_stats.get('likeCount', '0')
            v['comment_count'] = v_stats.get('commentCount', '0')

    # Sort by Newest
    videos = sorted(videos, key=lambda x: x['published_at'], reverse=True)
    return render_template('index.html', videos=videos)

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('index'))


    youtube = get_authorized_service()
    if not youtube:
        return redirect(url_for('login'))

    search_res = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=15
    ).execute()

    videos = []
    video_ids = []
    channel_ids = []

    for item in search_res.get('items', []):
        v_id = item['id']['videoId']
        video_ids.append(v_id)
        channel_ids.append(item['snippet']['channelId'])
        videos.append({
            'video_id': v_id,
            'title': html.unescape(item['snippet']['title']),
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'channelTitle': item['snippet']['channelTitle'],
            'channelId': item['snippet']['channelId'],
            'description': html.unescape(item['snippet']['description']),
            'published_at': item['snippet']['publishedAt']
        })

    if video_ids:
        # Batch fetch avatars
        channels_res = youtube.channels().list(
            part="snippet",
            id=",".join(list(set(channel_ids)))
        ).execute()
        avatar_map = {c['id']: c['snippet']['thumbnails']['default']['url'] for c in channels_res.get('items', [])}

        # Batch fetch stats
        stats_res = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()
        stats_map = {s['id']: s['statistics'] for s in stats_res.get('items', [])}

        for v in videos:
            v['channel_avatar'] = avatar_map.get(v['channelId'])
            v_stats = stats_map.get(v['video_id'], {})
            v['like_count'] = v_stats.get('likeCount', '0')
            v['comment_count'] = v_stats.get('commentCount', '0')

    return render_template('index.html', videos=videos)
@app.route('/summarize/<video_id>')
def summarize(video_id):
    youtube = get_authorized_service()
    if not youtube:
        return redirect(url_for('login'))
    video_res = youtube.videos().list(part="snippet", id=video_id).execute()
    if not video_res or not video_res.get('items'):
        return "Video not found", 404
    snippet = video_res['items'][0]['snippet']
    channel = snippet['channelTitle']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # --- CLI STYLE PROMPT & CALL ---
    prompt_text = f"""
        Analyze the video: {video_url}
        Write a professional blog post. 

        CRITICAL: Return the response ONLY in raw HTML format. 
        DO NOT use Markdown (no ## or **). 
        Use ONLY these tags: <h1>, <h2>, <p>, <ul>, <li>.

        Structure:
        1. <h1>[Catchy Blog Title]</h1>
        2. <p>[Introduction mentioning {channel}]</p>
        3. <h2>[Section Subheading]</h2>
        4. <p>[Detailed content]</p>
        ...
        """

    # Exponential Backoff variables
    max_retries = 3
    wait_time = 2 
    article_html = ""

    for attempt in range(max_retries):
        try:
            # Using Part.from_uri to pass the YouTube link multimodal style
            response = gemini_client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    types.Part.from_uri(file_uri=video_url, mime_type="video/mp4"),
                    types.Part.from_text(text=prompt_text)
                ],
            )
            if response.text is not None:
                article_html = response.text.replace('```html', '').replace('```', '').strip()
            else:
                article_html = "<h2>AI Error</h2><p>No response from AI model.</p>"
            break
        except APIError as e:
            if attempt < max_retries - 1:
                time.sleep(wait_time)
                wait_time *= 2
            else:
                article_html = f"<h2>AI Error</h2><p>{e}</p>"
        except Exception as e:
            article_html = f"<h2>Unexpected Error</h2><p>{e}</p>"

    video_details = {
        'title': snippet['title'],
        'channel': channel,
        'video_id': video_id,
        'article': article_html,
        'thumbnail': snippet['thumbnails']['high']['url']
    }
    return render_template('blog.html', video=video_details)

# --- Auth Routes ---

@app.route('/login')
def login():
    if not hasattr(oauth, 'google') or oauth.google is None:
        return "Google OAuth is not configured properly.", 500
    return oauth.google.authorize_redirect(url_for('authorize', _external=True))

@app.route('/callback')
def authorize():
    if not hasattr(oauth, 'google') or oauth.google is None:
        return "Google OAuth is not configured properly.", 500
    session['google_token'] = oauth.google.authorize_access_token()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)