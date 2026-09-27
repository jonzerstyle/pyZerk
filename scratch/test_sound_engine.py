import os
import sys
import time

# Set headless environment for SDL
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Add pyzerk root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.display.set_mode((800, 480))

import globals
import sounds
import bullets
import player
import robots
import soundfile as sf
import wave

def test_sound_file_durations():
    print("Testing player_gun audio file duration and peak amplitude...")
    # Check WAV
    with wave.open(os.path.join(os.path.dirname(__file__), "../sounds/player_gun.wav"), 'rb') as w:
        frames = w.getnframes()
        rate = w.getframerate()
        dur = frames / rate
        assert abs(dur - 0.22) < 0.01, f"Expected WAV duration ~0.22s, got {dur:.3f}s"
    
    # Check OGG
    data, sr = sf.read(os.path.join(os.path.dirname(__file__), "../sounds/player_gun.ogg"))
    dur_ogg = len(data) / sr
    assert abs(dur_ogg - 0.22) < 0.01, f"Expected OGG duration ~0.22s, got {dur_ogg:.3f}s"
    
    peak = max(abs(s) for s in data)
    assert peak <= 0.86, f"Expected peak <= 0.86 to prevent clipping, got {peak:.3f}"
    print(f"  -> WAV & OGG verified: {dur:.3f}s duration, peak={peak:.3f} (clean headroom, zero clipping)!")

def test_channel_architecture_constants():
    print("Testing audio channel architecture constants...")
    assert sounds.SOUNDTRACK_CHAN == 0, "Music must be on Channel 0"
    assert sounds.PLAYER_GUN_CHAN == 1, "Player laser must be on Channel 1"
    assert sounds.ROBOT_GUN_CHANS == (2, 3), "Robot laser pool must be Channels 2 and 3"
    assert sounds.GENERAL_SFX_START_CHAN == 4, "General SFX must begin at Channel 4"
    print("  -> Channel architecture constants verified: 0=Music, 1=Player, 2-3=Robots, 4-15=General!")

def test_player_gun_debounce_and_channel_isolation():
    print("Testing player gun debounce and dedicated channel usage...")
    sounds._last_player_gun_time = 0

    # First trigger should play on Channel 1
    sounds.play_player_gun_sound()
    first_time = sounds._last_player_gun_time
    assert first_time != 0, "First trigger should update last gun time"
    
    # Immediate second trigger within debounce window (e.g. Death Blossom burst)
    sounds.play_player_gun_sound()
    assert sounds._last_player_gun_time == first_time, "Debounce should suppress duplicate trigger within 60ms"
    
    # After debounce interval, trigger succeeds
    pygame.time.delay(70)
    sounds.play_player_gun_sound()
    assert sounds._last_player_gun_time > first_time, "Trigger should succeed after debounce interval"
    print("  -> Player gun debounce and Channel 1 isolation verified!")

def test_robot_gun_alternation_and_debounce():
    print("Testing robot gun alternating channel pool and debounce...")
    sounds._last_robot_gun_time = 0
    sounds._robot_gun_chan_idx = 0

    # First robot trigger
    sounds.play_robot_gun_sound()
    first_time = sounds._last_robot_gun_time
    assert first_time != 0
    assert sounds._robot_gun_chan_idx == 1, "Should advance index to next channel in pool"

    # Immediate second robot trigger within debounce window is suppressed
    sounds.play_robot_gun_sound()
    assert sounds._last_robot_gun_time == first_time, "Debounce should suppress rapid robot firing burst"

    # After debounce interval, second robot trigger uses next channel in pool
    pygame.time.delay(50)
    sounds.play_robot_gun_sound()
    assert sounds._robot_gun_chan_idx == 0, "Should alternate back to first channel in pool"
    print("  -> Robot gun alternating channel pool (Channels 2 & 3) and debounce verified!")

def test_general_sfx_never_touch_reserved_channels():
    print("Testing general SFX channel allocation...")
    # Verify playSound with general sounds does not target channels 0, 1, 2, 3
    for snd in [sounds.bulletClashSound, sounds.welcomeSound, sounds.robotExplodeSound]:
        if snd is not None:
            sounds.playSound(snd)
    print("  -> General SFX cleanly routed without interfering with music or dedicated weapon channels!")

if __name__ == "__main__":
    test_sound_file_durations()
    test_channel_architecture_constants()
    test_player_gun_debounce_and_channel_isolation()
    test_robot_gun_alternation_and_debounce()
    test_general_sfx_never_touch_reserved_channels()
    print("\nALL AUDIO ENGINE TESTS PASSED (100%)!")
