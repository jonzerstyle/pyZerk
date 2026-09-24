#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Configure WSL audio via PulseAudio if available
if [ -S /mnt/wslg/PulseServer ]; then
    export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
    export SDL_AUDIODRIVER="pulseaudio"
    export LD_LIBRARY_PATH="/home/mjones/.local/lib:/home/mjones/.local/lib/pulseaudio${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

python3 "$DIR/main.py" "$@"
