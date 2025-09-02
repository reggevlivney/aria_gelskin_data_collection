import aria.sdk as aria
import asyncio
import subprocess
import time
import socket

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
        else:
            raise Exception("Failed to start sensor recording")

    def stop(self):
        if self.state != 'RECORDING':
            raise Exception("Socket not recording")
        self.socket.sendall(b'STOP')
        response = self.receive(1024)
        if response == b'STOPPED':
            self._set_state('STOPPED')
        else:
            raise Exception("Failed to stop sensor recording")

    def get_recording_time(self):
        self.socket.sendall(b'TIME')
        response = self.receive(1024)
        # Expecting response as "start_time,length" (both floats)
        try:
            start_time_str, length_str = response.decode().split(',')
            return float(start_time_str), float(length_str)
        except Exception as e:
            raise Exception(f"Invalid response from sensor: {response}") from e
        
    def pull(self):
        self.socket.sendall(b'PULL')
        response = self.receive(1024)
        if response == b'SENT':
            print("[SNSR] Data pulled successfully")
        else:
            raise Exception("Failed to pull data from sensor")
        
    def close(self):
        self.socket.close()


def prepare_aria_video(device_ip, recording_duration=10, profile='profile0'):
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

    return device

def start_aria_recording(device):
    recording_manager = device.recording_manager
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Sending Record command...")
    recording_manager.start_recording()
    start_time = time.time()
    print(f"[ARIA] {time.strftime('%H:%M:%S')} Record started...")
    return start_time


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
    except subprocess.CalledProcessError as e:
        print(f"[ARIA] {time.strftime('%H:%M:%S')} Failed to execute video transfer script: {e}")
    




