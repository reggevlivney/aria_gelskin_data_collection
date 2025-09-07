import cv2
from pathlib import Path


if __name__ == "__main__":
    aria_video_path = Path('/home/reggev/shared/aria/aria_2025-09-07-12-40-47.mp4')
    sensor_video_path = Path('/home/reggev/shared/sensor/sensor_2025-09-07-12-40-23.mp4')

    aria_cap = cv2.VideoCapture(str(aria_video_path))
    sensor_cap = cv2.VideoCapture(str(sensor_video_path))

    ind_aria = 33
    ind_sensor = 30
    # ind_aria = 0
    # ind_sensor = 0

    for _ in range(1):
        # ind_aria += 1
        # ind_sensor += 1
        aria_cap.set(cv2.CAP_PROP_POS_FRAMES, ind_aria)
        ret_aria, frame_aria = aria_cap.read()
        sensor_cap.set(cv2.CAP_PROP_POS_FRAMES, ind_sensor)
        ret_sensor, frame_sensor = sensor_cap.read()
        print(ind_aria, ind_sensor)
        cv2.imshow('Aria Frame', cv2.resize(frame_aria,(640,480)))
        cv2.imshow('Sensor Frame', cv2.resize(frame_sensor,(640,480)))
        cv2.waitKey(0)
        pass