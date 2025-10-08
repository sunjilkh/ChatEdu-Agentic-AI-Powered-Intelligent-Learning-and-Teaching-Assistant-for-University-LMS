#!/usr/bin/env python3
"""
Demo script to show continuous voice functionality without 5-second time limits.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.continuous_voice_service import ContinuousVoiceInterface


def main():
    print("🎤 CONTINUOUS VOICE DEMO")
    print("=" * 60)
    print("This demo shows that continuous voice mode works WITHOUT 5-second limits!")
    print()
    print("Key Features:")
    print("✅ No time limit - speak as long as you want")
    print("✅ Automatic pause detection (2-second silence)")
    print("✅ Natural conversation flow")
    print("✅ WebRTC Voice Activity Detection")
    print()
    print("How it works:")
    print("1. Start speaking your question")
    print("2. When you pause for 2 seconds, it automatically processes")
    print("3. You get a response")
    print("4. It immediately starts listening for your next question")
    print("5. Continue the conversation naturally!")
    print()

    # Show service info
    interface = ContinuousVoiceInterface()
    info = interface.get_service_info()

    print("🔧 Service Status:")
    print(f"   Available: {info['available']}")
    print(f"   WebRTC VAD: {info['webrtcvad_available']}")
    print(f"   Features: {', '.join(info['features'])}")
    print(f"   Default silence threshold: {info['silence_threshold_default']} seconds")
    print(f"   Minimum speech duration: {info['min_speech_duration_default']} seconds")
    print()

    # Ask user if they want to start
    try:
        response = input("🚀 Start continuous voice session? (y/N): ").strip().lower()
        if response in ["y", "yes"]:
            print("\n🎯 Starting continuous voice session...")
            print("   Speak naturally and pause for 2 seconds when done!")

            # Get custom settings if desired
            try:
                silence_input = input(
                    "Custom silence threshold in seconds [2.0]: "
                ).strip()
                silence_threshold = float(silence_input) if silence_input else 2.0
            except ValueError:
                silence_threshold = 2.0

            print(f"🔄 Using {silence_threshold}s silence threshold")
            print("\n" + "=" * 60)

            # Start the continuous session
            success = interface.start_continuous_session(
                silence_threshold=silence_threshold, min_speech_duration=0.5
            )

            if success:
                print("\n✅ Session completed successfully!")
                interface.show_conversation_history()
            else:
                print("\n❌ Session ended unexpectedly")
        else:
            print(
                "👋 Demo cancelled. You can run this anytime to test continuous voice!"
            )

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
