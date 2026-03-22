import pickle
import torch
from ultralytics import YOLO

print("Loading model...")
model = YOLO('models/best.pt')
print("Model loaded successfully.")

print("Loading stubs...")
with open('stubs/track_stubs.pkl', 'rb') as f:
    tracks = pickle.load(f)
print(f"Tracks loaded: {len(tracks['players'])} frames.")

with open('stubs/camera_movement_stub.pkl', 'rb') as f:
    camera_movement = pickle.load(f)
print(f"Camera movement loaded: {len(camera_movement)} frames.")
