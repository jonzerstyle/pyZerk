import os
import random
import soundfile as sf
import numpy as np

# Set seed for artistic repeatability with natural variations
random.seed(1701)
np.random.seed(1701)

sr = 44100
target_dur = 64.0  # 64.0 seconds soundscape
total_samples = int(target_dur * sr)
xfade_dur = 3.5    # 3.5s crossfade
xfade_samples = int(xfade_dur * sr)

# 1. Load backdrop (Envisioning Science Fiction Starship Ambience)
m_path = '/home/mjones/agy/pyzerk_audio_scratch/envisioning_main_preview.mp3'
m_data, m_sr = sf.read(m_path)
if m_sr != sr:
    raise ValueError(f"Sample rate mismatch: {m_sr} != {sr}")

# Trim silence at ends
thresh = 0.001
act = np.where(np.abs(m_data).max(axis=1) > thresh)[0]
m_trimmed = m_data[act[0]:act[-1]]
m_len = len(m_trimmed)

# Create raw bed of length = total_samples + xfade_samples
raw_len = total_samples + xfade_samples
raw_bed = np.zeros((raw_len, 2), dtype=np.float32)

pos = 0
step = m_len - xfade_samples
while pos < raw_len:
    chunk = m_trimmed
    end_pos = min(pos + len(chunk), raw_len)
    actual_chunk_len = end_pos - pos
    
    if pos == 0:
        raw_bed[pos:end_pos] = chunk[:actual_chunk_len]
    else:
        xf = min(xfade_samples, actual_chunk_len)
        t = np.linspace(0, 1, xf, endpoint=False)
        f_in = np.sin(t * np.pi / 2)[:, None]
        f_out = np.cos(t * np.pi / 2)[:, None]
        raw_bed[pos:pos+xf] = raw_bed[pos:pos+xf] * f_out + chunk[:xf] * f_in
        if actual_chunk_len > xf:
            raw_bed[pos+xf:end_pos] = chunk[xf:actual_chunk_len]
    pos += step

print(f"Backdrop bed generated: {raw_bed.shape}, duration={raw_len/sr:.2f}s")

# 2. Pool of shorter sounds
short_sound_files = [
    'trek-communicator.mp3',
    'bridge_1.mp3',
    'bridge_56.mp3',
    'bridge_57.mp3',
    'bridge_74.mp3',
    'bridge_101.mp3',
    'bridge_116.mp3',
    'science-fiction-space-shu.mp3',
    'space-trek-02.mp3',
    'space-trek-03.mp3'
]

short_sounds = []
for fname in short_sound_files:
    p = f'/home/mjones/agy/pyzerk_audio_scratch/{fname}'
    d, s = sf.read(p)
    pk = np.max(np.abs(d))
    if pk > 0:
        # Standardize peak level to 0.40 before placement
        d = d * (0.40 / pk)
    short_sounds.append((fname, d))

# 3. Schedule random occurrences throughout raw_bed
t_cur = 3.5
events = []
used_indices = []

while t_cur < target_dur - 2.5:
    available = [i for i in range(len(short_sounds)) if i not in used_indices[-2:]]
    idx = random.choice(available)
    used_indices.append(idx)
    
    fname, snd = short_sounds[idx]
    dur = len(snd) / sr
    pan = random.uniform(-0.35, 0.35)
    left_gain = 0.5 * (1.0 - pan)
    right_gain = 0.5 * (1.0 + pan)
    gain = random.uniform(0.65, 0.90)
    
    start_sample = int(t_cur * sr)
    end_sample = start_sample + len(snd)
    
    if end_sample <= raw_len:
        panned = np.column_stack([snd[:, 0] * left_gain * gain, snd[:, 1] * right_gain * gain])
        raw_bed[start_sample:end_sample] += panned
        events.append((t_cur, fname, pan, gain))
    
    t_cur += dur + random.uniform(3.5, 7.0)

print(f"Scheduled {len(events)} short sound events:")
for ev in events:
    print(f"  at {ev[0]:5.2f}s: {ev[1]:30} (pan={ev[2]:+.2f}, gain={ev[3]:.2f})")

# 4. Make seamless loop: blend tail into head
base = raw_bed[:total_samples].copy()
tail = raw_bed[total_samples:total_samples + xfade_samples]

t = np.linspace(0, 1, xfade_samples, endpoint=False)
fade_in = np.sin(t * np.pi / 2)[:, None]
fade_out = np.cos(t * np.pi / 2)[:, None]
base[:xfade_samples] = base[:xfade_samples] * fade_in + tail * fade_out

# 5. Master: Peak normalize to -1.0 dBFS (0.89125)
current_peak = np.max(np.abs(base))
master_peak = 0.89125
mastered = (base * (master_peak / current_peak)).astype(np.float32)

final_rms = np.sqrt(np.mean(mastered**2))
final_peak = np.max(np.abs(mastered))
print(f"Mastered: Dur={len(mastered)/sr:.2f}s, Peak={final_peak:.4f}, RMS={final_rms:.4f}")

# Check seam error
seam_step = mastered[0] - mastered[-1]
natural_step = raw_bed[total_samples] * (master_peak / current_peak) - mastered[-1]
seam_error = np.max(np.abs(seam_step - natural_step))
print(f"Seam Discontinuity Error: {seam_error:.8f}")

# 6. Export to sounds/BMUSIC.wav (PCM 16-bit)
sf.write('sounds/BMUSIC.wav', mastered, sr, format='WAV', subtype='PCM_16')
print("Successfully written to sounds/BMUSIC.wav!")

# 7. Export to sounds/BMUSIC.ogg in safe chunks (Vorbis OGG)
chunk_size = 44100  # 1-second chunks to prevent libsndfile buffer overflow
with sf.SoundFile('sounds/BMUSIC.ogg', 'w', sr, 2, format='OGG', subtype='VORBIS') as f:
    for i in range(0, len(mastered), chunk_size):
        f.write(mastered[i:i+chunk_size])
print("Successfully written to sounds/BMUSIC.ogg!")

info_ogg = sf.info('sounds/BMUSIC.ogg')
print(f"Verified BMUSIC.ogg: {info_ogg.duration:.2f}s, {info_ogg.format} {info_ogg.subtype}, {os.path.getsize('sounds/BMUSIC.ogg')} bytes")
info_wav = sf.info('sounds/BMUSIC.wav')
print(f"Verified BMUSIC.wav: {info_wav.duration:.2f}s, {info_wav.format} {info_wav.subtype}, {os.path.getsize('sounds/BMUSIC.wav')} bytes")
