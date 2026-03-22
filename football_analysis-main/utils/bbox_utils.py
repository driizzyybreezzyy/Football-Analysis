# utils/bbox_utils.py
import math

def get_center_of_bbox(bbox):
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

def get_foot_position(bbox):
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int(y2)

def get_bbox_width(bbox):
    x1, _, x2, _ = bbox
    return x2 - x1

def measure_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# --- ADD THIS NEW FUNCTION ---
def measure_xy_distance(p1, p2):
    """
    Calculates the distance between two points in x and y separately.
    """
    return abs(p1[0] - p2[0]), abs(p1[1] - p2[1])