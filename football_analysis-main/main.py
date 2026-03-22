# main.py

import argparse
import numpy as np
import cv2
# Import the new save function
from utils import read_video, save_video, save_data_to_csv
from trackers import Tracker
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator

def main(video_path, output_path, skip_frames=3):
    # Get original FPS
    cap = cv2.VideoCapture(video_path)
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    if original_fps <= 0:
        original_fps = 24
    cap.release()
    
    target_fps = original_fps / skip_frames

    # 1. Read Video
    video_frames = read_video(video_path, skip_frames=skip_frames)

    # ... (Steps 2-8: All the analysis logic remains exactly the same) ...
    track_stub_path = f'stubs/track_stubs_skip_{skip_frames}.pkl'
    cam_stub_path = f'stubs/camera_movement_stub_skip_{skip_frames}.pkl'

    # 2. Initialize Tracker and get tracks
    tracker = Tracker('models/best.pt')
    tracks = tracker.get_object_tracks(video_frames,
                                       read_from_stub=True,
                                       stub_path=track_stub_path)
    tracker.add_position_to_tracks(tracks)
    # 3. Interpolate Ball Position
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    # 4. Estimate Camera Movement
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,
                                                                              read_from_stub=True,
                                                                              stub_path=cam_stub_path)
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks, camera_movement_per_frame)
    # 5. Transform positions to a 2D view
    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)
    # 6. Estimate Speed and Distance
    speed_and_distance_estimator = SpeedAndDistance_Estimator(fps=target_fps)
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)
    # 7. Assign Teams
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks['players'][0])
    
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],   
                                                 track['bbox'],
                                                 player_id)
            tracks['players'][frame_num][player_id]['team'] = team 
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
    # 8. Assign Ball Possession
    player_assigner = PlayerBallAssigner()
    team_ball_control = []
    for frame_num, player_track in enumerate(tracks['players']):
        ball_bbox = tracks['ball'][frame_num][1]['bbox']
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)

        if assigned_player != -1:
            tracks['players'][frame_num][assigned_player]['has_ball'] = True
            team_ball_control.append(tracks['players'][frame_num][assigned_player]['team'])
        else:
            team_ball_control.append(0)
    team_ball_control = np.array(team_ball_control)


    # 9. Draw Annotations on Video
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames, camera_movement_per_frame)
    output_video_frames = speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)

    # 10. Save Final Video
    save_video(output_video_frames, output_path, fps=target_fps)

    # --- NEW FEATURE: SAVE ANALYSIS TO CSV ---
    # 11. Structure and Save Data
    analysis_data = []
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track_info in player_track.items():
            # Get transformed position safely
            pos_transformed = track_info.get('position_transformed')
            
            record = {
                'frame_number': frame_num,
                'player_id': player_id,
                'team_id': track_info.get('team', -1),
                'has_ball': track_info.get('has_ball', False),
                'speed_mps': track_info.get('speed', 0),
                'distance_meters': track_info.get('distance', 0),
                'x_transformed_meters': pos_transformed[0] if pos_transformed else None,
                'y_transformed_meters': pos_transformed[1] if pos_transformed else None
            }
            analysis_data.append(record)

    # Create the CSV file path from the video output path
    csv_output_path = output_path.replace('.mp4', '_analysis.csv')
    save_data_to_csv(analysis_data, csv_output_path)
    print(f"Analysis data saved to: {csv_output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a football video for player and ball analysis.')
    parser.add_argument('--input_video', type=str, required=True, help='Path to the input video file.')
    parser.add_argument('--output_video', type=str, required=True, help='Path to save the output video file.')
    parser.add_argument('--skip_frames', type=int, default=3, help='Process 1 in every N frames to speed up analysis. Default is 3.')
    args = parser.parse_args()
    main(video_path=args.input_video, output_path=args.output_video, skip_frames=args.skip_frames)