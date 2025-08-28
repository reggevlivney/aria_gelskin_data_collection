import aria.sdk as aria
import time

def record_aria_video(device_ip, recording_duration=10, profile='profile0'):
    #  Optional: Set SDK's log level to Trace or Debug for more verbose logs. Defaults to Info
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

    print(
        f"Starting to record using {args.profile_name} for {args.recording_duration} seconds"
    )
    recording_manager.start_recording()

    recording_state = recording_manager.recording_state
    print(f"Recording state: {recording_state}")

    time.sleep(recording_duration)

    recording_manager.stop_recording()
    print(f"Took a {args.recording_duration}-second long recording.")

    device_client.disconnect(device)


if __name__ == "__main__":
    record_aria_video("132.69.202.247", 10, "profile0")
