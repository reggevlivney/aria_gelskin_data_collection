import cv2
from pathlib import Path

def combine_videos_side_by_side(video1_path, video2_path, output_path):
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)

    # Get properties
    fps1 = cap1.get(cv2.CAP_PROP_FPS)
    fps2 = cap2.get(cv2.CAP_PROP_FPS)

    # Use the smaller FPS to avoid frame mismatch
    fps = min(fps1, fps2)

    w1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    h1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
    h2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Determine resize dimensions (use smaller dimensions of both videos)
    new_w = min(w1, w2)
    new_h = min(h1, h2)

    # Determine the number of frames (use shorter video length)
    frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
    total_frames = min(frames1, frames2)

    # Define video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (new_w * 2, new_h))

    for i in range(total_frames):
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break

        # Resize frames
        frame1 = cv2.resize(frame1, (new_w, new_h))
        frame2 = cv2.resize(frame2, (new_w, new_h))

        # Concatenate horizontally
        combined = cv2.hconcat([frame1, frame2])

        out.write(combined)

    cap1.release()
    cap2.release()
    out.release()
    print(f"Output saved to {output_path}")

def get_most_recent_mp4(folder_path):
    folder = Path(folder_path)
    mp4_files = list(folder.glob("*.mp4"))
    
    if not mp4_files:
        return None  # No mp4 files found
    
    # Sort by modification time, newest last, take the last
    most_recent = max(mp4_files, key=lambda f: f.stat().st_mtime)
    return most_recent
    

# Example usage:
aria_video = get_most_recent_mp4("/home/reggev/shared/aria")
sensor_video = get_most_recent_mp4("/home/reggev/shared/sensor")
output_video = "/home/reggev/shared/output_combined.mp4"
combine_videos_side_by_side(aria_video, sensor_video, output_video)
