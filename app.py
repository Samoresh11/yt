from flask import Flask, render_template, request, jsonify
import os
import re
from pytube import YouTube

app = Flask(__name__)

# Ensure directories exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('downloads', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Validate YouTube URL
    if not is_valid_youtube_url(url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    try:
        # Create YouTube object
        yt = YouTube(url)
        
        # Get the highest resolution progressive stream
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            return jsonify({'error': 'No suitable video stream found'}), 400
        
        # Download the video
        filename = stream.download(output_path='downloads/')
        
        # Extract video title for response
        video_title = yt.title
        
        return jsonify({
            'success': True,
            'message': f'Successfully downloaded "{video_title}"',
            'video_title': video_title,
            'filename': os.path.basename(filename)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def is_valid_youtube_url(url):
    """Validate YouTube URL format"""
    pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'
    return re.match(pattern, url) is not None

if __name__ == '__main__':
    app.run(debug=True)
