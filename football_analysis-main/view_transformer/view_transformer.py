import numpy as np
import cv2

class ViewTransformer():
    def __init__(self):
        """
        Initializes the ViewTransformer with predefined source and destination points
        to create a perspective transformation matrix.
        """
        court_width = 68
        court_length = 23.32

        # Source points are the 4 corners of the penalty box in the video frame (pixels)
        self.pixel_vertices = np.array([
            [110, 1035], 
            [265, 275], 
            [910, 260], 
            [1640, 915]
        ])
        
        # Destination points are the same 4 corners in a top-down view (meters)
        self.target_vertices = np.array([
            [0, court_width],
            [0, 0],
            [court_length, 0],
            [court_length, court_width]
        ])

        # Convert points to float32, which is required by getPerspectiveTransform
        self.pixel_vertices = self.pixel_vertices.astype(np.float32)
        self.target_vertices = self.target_vertices.astype(np.float32)

        # FIX: Corrected the typo in the variable name
        self.perspective_transformer = cv2.getPerspectiveTransform(self.pixel_vertices, self.target_vertices)

    def transform_point(self, point):
        """
        Transforms a single point from the video's perspective to the top-down view.
        Returns None if the point is outside the defined source polygon.
        """
        if point is None:
            return None
            
        p = (int(point[0]), int(point[1]))
        is_inside = cv2.pointPolygonTest(self.pixel_vertices, p, False) >= 0 
        if not is_inside:
            return None
        
        # FIX: Convert the input tuple/list to a NumPy array for transformation
        reshaped_point = np.array(point).reshape(-1, 1, 2).astype(np.float32)
        
        # Apply the perspective transformation
        transformed_point = cv2.perspectiveTransform(reshaped_point, self.perspective_transformer)
        
        # Return the transformed point as a simple array or list
        return transformed_point.reshape(-1, 2)

    def add_transformed_position_to_tracks(self, tracks):
        """
        Iterates through all tracks and adds a 'position_transformed' key
        with the coordinates in the top-down view.
        """
        for object_name, object_tracks in tracks.items():
            for frame_num, frame_tracks in enumerate(object_tracks):
                if isinstance(frame_tracks, dict):
                    for track_id, track_info in frame_tracks.items():
                        # Get the camera-adjusted position safely
                        position_adjusted = track_info.get('position_adjusted')

                        # Transform the point
                        position_transformed = self.transform_point(position_adjusted)

                        # If the transformation was successful, convert the result to a simple list
                        if position_transformed is not None:
                            position_transformed = position_transformed.squeeze().tolist()
                        
                        # Add the key to the tracks dictionary (even if it's None)
                        tracks[object_name][frame_num][track_id]['position_transformed'] = position_transformed