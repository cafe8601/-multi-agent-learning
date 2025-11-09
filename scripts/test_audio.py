#!/usr/bin/env python3
"""
Test audio setup for Big Three Agents.

Verifies that sounddevice and audio hardware are properly configured
for voice mode operation.
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
        default_input = sd.query_devices(kind="input")
        default_output = sd.query_devices(kind="output")

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
        print("   Please make some noise...")
        duration = 2
        sample_rate = 44100

        recording = sd.rec(
            int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32"
        )
        sd.wait()

        # Check if we got audio
        max_amplitude = np.max(np.abs(recording))
        if max_amplitude > 0.01:
            print(f"✅ Microphone recording successful (amplitude: {max_amplitude:.3f})")
            return True
        else:
            print(f"⚠️  Microphone recorded silence (amplitude: {max_amplitude:.3f})")
            print("   Check microphone volume and permissions")
            return False

    except Exception as e:
        print(f"❌ Recording test failed: {e}")
        return False


def test_playback():
    """Test speaker playback."""
    try:
        import sounddevice as sd
        import numpy as np

        print("\n🔊 Testing speakers (1 second beep at 440 Hz)...")
        duration = 1
        frequency = 440  # Hz (A note)
        sample_rate = 44100

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)

        sd.play(audio, sample_rate)
        sd.wait()

        print("✅ Speaker playback successful")
        print("   (Did you hear a beep?)")
        return True

    except Exception as e:
        print(f"❌ Playback test failed: {e}")
        return False


def print_help():
    """Print help for common issues."""
    print("\n📖 Troubleshooting Help:")
    print("\n1. sounddevice not installed:")
    print("   pip install sounddevice numpy")
    print("\n2. No audio devices (Linux):")
    print("   sudo apt-get install portaudio19-dev")
    print("\n3. Permission denied (Linux):")
    print("   sudo usermod -a -G audio $USER")
    print("   (then logout and login)")
    print("\n4. Audio not working:")
    print("   - Check system sound settings")
    print("   - Verify microphone/speakers are not muted")
    print("   - Try different audio device")
    print("\n5. Still having issues:")
    print("   Use text mode instead: --input text --output text")
    print("   Voice mode is optional!")


def main():
    """Run all audio tests."""
    print("🎵 Big Three Agents - Audio Setup Test")
    print("=" * 50)

    results = []

    # Test 1: Import
    import_ok = test_import()
    results.append(("Import", import_ok))

    if not import_ok:
        print_help()
        return 1

    # Test 2: Devices
    devices_ok = test_devices()
    results.append(("Devices", devices_ok))

    if not devices_ok:
        print_help()
        return 1

    # Test 3: Recording
    recording_ok = test_recording()
    results.append(("Recording", recording_ok))

    # Test 4: Playback
    playback_ok = test_playback()
    results.append(("Playback", playback_ok))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All audio tests passed!")
        print("\n✅ Voice mode is ready to use:")
        print("   python -m apps.realtime-poc.big_three_realtime_agents.main --voice")
        return 0
    else:
        print("⚠️  Some audio tests failed")
        print("\n📝 Options:")
        print("   1. Fix audio issues (see troubleshooting above)")
        print("   2. Use text mode instead:")
        print("      python -m apps.realtime-poc.big_three_realtime_agents.main")
        print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
