import aria.sdk as aria
import asyncio
import subprocess
import time
import socket

def record_aria_video(device_ip, recording_duration=10, profile='profile0'):
    #  Optional: Set SDK's log level to Trace or Debug for more verbose logs. Defaults to Info
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Initializing Aria...")
    aria.set_log_level(aria.Level.Info)
    
    device_client = aria.DeviceClient()

    client_config = aria.DeviceClientConfig()
    client_config.ip_v4_address = device_ip
    device_client.set_client_config(client_config)

    device = device_client.connect()

    recording_manager = device.recording_manager

    recording_config = aria.RecordingConfig()
    recording_config.profile_name = profile
    recording_manager.recording_config = recording_config

    print(f"[ARIA] {time.strftime('%H:%M:%S')} Sending Record command...")

    recording_manager.start_recording()

    print(f"[ARIA] {time.strftime('%H:%M:%S')} Record started...")

    recording_state = recording_manager.recording_state
    # print(f"Recording state: {recording_state}")

    time.sleep(recording_duration)

    recording_manager.stop_recording()
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Took a {recording_duration}-second long recording.")

    device_client.disconnect(device)


def pull_recordings():
    host = "132.68.54.35"
    script_path = "/home/reggev/video_transfer_aria.sh"
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Pulling recordings from Aria device...")
    try:
        subprocess.run(
            ["ssh", host, script_path],
            check=True
        )
        print(f"[ARIA] {time.strftime('%H:%M:%S')} Video transfer script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ARIA] {time.strftime('%H:%M:%S')} Failed to execute video transfer script: {e}")
    
    script_path = "/home/reggev/video_transfer_sensor.sh"
    print(f"[SNSR] {time.strftime('%H:%M:%S')} Pulling recordings from Sensor...")
    try:
        subprocess.run(
            ["ssh", host, script_path],
            check=True
        )
        print(f"[SNSR] {time.strftime('%H:%M:%S')} Video transfer script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[SNSR] {time.strftime('%H:%M:%S')} Failed to execute video transfer script: {e}")


def record_sensor_video():
    host = "132.68.54.35"
    cmd = [
        "ssh",
        host,
        "OPENBLAS_CORETYPE=ARMV8",
        "python3",
        "/home/reggev/Documents/projects/intro_project/camera_record.py",
        "--length",
        "10"
    ]
    print(f"[SNSR] {time.strftime('%H:%M:%S')} Sending command to record sensor video...")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print(f"[SNSR] {time.strftime('%H:%M:%S')} Sensor video recording completed successfully.")
        print(stdout.decode())
    else:
        print(f"[SNSR] {time.strftime('%H:%M:%S')} Sensor video recording failed with code {process.returncode}.")
        print(stderr.decode())


