import asyncio
import utils    
import argparse
import aria as aaaa
import aria.sdk as aria
from vrs_to_video import VRSToVideo
from pathlib import Path
import time

class OutputObject():
    def __init__(self,context,chat_id):
        self.context = context
        self.chat_id = chat_id

    async def print(self,message):
        print(message)
        if self.context is not None:
            await self.context.bot.send_message(chat_id=self.chat_id, text=message)

async def main(context=None,chat_id=None):
    out = OutputObject(context,chat_id)
    parser = argparse.ArgumentParser(description="Record Aria video with optional length.")
    parser.add_argument("--length", type=int, default=10, help="Recording length in seconds")
    parser.add_argument("--aria-ip", type=str, default="132.69.202.144", help="Aria device IP address")
    parser.add_argument("--sensor-ip", type=str, default="132.69.205.22", help="Sensor device IP address")
    args = parser.parse_args()

    sensor_ip = args.sensor_ip
    # try:
    #     aria_ip = utils.get_aria_ip(sensor_ip)
    #     if aria_ip is None:
    #         aria_ip = args.aria_ip
    # except:
    #     await out.print("[MAIN] Glasses might be disconnected from Jetson. Using default Aria IP.")
    #     aria_ip = args.aria_ip

    # await out.print(f"[MAIN] Preparing to record {args.length} seconds of video from Aria at {aria_ip} and sensor at {sensor_ip}")
    await out.print(f"[MAIN] Preparing to record {args.length} seconds of video from sensor at {sensor_ip}")
    # await out.print(f"[MAIN] Make sure Aria is in the same network as this computer and the sensor")
    # await out.print(f"[MAIN] Preparing Aria...")
    # device, device_client = utils.prepare_aria_video(device_ip=aria_ip,profile='profile5')
    await out.print(f"[MAIN] Preparing Sensor...")
    sensor = utils.SensorSocket(host=sensor_ip, port=12345)
    sensor.connect()
    sensor.prepare()
    await out.print(f"[MAIN] Starting recording for {args.length} seconds...")
    # aria_start_time = utils.start_aria_recording(device) - 0.2
    # await out.print(f"[MAIN] Aria recording started at {aria_start_time}")
    _ = sensor.start()
    await out.print(f"[MAIN] Sensor recording started at {time.time()}")
    await out.print(f"[MAIN] Waiting for {args.length} seconds...")
    time.sleep(args.length)
    await out.print(f"[MAIN] Sending stop command at {time.time()}")
    _ = sensor.stop()
    await out.print(f"[MAIN] Sensor recording stopped at {time.time()}")
    # aria_stop_time = utils.stop_aria_recording(device)
    # await out.print(f"[MAIN] Aria recording stopped at {aria_stop_time}")
    print(time.time())
    # lab_unix_time_sample = time.time()
    sensor_start_time, sensor_end_time, _, _ = sensor.get_recording_time()
    await out.print(f"[MAIN] Pulling video from sensor...")
    sensor_video_path = sensor.pull()
    await out.print('[MAIN] Closing sensor connection...')
    sensor.close()
    # await out.print(f"[MAIN] Disconnecting from Aria...")
    # utils.disconnect_aria(device_client,device)
    # await out.print(f"[MAIN] Pulling video from Aria...")
    # aria_video_path = utils.pull_aria_recording(sensor_ip)
    # await out.print(f"[MAIN] Converting Aria VRS to MP4...")
    # VRSToVideo(Path(aria_video_path),
    #             sensor_start_time=sensor_start_time,
    #             sensor_end_time=sensor_end_time,
    #             aria_start_time=aria_start_time,
    #             aria_end_time=aria_stop_time)

    # await out.print(f"[MAIN] Aria recording from {aria_start_time} to {aria_stop_time}, duration {aria_stop_time - aria_start_time} seconds")
    await out.print(f"[MAIN] Sensor recording started at {sensor_start_time} to {sensor_end_time}, duration {sensor_end_time - sensor_start_time} seconds")
    await out.print(f"[MAIN] All done!")


if __name__ == "__main__":
    asyncio.run(main())