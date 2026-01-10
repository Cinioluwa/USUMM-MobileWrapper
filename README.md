
# USUMM-MobileWrapper: YouTube Summarizer for Mobile & Web 📱🖥️

**USUMM-MobileWrapper** is a mobile-first YouTube summarizer app, combining a Flask backend with a Cordova-powered Android/iOS wrapper. It transforms your YouTube feed into immersive blog articles using Google Gemini AI, with robust authentication and mobile features.

---

## 🚀 Key Features

- **Mobile & Tablet Support:** Cordova wrapper for Android/iOS, optimized for touch and offline use.
- **Subscription Feed Integration:** Secure OAuth 2.0 login to pull your YouTube feed.
- **AI-Powered Summaries:** Uses Google Gemini 2.5 Flash-Lite for detailed, engaging blog-style video summaries.
- **Feed Download:** Download your feed for offline reading.
- **Offline Mode:** Cordova-ready for mobile offline access (service worker for web, Cordova for mobile).
- **Session Reset:** Built-in `/clear-session` route for troubleshooting OAuth and refresh token issues.
- **Smart Search:** Search YouTube directly from the app.
- **Resilient Architecture:** Exponential backoff for API reliability.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.13 / Flask
- **Mobile Wrapper:** Cordova (Android/iOS)
- **AI Model:** Google Gemini API (`google-genai` SDK)
- **API Integration:** YouTube Data API v3
- **Authentication:** OAuth 2.0 (Authlib)
- **CORS:** flask-cors
- **Production Server:** Gunicorn
- **Deployment:** Railway (or local)
- **Frontend:** HTML5 / CSS3 (Jinja templates)

---

## 🏗️ Setup Guide

### 1. Prerequisites
- Python 3.13+
- Node.js & Cordova CLI (for mobile build)
- Android Studio (for Android build)
- Google Cloud Console & AI Studio API Key

### 2. Google Cloud Configuration
1. **Create a Project** in Cloud Console.
2. **Enable YouTube Data API v3**.
3. **Configure OAuth Consent Screen** (External).
4. **Create OAuth 2.0 Client ID** (Web Application):
    - Add `http://127.0.0.1:5000/callback` and your production/callback URLs.

### 3. Backend Installation
Clone and install dependencies:

```bash
git clone https://github.com/yourusername/usumm-mobile-wrapper.git
cd USUMM-MobileWrapper
pip install -r requirements.txt
```

### 4. Environment Configuration (.env)
Create a `.env` file in the root folder:

```
SECRET_KEY=your_secret_key
YOUTUBE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=your_google_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Running the Backend

```bash
python app.py
# or for production
gunicorn app:app
```

Visit: `http://127.0.0.1:5000`

### 6. Cordova Mobile Wrapper Setup

```bash
cd usumm-mobile-wrapper
cordova platform add android
cordova platform add ios
cordova plugin add cordova-plugin-inappbrowser cordova-plugin-network-information
cordova build android # or ios
```

Update `config.xml` for HTTPS intents and permissions as needed.

### 7. Mobile App Configuration
- Update API URLs in `www/index.html` to point to your backend.
- Build and deploy to your device/emulator.

---

## 🧪 Troubleshooting & Tips

- **OAuth Refresh Token Issues:**
   - Use `/clear-session` route to fully reset session.
   - Remove app access from your Google account, then log in again.
- **Cordova Build Issues:**
   - Ensure Android SDK path is set in `local.properties`.
   - Use Android Studio for Gradle setup.
- **Offline Mode:**
   - Cordova handles offline for mobile; service worker is used for web only.
- **Production Deployment:**
   - Use Gunicorn and Railway for scalable deployment.

---

## ✨ Improvements & Learnings

- **Immersive AI Prompt:**
   - Custom prompt for Gemini ensures summaries match the creator’s style and provide a vivid, blog-like experience.
- **Session Management:**
   - Added `/clear-session` for robust OAuth troubleshooting.
- **Mobile Experience:**
   - Cordova wrapper enables true mobile/tablet usability, with offline and download support.

---

## 📄 License

MIT License
