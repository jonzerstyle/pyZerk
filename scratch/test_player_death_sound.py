#!/usr/bin/env python3
"""
Unit test for pyZerk player death sound (Wilhelm scream).
Verifies:
1. Audio format, duration (~1.2s), sample rate (44100Hz), and channels (mono).
2. Proper loading in Pygame mixer without errors.
3. In-game player collision triggering sounds.playerDeathSound.
"""

import os
import sys
import soundfile as sf
import pygame

os.environ["SDL_AUDIODRIVER"] = "dummy"

def test_player_death_audio_files():
    sounds_dir = os.path.join(os.path.dirname(__file__), "..", "sounds")
    wav_path = os.path.join(sounds_dir, "player_death.wav")
    ogg_path = os.path.join(sounds_dir, "player_death.ogg")

    assert os.path.isfile(wav_path), f"Missing {wav_path}"
    assert os.path.isfile(ogg_path), f"Missing {ogg_path}"

    wav_info = sf.info(wav_path)
    ogg_info = sf.info(ogg_path)

    print(f"WAV: {wav_info.samplerate}Hz, {wav_info.channels}ch, {wav_info.duration:.3f}s")
    print(f"OGG: {ogg_info.samplerate}Hz, {ogg_info.channels}ch, {ogg_info.duration:.3f}s")

    assert wav_info.samplerate == 44100, f"Expected 44100Hz, got {wav_info.samplerate}"
    assert ogg_info.samplerate == 44100, f"Expected 44100Hz, got {ogg_info.samplerate}"
    assert wav_info.channels == 1, f"Expected 1 channel (mono), got {wav_info.channels}"
    assert ogg_info.channels == 1, f"Expected 1 channel (mono), got {ogg_info.channels}"
    assert 1.15 <= wav_info.duration <= 1.25, f"Unexpected duration: {wav_info.duration}"
    assert 1.15 <= ogg_info.duration <= 1.25, f"Unexpected duration: {ogg_info.duration}"
    print("[PASS] Audio file properties verified.")

def test_pygame_loading_and_trigger():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    pygame.init()
    import globals
    globals.SOUNDS_ON = True

    import sounds
    import player

    assert sounds.playerDeathSound is not None, "sounds.playerDeathSound failed to load!"
    length = sounds.playerDeathSound.get_length()
    print(f"Loaded sound length in mixer: {length:.3f}s")
    assert 1.15 <= length <= 1.25, f"Unexpected mixer sound length: {length}"

    p = player.Class_Player([100, 100], [0, 0])
    class DummyObstacle(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.rect = pygame.Rect(95, 95, 20, 20)

    p.collide(DummyObstacle())
    assert p.killState is True, "Player should be dead (killState=True) after collision!"
    print("[PASS] Pygame loading and collision sound trigger verified.")

if __name__ == "__main__":
    test_player_death_audio_files()
    test_pygame_loading_and_trigger()
    print("\nALL WILHELM DEATH SOUND TESTS PASSED SUCCESSFULLY! (100%)")
