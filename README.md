#  InstaFetch - Web Video & Audio Downloader

[![Render](https://img.shields.io/badge/Render-Live-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://instagram-reel-downloader-n4jx.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

A powerful and lightweight web application that allows users to download Instagram Reels as **MP4 video** or convert them to **MP3 audio**. 

Deployed live on Render! 🚀

## 🔗 Live Demo
👉 **[Click here to use the App](https://instagram-reel-downloader-n4jx.onrender.com)**

---

## ✨ Features
* **Video Download:** Fetches high-quality MP4s directly from Instagram.
* **Audio Conversion:** Extracts audio from Reels and converts to MP3 automatically using `moviepy`.
* **Smart Metadata:** Automatically detects the caption to name your files cleanly.
* **Web Interface:** Clean, responsive UI with a real-time progress bar.
* **No Login Required:** Works for public posts and reels.

## 🛠️ Tech Stack
* **Backend:** Python (Flask)
* **Scraping Engine:** Instaloader
* **Media Processing:** MoviePy (FFmpeg)
* **Deployment:** Render (Gunicorn)
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)

---

##  Local Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/NOORBAJI55/Instagram_Reel_Downloader
    cd Instagram_Reel_Downloader
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    python app.py
    ```

4.  **Open in Browser**
    Visit `http://127.0.0.1:5000`
---

## 🚀 Deployment
This app is configured to run on **Render**.
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn app:app`

## ⚠️ Disclaimer
This tool is for **educational purposes only**. Please respect copyright laws and Instagram's Terms of Service. Do not use this tool to infringe on content creators' rights.
