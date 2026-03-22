import os
os.environ['YOLO_OFFLINE'] = 'True'
os.environ['ULTRALYTICS_OFFLINE'] = 'True'

import sys
print("Importing torch...")
import torch
print("Torch version:", torch.__version__)
print("Importing ultralytics...")
import ultralytics
print("Ultralytics version:", ultralytics.__version__)
from ultralytics import YOLO
print("Importing pickle...")
import pickle
print("All imports done.")
