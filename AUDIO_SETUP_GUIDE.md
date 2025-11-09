# 🎤 Audio Setup Guide

**Purpose**: Complete guide for setting up audio drivers for voice mode

**Addresses**: Manus AI evaluation recommendation for OS-specific audio setup guidance

---

## 📋 Overview

The Big Three Agents system supports **voice mode** using:
- **Input**: Microphone (via `sounddevice`)
- **Output**: Speakers (via `sounddevice`)
- **Processing**: OpenAI Realtime API

Voice mode is **optional** - the system works perfectly in text mode without any audio setup.

---

## 🖥️ OS-Specific Setup

### Linux (Ubuntu/Debian)

#### 1. Install System Audio Libraries

```bash
# Install PortAudio (required for sounddevice)
sudo apt-get update
sudo apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    libasound2-dev \
    libportaudio2

# Install PulseAudio (for modern audio management)
sudo apt-get install -y pulseaudio pulseaudio-utils
```

#### 2. Verify Audio Devices

```bash
# List audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Test microphone
arecord -d 5 test.wav  # Record 5 seconds
aplay test.wav         # Playback
```

#### 3. Fix Common Issues

**Issue**: "ALSA lib pcm.c: Unknown PCM"
```bash
# Solution: Install ALSA plugins
sudo apt-get install libasound2-plugins
```

**Issue**: Permission denied
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login for changes to take effect
```

---

### macOS

#### 1. Install PortAudio

```bash
# Using Homebrew
brew install portaudio

# Verify installation
brew list portaudio
```

#### 2. Install Python Audio Library

```bash
# sounddevice should install automatically with pip
pip install sounddevice

# If issues, try:
pip install --upgrade sounddevice
```

#### 3. Verify Audio Devices

```bash
# List devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

#### 4. Fix Common Issues

**Issue**: "PortAudio library not found"
```bash
# Reinstall portaudio
brew reinstall portaudio

# Update environment
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
```

---

### Windows

#### 1. No Additional Drivers Needed

Windows includes audio support by default. Python `sounddevice` should work out of the box.

#### 2. Install Python Dependencies

```bash
# In PowerShell or Command Prompt
pip install sounddevice numpy

# If using WSL2, follow Linux instructions
```

#### 3. Verify Audio

```python
# test_audio.py
import sounddevice as sd
import numpy as np

# Test playback
duration = 1  # seconds
frequency = 440  # Hz (A note)
sample_rate = 44100

t = np.linspace(0, duration, int(sample_rate * duration))
audio = 0.5 * np.sin(2 * np.pi * frequency * t)

sd.play(audio, sample_rate)
sd.wait()
print("✅ Audio playback working!")
```

#### 4. Fix Common Issues

**Issue**: "No audio devices found"
- Check Windows Sound Settings
- Ensure microphone/speakers are enabled
- Update audio drivers

---

## 🐳 Docker Audio Setup

### Linux Docker Audio

```yaml
# docker-compose.yml
services:
  big-three-agents:
    # ... existing config
    devices:
      - /dev/snd:/dev/snd  # Audio devices
    group_add:
      - audio
    environment:
      - PULSE_SERVER=unix:/run/user/1000/pulse/native
    volumes:
      - /run/user/1000/pulse:/run/user/1000/pulse
```

### macOS Docker Audio

Audio passthrough on macOS Docker is complex. **Recommended**: Use text mode or run natively.

---

## 🧪 Testing Audio Setup

### Quick Test Script

