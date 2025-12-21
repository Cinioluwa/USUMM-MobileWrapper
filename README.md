# USUMM: YouTube to Blog Article Converter 📺

**USUMM** (YouTube Summarizer) is a productivity tool built to combat digital addiction. Instead of "doom-scrolling" through an endless feed of thumbnails and clickbait, this app transforms your subscription feed into a curated list of professional blog articles. 

By converting video content into text, you can quickly assess the value of a video before committing 20 minutes to watching it.

---

## 🚀 Key Features

- **Subscription Feed Integration:** Securely connects to your YouTube account via OAuth 2.0 to pull your real-time feed.
- **AI-Powered Analysis:** Leverages **Google Gemini 2.5 Flash-Lite** to analyze video content, creator intent, and tone.
- **Multimodal Content Generation:** Generates a 5-point key takeaway summary followed by a 300-word professional blog article.
- **Smart Search:** Explore specific topics outside your subscriptions using the integrated YouTube Search API.
- **Resilient Architecture:** Features a custom **Exponential Backoff** implementation to handle API rate limits and server hiccups gracefully.

---

## 🛠️ Tech Stack

- **Backend:** Python / Flask
- **AI Model:** Google Gemini API (`google-genai` SDK)
- **API Integration:** YouTube Data API v3
- **Authentication:** OAuth 2.0 (via Authlib & Flask-Session)
- **Frontend:** HTML5 / CSS3

---

## 🏗️ Step-by-Step Setup Guide

Follow these steps to build your own version of this tool.

### 1. Prerequisites
- Python 3.9+
- A [Google Cloud Console](https://console.cloud.google.com/) account.
- A [Google AI Studio](https://aistudio.google.com/) API Key.

### 2. Google Cloud Configuration
1. **Create a Project:** In the Cloud Console, create a new project.
2. **Enable YouTube Data API v3:** Go to "APIs & Services" > "Library" and enable the YouTube API.
3. **Configure OAuth Consent Screen:** Set it to "External" and add your email.
4. **Create Credentials:**
   - Create an **OAuth 2.0 Client ID** (Web Application).
   - Add `http://127.0.0.1:5000/callback` to the **Authorized redirect URIs**.

### 3. Installation
Clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/usumm.git
cd usumm
pip install -r requirements.txt
```

### 4. Environment Configuration (.env)
Create a file named `.env` in the root folder and paste the following, replacing the placeholders with your actual keys:

```
SECRET_KEY=yoursecretkeyhere
YOUTUBE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=your_google_client_secret
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Running the App
Start the Flask server:

```bash
python app.py
```

Open your browser and visit: `http://127.0.0.1:5000`

---

## 🧪 Challenges & Learnings

### Prompt Engineering
One of the core challenges was fine-tuning the Gemini prompt to avoid "generic AI" introductions. I experimented with persona-based prompting to ensure the articles maintain the specific "voice" of the YouTuber.

### API Resilience
To ensure the app didn't crash during peak API usage, I implemented an exponential backoff algorithm. This logic catches transient errors and retries the request after an increasing delay:

$wait\_time = (2^n) + random\_jitter$

### Data Security
Implementing OAuth 2.0 required a deep dive into session management and token handling to ensure that user data remains private and secure while browsing their feed.
