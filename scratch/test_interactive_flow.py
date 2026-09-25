import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import main
import globals

async def simulate_interactive_flow():
    print("Testing simulated interactive loop...")
    # Start main() task
    task = asyncio.create_task(main.main())
    
    # Wait for menu to boot up
    await asyncio.sleep(0.1)
    assert globals.MENUON == True, "Game should boot into Start Menu"
    print("  -> Game booted into Start Menu: globals.MENUON == True")
    
    # Simulate pressing '1' to start the game
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
    await asyncio.sleep(0.2)
    assert globals.MENUON == False, "Game should start: globals.MENUON == False"
    print("  -> Game started via '1': globals.MENUON == False")
    
    # Play for a few frames
    await asyncio.sleep(0.2)
    
    # Simulate pressing Enter while in-game to return to menu
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    await asyncio.sleep(0.2)
    assert globals.MENUON == True, "Hitting Enter should return to Start Menu"
    print("  -> Returned to Start Menu on Enter: globals.MENUON == True")
    
    # Simulate pressing Enter again to start a new game
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    await asyncio.sleep(0.2)
    assert globals.MENUON == False, "Hitting Enter on Option 1.0 starts new game"
    print("  -> Restarted game from menu: globals.MENUON == False")
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("  -> Interactive loop completed cleanly!")

if __name__ == "__main__":
    asyncio.run(simulate_interactive_flow())
    print("\nSIMULATED INTERACTIVE FLOW COMPLETED SUCCESSFULLY!")
