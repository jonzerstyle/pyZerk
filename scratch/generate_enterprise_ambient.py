import os
import sys
import numpy as np
import scipy.signal as signal
import soundfile as sf

def generate_enterprise_ambient():
    sample_rate = 44100
    duration = 30.0  # 30 seconds loop
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # Initialize stereo channels (Left, Right)
    left = np.zeros(num_samples, dtype=np.float64)
    right = np.zeros(num_samples, dtype=np.float64)
    
    # -------------------------------------------------------------
    # 1. Warp Core / Engine Low Drone (The classic 60s TOS hum)
    # Fundamental: 60.0 Hz with integer harmonics
    # -------------------------------------------------------------
    engine_lfo_freq = 1.20  # 1.20 Hz -> exactly 36 cycles in 30.0s
    throb_env = 1.0 + 0.32 * np.sin(2.0 * np.pi * engine_lfo_freq * t)
    
    # Subtle subharmonic wow/flutter
    flutter = 0.40 * np.sin(2.0 * np.pi * 0.60 * t)
    
    harmonics = [
        (60.0,  0.30),  # fundamental 60 Hz
        (120.0, 0.18),  # 2nd harmonic
        (180.0, 0.11),  # 3rd harmonic
        (240.0, 0.07),  # 4th harmonic
        (300.0, 0.04),  # 5th harmonic
        (360.0, 0.025), # 6th harmonic
        (480.0, 0.015), # 8th harmonic
    ]
    
    drone = np.zeros(num_samples, dtype=np.float64)
    for freq, amp in harmonics:
        phase = 2.0 * np.pi * freq * t + flutter * (freq / 60.0)
        drone += amp * np.sin(phase)
        
    drone *= throb_env
    left += drone * 0.95
    right += drone * 0.95
    
    # -------------------------------------------------------------
    # 2. Filtered Ventilation / Plasma Airflow (Warm Pink Noise)
    # -------------------------------------------------------------
    np.random.seed(1701)  # NCC-1701 seed!
    white_noise = np.random.normal(0, 1, num_samples)
    
    # Lowpass filter at 190 Hz to create deep resonant airflow
    b, a = signal.butter(3, 190.0 / (sample_rate / 2.0), btype='low')
    air_noise = signal.filtfilt(b, a, white_noise)
    air_noise = (air_noise / np.max(np.abs(air_noise))) * 0.12 * (0.85 + 0.15 * throb_env)
    
    # Slight stereo decorrelation for wide ambient atmosphere
    white_noise_r = np.random.normal(0, 1, num_samples)
    air_noise_r = signal.filtfilt(b, a, white_noise_r)
    air_noise_r = (air_noise_r / np.max(np.abs(air_noise_r))) * 0.12 * (0.85 + 0.15 * throb_env)
    
    left += air_noise
    right += air_noise_r
    
    # -------------------------------------------------------------
    # 3. Instrumentation Gyro / Bridge Singing Tone
    # -------------------------------------------------------------
    gyro_l = 0.014 * np.sin(2.0 * np.pi * 2400.0 * t)
    gyro_r = 0.014 * np.sin(2.0 * np.pi * 2404.0 * t)  # 4 Hz stereo beating
    left += gyro_l
    right += gyro_r
    
    # -------------------------------------------------------------
    # Helper for adding console beeps, warbles, and scanner chirps
    # -------------------------------------------------------------
    def add_tone(start_time, dur, freq, amp, pan=0.0, waveform='sine'):
        idx_start = int(start_time * sample_rate)
        n_samples = int(dur * sample_rate)
        if idx_start + n_samples >= num_samples:
            return
        
        t_tone = np.linspace(0, dur, n_samples, endpoint=False)
        
        if waveform == 'sine':
            wave = np.sin(2.0 * np.pi * freq * t_tone)
        elif waveform == 'triangle':
            wave = signal.sawtooth(2.0 * np.pi * freq * t_tone, width=0.5)
        elif waveform == 'soft_square':
            wave = np.sin(2.0 * np.pi * freq * t_tone) + 0.25 * np.sin(6.0 * np.pi * freq * t_tone)
        else:
            wave = np.sin(2.0 * np.pi * freq * t_tone)
            
        # Smooth envelope (fast raised-cosine attack, exponential decay)
        attack_len = min(int(0.012 * sample_rate), n_samples // 3)
        decay_len = n_samples - attack_len
        env = np.ones(n_samples)
        if attack_len > 0:
            env[:attack_len] = 0.5 * (1.0 - np.cos(np.pi * np.arange(attack_len) / attack_len))
        if decay_len > 0:
            env[attack_len:] = np.exp(-3.5 * np.linspace(0, 1, decay_len))
            
        tone_signal = wave * env * amp
        
        # Panning (-1.0 to 1.0)
        pan_left = np.cos((pan + 1.0) * np.pi / 4.0)
        pan_right = np.sin((pan + 1.0) * np.pi / 4.0)
        
        left[idx_start:idx_start+n_samples] += tone_signal * pan_left
        right[idx_start:idx_start+n_samples] += tone_signal * pan_right

    def add_fm_warble(start_time, dur, carrier, mod_freq, mod_depth, amp, pan=0.0):
        """Science station / Spock scanner warble."""
        idx_start = int(start_time * sample_rate)
        n_samples = int(dur * sample_rate)
        if idx_start + n_samples >= num_samples:
            return
        t_w = np.linspace(0, dur, n_samples, endpoint=False)
        fm_phase = 2.0 * np.pi * carrier * t_w + (mod_depth / mod_freq) * np.sin(2.0 * np.pi * mod_freq * t_w)
        wave = np.sin(fm_phase)
        
        # Gentle bell envelope
        attack = int(0.04 * sample_rate)
        decay = int(0.12 * sample_rate)
        env = np.ones(n_samples)
        if attack > 0:
            env[:attack] = np.linspace(0, 1, attack)
        if decay > 0:
            env[-decay:] = np.linspace(1, 0, decay)
            
        sig = wave * env * amp
        pan_l = np.cos((pan + 1.0) * np.pi / 4.0)
        pan_r = np.sin((pan + 1.0) * np.pi / 4.0)
        left[idx_start:idx_start+n_samples] += sig * pan_l
        right[idx_start:idx_start+n_samples] += sig * pan_r

    def add_nav_ping(start_time, freq=520.0, amp=0.10, pan=0.0):
        """Classic bridge sonar / navigational pulse with reverb tail."""
        dur = 1.2
        idx_start = int(start_time * sample_rate)
        n_samples = int(dur * sample_rate)
        if idx_start + n_samples >= num_samples:
            return
        t_p = np.linspace(0, dur, n_samples, endpoint=False)
        wave = np.sin(2.0 * np.pi * freq * t_p) + 0.3 * np.sin(2.0 * np.pi * (freq * 2.0) * t_p)
        env = np.exp(-4.2 * t_p)
        ping_sig = wave * env * amp
        
        # Add a subtle delayed echo (0.18s later)
        echo_delay = int(0.18 * sample_rate)
        echo_sig = np.zeros(n_samples)
        if echo_delay < n_samples:
            echo_sig[echo_delay:] = ping_sig[:-echo_delay] * 0.35
            
        total_ping = ping_sig + echo_sig
        pan_l = np.cos((pan + 1.0) * np.pi / 4.0)
        pan_r = np.sin((pan + 1.0) * np.pi / 4.0)
        left[idx_start:idx_start+n_samples] += total_ping * pan_l
        right[idx_start:idx_start+n_samples] += total_ping * pan_r

    # -------------------------------------------------------------
    # 4. Spock's Science Console / Scanner Warbles
    # -------------------------------------------------------------
    # Warble 1: at t = 2.6s (Left side science station)
    add_fm_warble(start_time=2.6, dur=0.75, carrier=980.0, mod_freq=8.5, mod_depth=160.0, amp=0.08, pan=-0.5)
    
    # Warble 2: at t = 11.2s (Two-tone scanner query)
    add_fm_warble(start_time=11.2, dur=0.55, carrier=860.0, mod_freq=10.0, mod_depth=140.0, amp=0.075, pan=-0.6)
    add_fm_warble(start_time=11.8, dur=0.60, carrier=1120.0, mod_freq=9.0, mod_depth=150.0, amp=0.07, pan=-0.4)
    
    # Warble 3: at t = 20.4s (Right side sensor readout)
    add_fm_warble(start_time=20.4, dur=0.85, carrier=1050.0, mod_freq=7.5, mod_depth=180.0, amp=0.08, pan=0.5)

    # -------------------------------------------------------------
    # 5. Bridge Computer Chatter & Console Blips (TOS Beeps)
    # -------------------------------------------------------------
    # Burst 1: t = 4.8s (Helm / Navigation console)
    add_tone(start_time=4.80, dur=0.08, freq=1200.0, amp=0.07, pan=0.3)
    add_tone(start_time=4.92, dur=0.08, freq=1600.0, amp=0.07, pan=0.4)
    add_tone(start_time=5.04, dur=0.10, freq=2000.0, amp=0.08, pan=0.3)

    # Burst 2: t = 7.5s (Communication station chirp)
    add_tone(start_time=7.50, dur=0.09, freq=880.0, amp=0.065, pan=0.7)
    add_tone(start_time=7.62, dur=0.12, freq=1320.0, amp=0.07, pan=0.75)

    # Navigational Ping 1: t = 8.8s
    add_nav_ping(start_time=8.8, freq=520.0, amp=0.09, pan=0.15)

    # Burst 3: t = 14.2s (Library computer calculation)
    add_tone(start_time=14.20, dur=0.07, freq=1440.0, amp=0.06, pan=-0.3)
    add_tone(start_time=14.30, dur=0.07, freq=1080.0, amp=0.06, pan=-0.2)
    add_tone(start_time=14.40, dur=0.09, freq=1800.0, amp=0.07, pan=-0.4)
    add_tone(start_time=14.52, dur=0.11, freq=1350.0, amp=0.065, pan=-0.3)

    # Burst 4: t = 17.0s (Main viewer sensor blip)
    add_tone(start_time=17.00, dur=0.08, freq=2160.0, amp=0.06, pan=0.1)
    add_tone(start_time=17.10, dur=0.10, freq=1620.0, amp=0.065, pan=0.1)

    # Navigational Ping 2: t = 22.8s
    add_nav_ping(start_time=22.8, freq=520.0, amp=0.09, pan=-0.15)

    # Burst 5: t = 24.6s (Engineering status blips)
    add_tone(start_time=24.60, dur=0.07, freq=960.0, amp=0.065, pan=-0.7)
    add_tone(start_time=24.70, dur=0.08, freq=1280.0, amp=0.07, pan=-0.6)
    add_tone(start_time=24.82, dur=0.12, freq=1600.0, amp=0.075, pan=-0.7)

    # Burst 6: t = 27.5s (Science console query)
    add_tone(start_time=27.50, dur=0.08, freq=1750.0, amp=0.06, pan=-0.4)
    add_tone(start_time=27.60, dur=0.10, freq=2100.0, amp=0.065, pan=-0.5)

    # -------------------------------------------------------------
    # 6. Perfect Equal-Power Loop Crossfade (1.2 seconds)
    # -------------------------------------------------------------
    xfade_samples = int(1.2 * sample_rate)
    fade_out = np.cos(0.5 * np.pi * np.linspace(0, 1, xfade_samples))
    fade_in = np.sin(0.5 * np.pi * np.linspace(0, 1, xfade_samples))
    
    # Smooth start and end crossfade so looping is 100% seamless
    tail_l = left[-xfade_samples:].copy()
    tail_r = right[-xfade_samples:].copy()
    head_l = left[:xfade_samples].copy()
    head_r = right[:xfade_samples].copy()
    
    left[:xfade_samples] = head_l * fade_in + tail_l * fade_out
    right[:xfade_samples] = head_r * fade_in + tail_r * fade_out
    left[-xfade_samples:] = left[:xfade_samples]
    right[-xfade_samples:] = right[:xfade_samples]

    # Combine into stereo array
    stereo = np.column_stack((left, right))
    
    # Normalize peak to -1.0 dBFS (approx 0.89)
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo = (stereo / peak) * 0.89
        
    print(f"Synthesized {duration}s Star Trek TOS ambient sound! Peak: {np.max(np.abs(stereo)):.3f}")
    return stereo, sample_rate

if __name__ == "__main__":
    audio, sr = generate_enterprise_ambient()
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sounds"))
    ogg_path = os.path.join(out_dir, "BMUSIC.ogg")
    wav_path = os.path.join(out_dir, "BMUSIC.wav")
    
    sf.write(ogg_path, audio, sr, format='OGG', subtype='VORBIS')
    sf.write(wav_path, audio, sr, format='WAV', subtype='PCM_16')
    print(f"Saved: {ogg_path}")
    print(f"Saved: {wav_path}")
