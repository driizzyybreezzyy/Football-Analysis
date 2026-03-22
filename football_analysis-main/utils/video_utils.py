# utils/video_utils.py
import cv2
import pandas as pd # <-- ADD THIS IMPORT

def read_video(video_path, skip_frames=1):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % skip_frames == 0:
            frames.append(frame)
        frame_count += 1
    cap.release()
    return frames

def save_video(output_video_frames, output_video_path, fps=24):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    height, width, _ = output_video_frames[0].shape
    frame_size = (width, height)
    out = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size)
    for frame in output_video_frames:
        out.write(frame)
    out.release()

# --- ADD THIS NEW FUNCTION ---
def save_data_to_csv(data, output_path):
    """
    Saves a list of dictionaries (our analysis data) to a CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)