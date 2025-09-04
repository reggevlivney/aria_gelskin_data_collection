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
    parser.add_argument("--aria-ip", type=str, default="132.69.202.74", help="Aria device IP address")
    parser.add_argument("--sensor-ip", type=str, default="132.68.54.35", help="Sensor device IP address")
    args = parser.parse_args()

    sensor_ip = args.sensor_ip
    try:
        aria_ip = utils.get_aria_ip(sensor_ip)
        if aria_ip is None:
            aria_ip = args.aria_ip
    except:
        aria_ip = args.aria_ip

    print(f"[MAIN] Preparing to record {args.length} seconds of video from Aria at {aria_ip} and sensor at {sensor_ip}")
    print(f"[MAIN] Make sure Aria is in the same network as this computer and the sensor")
    print(f"[MAIN] Preparing Aria...")
    device, device_client = utils.prepare_aria_video(device_ip=aria_ip,profile='profile5')
    print(f"[MAIN] Preparing Sensor...")
    sensor = utils.SensorSocket(host=sensor_ip, port=12345)
    sensor.connect()
    sensor.prepare()
    print(f"[MAIN] Starting recording for {args.length} seconds...")
    aria_start_time = utils.start_aria_recording(device)
    print(f"[MAIN] Aria recording started at {aria_start_time}")
    sensor.start()
    print(f"[MAIN] Sensor recording started at {time.time()}")
    print(f"[MAIN] Waiting for {args.length} seconds...")
    time.sleep(args.length)
    print(f"[MAIN] Sending stop command at {time.time()}")
    sensor.stop()
    print(f"[MAIN] Sensor recording stopped at {time.time()}")
    aria_stop_time = utils.stop_aria_recording(device)
    print(f"[MAIN] Aria recording stopped at {aria_stop_time}")
    sensor_start_time, sensor_duration, sync_data = sensor.get_recording_time()
    print(f"[MAIN] Pulling video from sensor...")
    sensor.pull()
    print('[MAIN] Closing sensor connection...')
    sensor.close()
    print(f"[MAIN] Disconnecting from Aria...")
    utils.disconnect_aria(device_client,device)
    print(f"[MAIN] Pulling video from Aria...")
    utils.pull_aria_recording()
    print(f"[MAIN] Converting Aria VRS to MP4...")
    VRSToVideo(Path('/home/reggev/shared/aria'))

    print(f"[MAIN] Aria recording from {aria_start_time} to {aria_stop_time}, duration {aria_stop_time - aria_start_time} seconds")
    print(f"[MAIN] Sensor recording started at {sensor_start_time} for duration {sensor_duration} seconds")
    print(f"[MAIN] All done!")
