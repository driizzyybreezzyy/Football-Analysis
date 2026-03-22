# Football Analysis Project

A YOLO-based football analysis system that detects players, referees, and the ball in video footage. It includes features for tracking, team assignment, camera movement estimation, and perspective transformation.

## Features
- **Object Detection**: Detects players, referees, and the ball using YOLOv8.
- **Tracking**: Tracks players across frames.
- **Team Assignment**: Automatically assigns players to teams based on jersey colors.
- **Camera Movement Estimation**: Compensates for camera pans and tilts.
- **View Transformation**: Maps pixel coordinates to ground coordinates for speed and distance estimation.
- **Web Interface**: Easy-to-use Flask web app for video uploads and YouTube analysis.

---

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher.
- `git` installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/driizzyybreezzyy/Football-Analysis.git
cd Football-Analysis
```

### 3. Create a Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r football_analysis-main/requirements.txt
```

### 5. Download Model Weights
The custom YOLO model weights (`best.pt`) are excluded from the repository due to file size limits. 
- Obtain the `best.pt` model file.
- Place it in: `football_analysis-main/models/best.pt`.

### 6. Run the Application
You can run the project via the web interface:
```bash
cd football_analysis-main
python app.py
```
Then open your browser and navigate to `http://127.0.0.1:5000`.

---

## Project Structure
- `football_analysis-main/`: Core application logic.
  - `app.py`: Flask application server.
  - `main.py`: Video processing and analysis script.
  - `trackers/`: Object tracking implementations.
  - `team_assigner/`: Jersey color analysis.
  - `models/`: Folder for YOLO model weights.
- `runs/`: Output directory for detection results (local only).

---

## Technical Details
- **Core AI**: [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- **Computer Vision**: OpenCV, [Supervision](https://github.com/roboflow/supervision)
- **Web Framework**: Flask
- **Video Download**: yt-dlp
