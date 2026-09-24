import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import main

async def test_run():
    print("Starting test_run()...")
    task = asyncio.create_task(main.main())
    await asyncio.sleep(1.0)
    print("Game ran for 1 second successfully!")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Test run completed cleanly with zero exceptions!")

if __name__ == "__main__":
    asyncio.run(test_run())
