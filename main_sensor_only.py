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

async def main(context=None,chat_id=None,duration=10,aria_ip="132.69.202.144",sensor_ip="132.69.205.22"):
    out = OutputObject(context,chat_id)

    await out.print(f"[MAIN] Preparing to record {duration} seconds of video from sensor at {sensor_ip}")
    await out.print(f"[MAIN] Preparing Sensor...")
    sensor = utils.SensorSocket(host=sensor_ip, port=12345)
    sensor.connect()
    sensor.prepare()
    await out.print(f"[MAIN] Starting recording for {duration} seconds...")
    _ = sensor.start()
    await out.print(f"[MAIN] Sensor recording started at {time.time()}")
    await out.print(f"[MAIN] Waiting for {duration} seconds...")
    time.sleep(duration)
    await out.print(f"[MAIN] Sending stop command at {time.time()}")
    _ = sensor.stop()
    await out.print(f"[MAIN] Sensor recording stopped at {time.time()}")
    print(time.time())
    sensor_start_time, sensor_end_time, _, _ = sensor.get_recording_time()
    await out.print(f"[MAIN] Pulling video from sensor...")
    _ = sensor.pull()
    await out.print('[MAIN] Closing sensor connection...')
    sensor.close()
    await out.print(f"[MAIN] Sensor recording started at {sensor_start_time} to {sensor_end_time}, duration {sensor_end_time - sensor_start_time} seconds")
    await out.print(f"[MAIN] All done!")


if __name__ == "__main__":
    asyncio.run(main())