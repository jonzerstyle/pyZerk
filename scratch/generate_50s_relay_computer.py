import os
import sys
import numpy as np
import scipy.signal as signal
import soundfile as sf

def synthesize_relay_click(relay_type='medium', sample_rate=44100):
    """Synthesize a single physical mechanical relay click."""
    dur = 0.045  # 45ms duration
    num_pts = int(dur * sample_rate)
    t = np.linspace(0, dur, num_pts, endpoint=False)
    
    if relay_type == 'light':
        # Fast, sharp, miniature signal relay
        f_res1, f_res2, f_res3 = 3400.0, 4800.0, 6200.0
        thump_f = 240.0
        decay_time = 0.002
        noise_weight = 0.45
        bounce_gap = 0.007
        bounce_amp = 0.35
    elif relay_type == 'heavy':
        # Large solenoid / power relay with substantial frame resonance
        f_res1, f_res2, f_res3 = 1400.0, 2200.0, 3100.0
        thump_f = 130.0
        decay_time = 0.005
        noise_weight = 0.35
        bounce_gap = 0.012
        bounce_amp = 0.45
    elif relay_type == 'stepper':
        # Rotary / stepping switch with distinct mechanical latch
        f_res1, f_res2, f_res3 = 1900.0, 2800.0, 4200.0
        thump_f = 170.0
        decay_time = 0.004
        noise_weight = 0.40
        bounce_gap = 0.010
        bounce_amp = 0.50
    else:  # 'medium'
        # Standard telephone / logic relay
        f_res1, f_res2, f_res3 = 2400.0, 3600.0, 5000.0
        thump_f = 180.0
        decay_time = 0.003
        noise_weight = 0.40
        bounce_gap = 0.009
        bounce_amp = 0.40

    # 1. Armature metallic impact strike
    impact_wave = (
        0.50 * np.sin(2.0 * np.pi * f_res1 * t) +
        0.35 * np.sin(2.0 * np.pi * f_res2 * t) +
        0.20 * np.sin(2.0 * np.pi * f_res3 * t)
    ) * np.exp(-t / decay_time)
    
    # 2. High-frequency friction / contact spark noise burst
    noise = np.random.normal(0, 1, num_pts)
    b_n, a_n = signal.butter(2, [1800.0 / (sample_rate / 2.0), 7500.0 / (sample_rate / 2.0)], btype='band')
    filt_noise = signal.filtfilt(b_n, a_n, noise)
    noise_env = np.exp(-t / (decay_time * 0.7))
    impact_noise = filt_noise * noise_env
    
    # 3. Solenoid electromagnetic thump
    thump = 0.45 * np.sin(2.0 * np.pi * thump_f * t) * np.exp(-t / 0.010)
    
    # Primary click
    primary = (1.0 - noise_weight) * impact_wave + noise_weight * impact_noise + thump
    
    # 4. Contact bounce (secondary lighter click as spring settles)
    bounce_idx = int(bounce_gap * sample_rate)
    bounce = np.zeros(num_pts)
    if bounce_idx < num_pts:
        t_b = t[:-bounce_idx]
        b_wave = (
            0.6 * np.sin(2.0 * np.pi * (f_res2 * 1.05) * t_b) +
            0.4 * np.sin(2.0 * np.pi * (f_res3 * 1.05) * t_b)
        ) * np.exp(-t_b / (decay_time * 0.8))
        bounce[bounce_idx:] = b_wave * bounce_amp
        
    click = primary + bounce
    max_val = np.max(np.abs(click))
    if max_val > 0:
        click /= max_val
    return click

