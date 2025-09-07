import aria.sdk as aria
import asyncio
import subprocess
import time
import socket
from datetime import datetime
from pathlib import Path


class SensorSocket:
    def __init__(self, host='132.68.54.35', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._state = 'DISCONNECTED'

    def _set_state(self, new_state):
        print(f"[SNSR] State changed: {self._state} -> {new_state}")
        self._state = new_state

    @property
    def state(self):
        return self._state

    def receive(self, bufsize=1024):
        data = self.socket.recv(bufsize)
        return data

    def connect(self):
        self.socket.connect((self.host, self.port))
        self._set_state('CONNECTED')

    def prepare(self):
        if self.state != 'CONNECTED':
            raise Exception("Socket not connected")
        self.socket.sendall(b'PREPARE')
        response = self.receive(1024)
        if response == b'PREPARED':
            self._set_state('PREPARED')
        else:
            raise Exception("Failed to prepare sensor")

    def start(self):
        if self.state != 'PREPARED':
            raise Exception("Socket not prepared")
        self.socket.sendall(b'START')
        response = self.receive(1024)
        if response == b'STARTED':
            self._set_state('RECORDING')
            return time.time()
        else:
            raise Exception("Failed to start sensor recording")

    def stop(self):
        if self.state != 'RECORDING':
            raise Exception("Socket not recording")
        self.socket.sendall(b'STOP')
        response = self.receive(1024)
        if response == b'STOPPED':
            self._set_state('STOPPED')
            return time.time()
        else:
            raise Exception("Failed to stop sensor recording")

    def get_recording_time(self):
        self.socket.sendall(b'TIME')
        response = self.receive(1024)
        # Expecting response as "start_time,length" (both floats)
        try:
            start_time_str, length_str, unix_time, up_time = response.decode().split(',')
            return float(start_time_str), float(length_str), float(unix_time), float(up_time)
        except Exception as e:
            raise Exception(f"Invalid response from sensor: {response}") from e
        
    def pull(self):
        self.socket.sendall(b'PULL')
        response = self.receive(1024)
        if response != b'ERROR':
            print("[SNSR] Data pulled successfully")
            return response.decode()  # Assuming response is the path to the pulled data``
        else:
            raise Exception("Failed to pull data from sensor")
        
    def close(self):
        self.socket.close()


def get_aria_ip(sensor_ip):
    try:
        result = subprocess.check_output(['ssh', sensor_ip, 'source ~/.bashrc && aria-ip']).decode().strip()
        return result
    except subprocess.CalledProcessError as e:
        print(f"Failed to get Aria IP: {e}")
        return None

def prepare_aria_video(device_ip, profile=None):
    #  Optional: Set SDK's log level to Trace or Debug for more verbose logs. Defaults to Info
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Initializing Aria...")
    # aria.set_log_level(aria.Level.Info)
    
    device_client = aria.DeviceClient()

    client_config = aria.DeviceClientConfig()
    client_config.ip_v4_address = device_ip
    device_client.set_client_config(client_config)

    device = device_client.connect()

    recording_manager = device.recording_manager
    recording_config = aria.RecordingConfig()
    if profile:
        recording_config.profile_name = profile
    else:
        # Apply your settings
        recording_config.rgb_camera.enabled = True
        recording_config.rgb_camera.width = 1408
        recording_config.rgb_camera.height = 1408
        recording_config.rgb_camera.fps = 20
        recording_config.rgb_camera.image_format = aria.ImageFormat.JPEG
        recording_config.rgb_camera.jpeg_quality = 80

        # Disable other sensors
        recording_config.imu1.enabled = False
        recording_config.imu2.enabled = False
        recording_config.audio.enabled = False
        recording_config.magnetometer.enabled = False
        recording_config.barometer.enabled = False
        recording_config.gps.enabled = False
        recording_config.ble.enabled = False
        recording_config.wifi.enabled = False
        recording_config.et_camera.enabled = False
        recording_config.slam_cameras.enabled = False
    # recording_config.time_sync_mode = aria.TimeSyncMode.Ntp
    recording_manager.recording_config = recording_config
    return device, device_client

def start_aria_recording(device):
    recording_manager = device.recording_manager
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Sending Record command...")
    recording_manager.start_recording()
    start_time = time.time()
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Record started...")
    return start_time

def stop_aria_recording(device):
    recording_manager = device.recording_manager
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Sending Stop command...")
    recording_manager.stop_recording()
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Record stopped...")
    stop_time = time.time()
    return stop_time

def disconnect_aria(device_client,device):
    device_client.disconnect(device)
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Disconnected from Aria device.")
    
def pull_aria_recording():
    host = "132.68.54.35"
    script_path = "/home/reggev/video_transfer_aria.sh"
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Pulling recordings from Aria device...")
    try:
        subprocess.run(
            ["ssh", host, script_path],
            check=True
        )
        print(f"[ARIA] {time.strftime('%H:%M:%S')} Video transfer script executed successfully.")
        folder = Path('/home/reggev/shared/aria')
        file = [f for f in folder.iterdir() if f.suffix == '.vrs']
        most_recent_file = max(file, key=lambda x: x.stat().st_mtime)   
        return most_recent_file
    except subprocess.CalledProcessError as e:
        print(f"[ARIA] {time.strftime('%H:%M:%S')} Failed to execute video transfer script: {e}")
    