```python
#!/usr/bin/env python3
"""
Test audio setup for Big Three Agents.
"""

import sys


def test_import():
    """Test sounddevice import."""
    try:
        import sounddevice as sd
        print("✅ sounddevice imported successfully")
        return True
    except ImportError as e:
        print(f"❌ sounddevice import failed: {e}")
        print("   Install: pip install sounddevice")
        return False


def test_devices():
    """Test audio device detection."""
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        print(f"\n📊 Found {len(devices)} audio devices:")

        for i, device in enumerate(devices):
            print(f"   [{i}] {device['name']}")
            print(f"       Input channels: {device['max_input_channels']}")
            print(f"       Output channels: {device['max_output_channels']}")

        # Check default devices
        default_input = sd.query_devices(kind='input')
        default_output = sd.query_devices(kind='output')

        print(f"\n✅ Default input: {default_input['name']}")
        print(f"✅ Default output: {default_output['name']}")

        return True

    except Exception as e:
        print(f"❌ Device query failed: {e}")
        return False


def test_recording():
    """Test microphone recording."""
    try:
        import sounddevice as sd
        import numpy as np

        print("\n🎤 Testing microphone (2 seconds)...")
        duration = 2
        sample_rate = 44100

        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()

        # Check if we got audio
        if np.max(np.abs(recording)) > 0.01:
            print("✅ Microphone recording successful")
            return True
        else:
            print("⚠️  Microphone recorded silence (check volume/permissions)")
            return False

    except Exception as e:
        print(f"❌ Recording test failed: {e}")
        return False


def test_playback():
    """Test speaker playback."""
    try:
        import sounddevice as sd
        import numpy as np

        print("\n🔊 Testing speakers (1 second beep)...")
        duration = 1
        frequency = 440  # Hz
        sample_rate = 44100

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)

        sd.play(audio, sample_rate)
        sd.wait()

        print("✅ Speaker playback successful")
        return True

    except Exception as e:
        print(f"❌ Playback test failed: {e}")
        return False


def main():
    """Run all audio tests."""
    print("🎵 Big Three Agents - Audio Setup Test")
    print("=" * 50)

    results = []

    results.append(("Import", test_import()))
    results.append(("Devices", test_devices()))

    # Only test recording/playback if import worked
    if results[0][1]:
        results.append(("Recording", test_recording()))
        results.append(("Playback", test_playback()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 All audio tests passed!")
        print("   You can use voice mode: --voice")
        return 0
    else:
        print("\n⚠️  Some audio tests failed")
        print("   Voice mode may not work properly")
        print("   Use text mode instead: --input text --output text")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Save as**: `scripts/test_audio.py`

**Run**:
```bash
python scripts/test_audio.py
```

---

## 🔧 Troubleshooting

### Common Issues

#### "Module not found: sounddevice"
```bash
pip install sounddevice numpy
```

#### "No audio devices found"
```bash
# Linux
sudo apt-get install alsa-utils
alsamixer  # Check if devices are muted

# macOS
# Check System Preferences > Sound
```

#### "Permission denied" (Linux)
```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Restart session
```

#### "ALSA errors" (Linux)
```bash
# Create ALSA config
cat > ~/.asoundrc << EOF
pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}
EOF
```

#### "Audio stuttering/crackling"
```bash
# Increase buffer size
export PULSE_LATENCY_MSEC=60

# Or in Python
import sounddevice as sd
sd.default.latency = 'high'
```

---

## 🎯 Recommendations

### For Development

**Use Text Mode**:
```bash
python -m apps.realtime-poc.big_three_realtime_agents.main --input text --output text
```
- No audio setup needed
- Faster iteration
- Easier debugging

### For Production

**Docker Recommended**:
```bash
docker compose up -d
```
- All audio dependencies pre-installed
- Consistent environment
- No OS-specific issues

### For Voice Features

**Test Incrementally**:
1. Verify audio devices work (run test script)
2. Test text mode first
3. Test audio input only
4. Test audio output only
5. Test full voice mode

---

## 📚 Additional Resources

### Python Audio Libraries
- **sounddevice**: https://python-sounddevice.readthedocs.io/
- **PortAudio**: http://www.portaudio.com/

### OS Audio Documentation
- **Linux ALSA**: https://alsa-project.org/
- **Linux PulseAudio**: https://www.freedesktop.org/wiki/Software/PulseAudio/
- **macOS Core Audio**: https://developer.apple.com/audio/

---

## 🎓 Summary

| Platform | Setup Difficulty | Recommended Approach |
|----------|-----------------|---------------------|
| **Linux** | 🟡 Medium | Docker or manual setup |
| **macOS** | 🟢 Easy | Native or Docker |
| **Windows** | 🟢 Easy | Native (built-in support) |
| **WSL2** | 🔴 Hard | Use text mode |

**Best Practice**: Start with **text mode**, enable voice only if needed.

---

**Guide Version**: 1.0
**Last Updated**: 2025-11-09
**Addresses**: Manus AI Evaluation Recommendation