def generate_50s_computer_soundtrack():
    sample_rate = 44100
    duration = 32.0  # 32 seconds loop
    num_samples = int(duration * sample_rate)
    
    left = np.zeros(num_samples, dtype=np.float64)
    right = np.zeros(num_samples, dtype=np.float64)
    
    # -------------------------------------------------------------
    # 1. Very faint, clean room background air (NO buzzing hum at all!)
    # Just quiet, smooth room acoustic tone (-38 dB)
    # -------------------------------------------------------------
    np.random.seed(1951)  # UNIVAC I year!
    room_noise = np.random.normal(0, 1, num_samples)
    b_r, a_r = signal.butter(2, [80.0 / (sample_rate / 2.0), 400.0 / (sample_rate / 2.0)], btype='band')
    soft_air = signal.filtfilt(b_r, a_r, room_noise)
    soft_air = (soft_air / np.max(np.abs(soft_air))) * 0.022
    
    room_noise_r = np.random.normal(0, 1, num_samples)
    soft_air_r = signal.filtfilt(b_r, a_r, room_noise_r)
    soft_air_r = (soft_air_r / np.max(np.abs(soft_air_r))) * 0.022
    
    left += soft_air
    right += soft_air_r
    
    # -------------------------------------------------------------
    # Helper to add a click at a timestamp with panning and gain
    # -------------------------------------------------------------
    def add_click(timestamp, relay_type='medium', gain=1.0, pan=0.0):
        click = synthesize_relay_click(relay_type, sample_rate) * gain
        start_idx = int(timestamp * sample_rate)
        end_idx = start_idx + len(click)
        if end_idx >= num_samples:
            return
        
        # Panning (-1.0 to 1.0)
        pan_l = np.cos((pan + 1.0) * np.pi / 4.0)
        pan_r = np.sin((pan + 1.0) * np.pi / 4.0)
        
        left[start_idx:end_idx] += click * pan_l
        right[start_idx:end_idx] += click * pan_r

    # -------------------------------------------------------------
    # 2. Program Event Sequences (Active 1950s Computing)
    # Realistic timing of relay-based calculation cycles
    # -------------------------------------------------------------
    
    # Pre-generate random, organic timing across the 32 seconds
    np.random.seed(1955)
    
    # A) Steady scattered background logic clicks (0.2s - 0.7s intervals)
    cur_t = 0.4
    while cur_t < duration - 1.0:
        relay_choice = np.random.choice(['light', 'medium', 'heavy'], p=[0.45, 0.40, 0.15])
        gain = np.random.uniform(0.35, 0.75)
        pan = np.random.uniform(-0.85, 0.85)
        add_click(cur_t, relay_choice, gain, pan)
        
        # Sometimes a paired relay response (e.g. flip-flop toggle, 20-50ms later)
        if np.random.random() < 0.40:
            pair_delay = np.random.uniform(0.025, 0.065)
            pair_pan = np.clip(pan + np.random.uniform(-0.25, 0.25), -1.0, 1.0)
            add_click(cur_t + pair_delay, 'light' if relay_choice != 'heavy' else 'medium', gain * 0.85, pair_pan)
            
        cur_t += np.random.uniform(0.18, 0.65)
        
    # B) Computation bursts (Accumulator cycles, add/multiply flurries)
    # Several bursts simulating mathematical execution
    burst_start_times = [2.2, 6.8, 11.4, 15.6, 20.2, 24.8, 28.5]
    
    for b_start in burst_start_times:
        num_clicks = np.random.randint(6, 14)
        tempo = np.random.uniform(0.038, 0.068)  # 38ms - 68ms clock period
        base_pan = np.random.uniform(-0.6, 0.6)
        
        for k in range(num_clicks):
            t_click = b_start + k * tempo + np.random.uniform(-0.004, 0.004)
            r_type = np.random.choice(['light', 'medium', 'heavy'], p=[0.55, 0.35, 0.10])
            gain = np.random.uniform(0.45, 0.85)
            pan = np.clip(base_pan + np.random.uniform(-0.25, 0.25), -1.0, 1.0)
            add_click(t_click, r_type, gain, pan)
            
        # Concluding heavy register latch at end of calculation
        t_finish = b_start + num_clicks * tempo + 0.085
        add_click(t_finish, 'heavy', 0.90, base_pan)
        add_click(t_finish + 0.015, 'stepper', 0.70, base_pan)

    # C) Stepping switches (Rotary drum selector / sequence advance)
    # Rhythmic mechanical "chunk-chunk-chunk-clack" every 10 seconds
    stepper_times = [4.5, 13.8, 22.5]
    for s_time in stepper_times:
        steps = np.random.randint(4, 7)
        step_interval = 0.082
        s_pan = np.random.choice([-0.7, 0.7])
        for s_idx in range(steps):
            t_s = s_time + s_idx * step_interval
            add_click(t_s, 'stepper', 0.85, s_pan)
        add_click(s_time + steps * step_interval + 0.04, 'heavy', 0.95, s_pan)

    # D) Occasional gentle vacuum-tube warm audio chime / bell ping (very subtle)
    # Like an end-of-batch or card-punch bell, once or twice in 32s
    for bell_t in [9.5, 26.5]:
        b_dur = 0.8
        n_b = int(b_dur * sample_rate)
        t_b = np.linspace(0, b_dur, n_b, endpoint=False)
        bell_wave = (
            0.6 * np.sin(2.0 * np.pi * 784.0 * t_b) +  # G5
            0.4 * np.sin(2.0 * np.pi * 1568.0 * t_b)   # G6
        ) * np.exp(-t_b / 0.18) * 0.08
        idx_b = int(bell_t * sample_rate)
        if idx_b + n_b < num_samples:
            left[idx_b:idx_b+n_b] += bell_wave * 0.3
            right[idx_b:idx_b+n_b] += bell_wave * 0.8

    # -------------------------------------------------------------
    # 3. Seamless Loop Crossfade (1.0 second)
    # -------------------------------------------------------------
    xfade_samples = int(1.0 * sample_rate)
    fade_out = np.cos(0.5 * np.pi * np.linspace(0, 1, xfade_samples))
    fade_in = np.sin(0.5 * np.pi * np.linspace(0, 1, xfade_samples))
    
    tail_l = left[-xfade_samples:].copy()
    tail_r = right[-xfade_samples:].copy()
    head_l = left[:xfade_samples].copy()
    head_r = right[:xfade_samples].copy()
    
    left[:xfade_samples] = head_l * fade_in + tail_l * fade_out
    right[:xfade_samples] = head_r * fade_in + tail_r * fade_out
    left[-xfade_samples:] = left[:xfade_samples]
    right[-xfade_samples:] = right[:xfade_samples]
    
    stereo = np.column_stack((left, right))
    
    # Normalize peak to -1.0 dBFS (~0.89)
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo = (stereo / peak) * 0.89
        
    print(f"Synthesized {duration}s 1950s Mechanical Relay Computer Sound! Peak: {np.max(np.abs(stereo)):.3f}")
    return stereo, sample_rate

if __name__ == "__main__":
    audio, sr = generate_50s_computer_soundtrack()
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sounds"))
    ogg_path = os.path.join(out_dir, "BMUSIC.ogg")
    wav_path = os.path.join(out_dir, "BMUSIC.wav")
    
    sf.write(ogg_path, audio, sr, format='OGG', subtype='VORBIS')
    sf.write(wav_path, audio, sr, format='WAV', subtype='PCM_16')
    print(f"Saved: {ogg_path}")
    print(f"Saved: {wav_path}")
