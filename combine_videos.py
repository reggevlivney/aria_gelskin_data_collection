import cv2

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


# Example usage:
combine_videos_side_by_side("/home/reggev/shared/aria/aria_2025-09-10-16-59-44.mp4",
                             "/home/reggev/shared/sensor/sensor_2025-09-10-16-59-14.mp4",
                               "/home/reggev/shared/output_1.mp4")
