#!/usr/bin/env python3
"""
Quick test for continuous voice functionality.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_continuous_voice_import():
    """Test that continuous voice service can be imported."""
    try:
        from services.continuous_voice_service import ContinuousVoiceInterface

        print("✅ Continuous voice service imported successfully!")

        # Test instantiation
        interface = ContinuousVoiceInterface()
        print("✅ Continuous voice interface created successfully!")

        # Test service info
        info = interface.get_service_info()
        print(f"✅ Service info: {info}")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are available."""
    try:
        import webrtcvad
        import numpy
        import pyaudio

        print("✅ All dependencies (webrtcvad, numpy, pyaudio) are available!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Testing Continuous Voice Functionality")
    print("=" * 50)

    deps_ok = test_dependencies()
    import_ok = test_continuous_voice_import()

    if deps_ok and import_ok:
        print("\n🎉 Continuous voice service is ready!")
        print("💡 You can now use option 2 (Continuous mode) in voice sessions")
    else:
        print("\n⚠️  Some issues detected with continuous voice setup")
