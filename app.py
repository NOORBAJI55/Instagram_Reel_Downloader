from flask import Flask, render_template_string, request, send_file, jsonify
import instaloader
import re
import requests
import os
from moviepy import VideoFileClip

app = Flask(__name__)

# Setup a temporary folder for audio processing
TEMP_FOLDER = "temp_downloads"
os.makedirs(TEMP_FOLDER, exist_ok=True)

def sanitize_filename(text):
    if not text: return "insta_download"
    text = text.replace('\n', ' ')
    text = re.sub(r'[^a-zA-Z0-9 \-_]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:60]

@app.route('/')
def home():
    # We put the HTML directly here for simplicity
    return render_template_string(HTML_TEMPLATE)

@app.route('/fetch_info', methods=['POST'])
def fetch_info():
    """Step 1: Get metadata (Thumbnail, Caption) without downloading the full video yet."""
    url = request.json.get('link')
    L = instaloader.Instaloader()
    
    try:
        match = re.search(r'(p|reel|tv)/([A-Za-z0-9_-]+)', url)
        if not match: return jsonify({"error": "Invalid URL"}), 400
        
        shortcode = match.group(2)
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        return jsonify({
            "status": "success",
            "shortcode": shortcode,
            "caption": sanitize_filename(post.caption),
            "thumbnail": post.url, # URL to the image preview
            "video_url": post.video_url # We will need this for step 2
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    """Step 2: Download and Convert"""
    data = request.json
    video_url = data.get('video_url')
    filename_base = data.get('filename')
    mode = data.get('mode') # 'video' or 'audio'
    
    try:
        # Download video content
        print(f"⬇️ Downloading content for {mode}...")
        response = requests.get(video_url)
        
        if mode == 'video':
            # --- VIDEO MODE: Stream directly ---
            from io import BytesIO
            return send_file(
                BytesIO(response.content),
                as_attachment=True,
                download_name=f"{filename_base}.mp4",
                mimetype='video/mp4'
            )
            
        elif mode == 'audio':
            # --- AUDIO MODE: Save, Convert, Send, Delete ---
            
            # 1. Save temp video
            temp_vid_path = os.path.join(TEMP_FOLDER, f"{filename_base}.mp4")
            temp_audio_path = os.path.join(TEMP_FOLDER, f"{filename_base}.mp3")
            
            with open(temp_vid_path, 'wb') as f:
                f.write(response.content)
            
            # 2. Convert using MoviePy (Fixed: Removed 'verbose' argument)
            print("🎵 Converting to MP3...")
            clip = VideoFileClip(temp_vid_path)
            
            # FIXED LINE BELOW:
            clip.audio.write_audiofile(temp_audio_path, logger=None)
            
            clip.close()
            
            # 3. Read MP3 into memory
            with open(temp_audio_path, 'rb') as f:
                mp3_data = f.read()
            
            # 4. Cleanup temp files
            # (Wrap in try/except so if file is locked, it doesn't crash app)
            try:
                os.remove(temp_vid_path)
                os.remove(temp_audio_path)
            except Exception as e:
                print(f"Warning: Could not delete temp files: {e}")
            
            from io import BytesIO
            return send_file(
                BytesIO(mp3_data),
                as_attachment=True,
                download_name=f"{filename_base}.mp3",
                mimetype='audio/mpeg'
            )

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

# --- THE FRONTEND (HTML/CSS/JS) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InstaLoader Pro</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            width: 90%;
            max-width: 400px;
            text-align: center;
        }
        h1 { color: #333; margin-bottom: 20px; font-size: 24px;}
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-sizing: border-box;
            margin-bottom: 15px;
            font-size: 16px;
        }
        /* Radio Button Styling */
        .radio-group {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        .radio-group label {
            cursor: pointer;
            padding: 8px 16px;
            border: 2px solid #eee;
            border-radius: 20px;
            font-weight: bold;
            color: #555;
            transition: all 0.3s;
        }
        input[type="radio"] { display: none; }
        input[type="radio"]:checked + label {
            background: #E1306C;
            color: white;
            border-color: #E1306C;
        }

        .btn {
            background: #E1306C;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: background 0.3s;
        }
        .btn:hover { background: #C13584; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }

        /* Progress Bar */
        .progress-container {
            width: 100%;
            background-color: #eee;
            border-radius: 5px;
            margin-top: 15px;
            display: none; /* Hidden by default */
        }
        .progress-bar {
            width: 0%;
            height: 10px;
            background-color: #4CAF50;
            border-radius: 5px;
            transition: width 0.4s;
        }
        .status-text {
            margin-top: 5px;
            font-size: 14px;
            color: #666;
            min-height: 20px;
        }
        
        #download-section { display: none; margin-top: 20px; border-top: 1px solid #eee; padding-top: 20px; }
        .preview-img { width: 100%; border-radius: 8px; margin-bottom: 10px; }

        .footer {
            margin-top: 25px;
            font-size: 13px;
            color: #888;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }
        .footer a {
            color: #E1306C;
            text-decoration: none;
            font-weight: bold;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<div class="card">
    <h1>Insta Downloader</h1>
    
    <input type="text" id="linkInput" placeholder="Paste Reel Link Here...">
    
    <div class="radio-group">
        <input type="radio" id="vid" name="type" value="video" checked>
        <label for="vid">Video (MP4)</label>
        
        <input type="radio" id="aud" name="type" value="audio">
        <label for="aud">Audio (MP3)</label>
    </div>

    <button class="btn" onclick="fetchMetadata()">Fetch Details</button>

    <div class="progress-container" id="progressContainer">
        <div class="progress-bar" id="progressBar"></div>
    </div>
    <div class="status-text" id="statusText"></div>

    <div id="download-section">
        <img id="previewImg" class="preview-img" src="">
        <h4 id="videoTitle" style="margin: 0 0 10px 0; font-size: 14px; color: #555;"></h4>
        <button class="btn" id="finalDownloadBtn" style="background-color: #4CAF50;">Download Now</button>
    </div>
    <div class="footer">
        Created with ❤️ by <a href="https://github.com/NOORBAJI55" target="_blank">Shaik Noor Baji</a>
    </div>

</div>
</div>

<script>
    let currentVideoData = {};

    function fetchMetadata() {
        const link = document.getElementById('linkInput').value;
        const status = document.getElementById('statusText');
        const progress = document.getElementById('progressBar');
        const container = document.getElementById('progressContainer');
        const dlSection = document.getElementById('download-section');
        
        if(!link) { alert("Please paste a link first!"); return; }

        // Reset UI
        dlSection.style.display = 'none';
        container.style.display = 'block';
        progress.style.width = '30%';
        status.innerText = "Fetching Metadata...";

        // Step 1: Call Server to get Info
        fetch('/fetch_info', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ link: link })
        })
        .then(response => response.json())
        .then(data => {
            if(data.error) {
                status.innerText = "Error: " + data.error;
                progress.style.width = '0%';
                return;
            }
            
            // Success: Update UI
            progress.style.width = '100%';
            status.innerText = "Ready to Download!";
            
            // Store data for step 2
            currentVideoData = data;
            
            // Show Preview
            document.getElementById('previewImg').src = data.thumbnail; // Note: Insta images might block hotlinking
            document.getElementById('videoTitle').innerText = data.caption || "Instagram Video";
            dlSection.style.display = 'block';
        })
        .catch(err => {
            status.innerText = "Network Error";
            console.error(err);
        });
    }

    document.getElementById('finalDownloadBtn').addEventListener('click', function() {
        const mode = document.querySelector('input[name="type"]:checked').value;
        const status = document.getElementById('statusText');
        const progress = document.getElementById('progressBar');
        
        // UI Feedback
        status.innerText = mode === 'audio' ? "Converting to Audio... (This takes a moment)" : "Starting Download...";
        progress.style.width = '50%'; // Fake progress for processing

        fetch('/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                video_url: currentVideoData.video_url,
                filename: currentVideoData.caption,
                mode: mode
            })
        })
        .then(response => {
            if(response.ok) {
                progress.style.width = '100%';
                status.innerText = "Download Started!";
                return response.blob();
            }
            throw new Error("Download failed");
        })
        .then(blob => {
            // Trigger browser download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentVideoData.caption + (mode === 'audio' ? ".mp3" : ".mp4");
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(err => {
            status.innerText = "Error Downloading File";
        });
    });
</script>

</body>
</html>
'''

if __name__ == '__main__':
    app.run()
