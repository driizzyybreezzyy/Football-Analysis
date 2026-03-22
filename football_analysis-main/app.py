import os
import subprocess
import sys
import uuid
import threading
from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import yt_dlp

# =================================================================
#                 --- FLASK APP CONFIGURATION ---
# =================================================================
# Explicitly tell Flask where the static folder is.
app = Flask(__name__, static_folder='static')

# Define folder paths
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output_videos' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

# Ensure the necessary directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Simple in-memory job store
jobs = {}

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def download_youtube_video(url, output_path):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def process_video_job(job_id, input_video_path, output_filename, original_filename):
    output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    csv_filename = output_filename.replace('.mp4', '_analysis.csv')
    
    python_executable = sys.executable 

    command = [
        python_executable,
        'main.py', 
        '--input_video', input_video_path, 
        '--output_video', output_video_path
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['csv_filename'] = csv_filename
        jobs[job_id]['output_filename'] = output_filename
        print(f"Job {job_id} complete. Output video is at: {output_video_path}")
    except subprocess.CalledProcessError as e:
        print("Error during analysis:")
        print(e.stderr)
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error_message'] = e.stderr

# =================================================================
#                 --- MAIN APPLICATION ROUTES ---
# =================================================================

@app.route('/', methods=['GET', 'POST'])
def upload_and_process():
    """Handles the video upload or youtube URL and processing logic."""
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        file = request.files.get('video')
        
        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "processing", "csv_filename": "", "output_filename": "", "error_message": ""}
        
        if youtube_url and youtube_url.strip() != "":
            # --- 1. Handle YouTube Link ---
            input_filename = f"youtube_{job_id}.mp4"
            input_video_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
            
            def yt_task():
                try:
                    print(f"Downloading YouTube video {youtube_url}...")
                    download_youtube_video(youtube_url, input_video_path)
                    print(f"Download complete. Starting analysis...")
                    output_filename = 'output_' + input_filename.rsplit('.', 1)[0] + '.mp4'
                    process_video_job(job_id, input_video_path, output_filename, input_filename)
                except Exception as e:
                    print(f"Error in YouTube task: {e}")
                    jobs[job_id]['status'] = 'error'
                    jobs[job_id]['error_message'] = str(e)
            
            threading.Thread(target=yt_task).start()
            return redirect(url_for('polling', job_id=job_id))
            
        elif file and file.filename != '':
            # --- 2. Handle File Upload ---
            if allowed_file(file.filename):
                input_filename = secure_filename(file.filename)
                input_filename = f"{job_id}_{input_filename}"  # avoid collisions
                input_video_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
                file.save(input_video_path)
                
                output_filename = 'output_' + input_filename.rsplit('.', 1)[0] + '.mp4'
                threading.Thread(target=process_video_job, args=(job_id, input_video_path, output_filename, input_filename)).start()
                return redirect(url_for('polling', job_id=job_id))
            else:
                return "Invalid file type!", 400
        else:
            return "No video file or YouTube URL provided!", 400

    # For a GET request, just show the upload page
    return render_template('index.html')

@app.route('/polling/<job_id>')
def polling(job_id):
    if job_id not in jobs:
        return "Job not found", 404
    return render_template('poll.html', job_id=job_id)

@app.route('/status/<job_id>')
def job_status(job_id):
    if job_id not in jobs:
        return jsonify({"status": "not_found"}), 404
    return jsonify(jobs[job_id])

@app.route('/success/<job_id>')
def success(job_id):
    if job_id not in jobs or jobs[job_id]['status'] != 'completed':
        return "Not completed yet or job not found.", 404
    return render_template('success.html', csv_filename=jobs[job_id]['csv_filename'], output_filename=jobs[job_id]['output_filename'])

# =================================================================
#                 --- SCRIPT ENTRY POINT ---
# =================================================================
if __name__ == '__main__':
    app.run(debug=True)