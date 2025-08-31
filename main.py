import asyncio
import utils    
import argparse
import aria.sdk as aria

async def main():
    await asyncio.gather(
        utils.record_aria_video("132.69.205.31", 10, "profile0"),
        utils.record_sensor_video()
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record Aria video with optional length.")
    parser.add_argument("--length", type=int, default=10, help="Recording length in seconds")
    args = parser.parse_args()

    asyncio.run(main())
    utils.pull_recordings()
