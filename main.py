import asyncio
import utils    
import argparse
import aria.sdk as aria
from vrs_to_video import VRSToVideo
from pathlib import Path
import time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record Aria video with optional length.")
    parser.add_argument("--length", type=int, default=10, help="Recording length in seconds")
    args = parser.parse_args()

    aria_ip = '132.69.202.2'

    device = utils.prepare_aria_video(device_ip=aria_ip)
    sensor = utils.SensorSocket(host="132.68.54.35", port=12345)
    sensor.connect()
    sensor.prepare()
    aria_start_time = utils.start_aria_recording(device)
    sensor.start()
    time.sleep(args.length)
    sensor.stop()
    sensor_start_time, duration = sensor.get_recording_time()
    sensor.pull()
    sensor.close()

    print(f"Recording started at {start_time} for duration {duration} seconds")

    utils.pull_aria_recording()
    # VRSToVideo(Path('/home/reggev/shared/aria'))