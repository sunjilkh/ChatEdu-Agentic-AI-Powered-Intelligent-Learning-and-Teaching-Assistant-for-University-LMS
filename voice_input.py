import whisper
import pyaudio
import wave
import tempfile
import os
import argparse
import sys
from pathlib import Path
from query_database import load_database
from ollama_llm import run_rag_query
import warnings

# Try to import BanglaSpeech2Text for enhanced Bangla recognition
try:
    from banglaspeech2text import Speech2Text, available_models
    import speech_recognition as sr

    BANGLA_STT_AVAILABLE = True
    print("✅ BanglaSpeech2Text available for enhanced Bangla recognition")

    # Show available models
    try:
        models = available_models()
        print(f"📋 Available BanglaSpeech2Text models: {models}")
    except:
        print("📋 BanglaSpeech2Text models: tiny, base, small, large")

except ImportError:
    BANGLA_STT_AVAILABLE = False
    print(
        "⚠️  BanglaSpeech2Text not available. Install with: pip install banglaspeech2text"
    )
    print("💡 For enhanced Bangla recognition, run: pip install banglaspeech2text")

warnings.filterwarnings("ignore")

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5  # Default recording time

# Global models
_whisper_model = None
_bangla_stt_model = None


def load_whisper_model(model_size="base"):
    """
    Load Whisper model for transcription.

    Args:
        model_size (str): Model size - "tiny", "base", "small", "medium", "large"

    Returns:
        whisper.Whisper: Loaded model
    """
    global _whisper_model

    if _whisper_model is None:
        print(f"🔄 Loading Whisper '{model_size}' model...")
        try:
            _whisper_model = whisper.load_model(model_size)
            print(f"✅ Whisper model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            return None

    return _whisper_model


def load_bangla_stt_model(model_size="base"):
    """
    Load BanglaSpeech2Text model for enhanced Bangla recognition.

    According to the GitHub repo, available models:
    - tiny: 100-200 MB, WER: 74
    - base: 200-300 MB, WER: 46
    - small: 1 GB, WER: 18
    - large: 3-4 GB, WER: 11 (best accuracy)

    Args:
        model_size (str): Model size - "tiny", "base", "small", "large"

    Returns:
        Speech2Text: Loaded BanglaSpeech2Text model
    """
    global _bangla_stt_model

    if not BANGLA_STT_AVAILABLE:
        return None

    if _bangla_stt_model is None:
        print(f"🔄 Loading BanglaSpeech2Text '{model_size}' model...")
        print(f"📊 Expected performance - Model: {model_size}")

        # Show expected performance based on GitHub documentation
        wer_info = {
            "tiny": "WER: 74, Size: 100-200MB",
            "base": "WER: 46, Size: 200-300MB",
            "small": "WER: 18, Size: 1GB",
            "large": "WER: 11, Size: 3-4GB (best accuracy)",
        }
        print(f"📈 {wer_info.get(model_size, 'Custom model')}")

        try:
            _bangla_stt_model = Speech2Text(model_size)
            print(f"✅ BanglaSpeech2Text '{model_size}' model loaded successfully!")

            # Show model metadata if available
            if hasattr(_bangla_stt_model, "model_metadata"):
                metadata = _bangla_stt_model.model_metadata
                print(f"🔍 Model info: {metadata}")

        except Exception as e:
            print(f"❌ Error loading BanglaSpeech2Text model: {e}")
            print(f"💡 Try a smaller model size or check internet connection")
            return None

    return _bangla_stt_model


def record_audio(duration=RECORD_SECONDS, output_file="temp_audio.wav"):
    """
    Record audio from microphone.

    Args:
        duration (int): Recording duration in seconds
        output_file (str): Output file path

    Returns:
        str: Path to recorded audio file
    """
    try:
        # Initialize PyAudio
        p = pyaudio.PyAudio()

        print(f"🎤 Recording audio for {duration} seconds...")
        print("📍 Speak now!")

        # Open stream
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []

        # Record audio
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("🔴 Recording finished!")

        # Stop and close stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save audio file
        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))

        print(f"💾 Audio saved to: {output_file}")
        return output_file

    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        return None


def transcribe_audio(
    audio_file, model_size="base", language=None, use_bangla_stt=False
):
    """
    Transcribe audio file using Whisper or BanglaSpeech2Text.

    Enhanced logic to prefer BanglaSpeech2Text for better Bangla recognition.

    Args:
        audio_file (str): Path to audio file
        model_size (str): Model size
        language (str): Language code (e.g., 'en', 'bn') or None for auto-detection
        use_bangla_stt (bool): Whether to use BanglaSpeech2Text for Bangla audio

    Returns:
        dict: Transcription results
    """
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return None

    # Smart language detection: if BanglaSpeech2Text is available and no specific language is set,
    # try BanglaSpeech2Text first for better Bangla recognition
    if BANGLA_STT_AVAILABLE and (use_bangla_stt or language == "bn"):
        print("🇧🇩 Using BanglaSpeech2Text for enhanced Bangla recognition...")
        return transcribe_with_bangla_stt(audio_file, model_size)

    # If no language specified and BanglaSpeech2Text is available, try it first
    # then fallback to Whisper if needed
    if BANGLA_STT_AVAILABLE and language is None:
        print("🔄 Trying BanglaSpeech2Text first for potential Bangla content...")
        bangla_result = transcribe_with_bangla_stt(audio_file, model_size)

        # Check if BanglaSpeech2Text produced meaningful results
        if bangla_result and bangla_result.get("text", "").strip():
            bangla_text = bangla_result["text"].strip()
            # If the result has Bangla characters or reasonable length, use it
            if len(bangla_text) > 3 and (
                any(char in bangla_text for char in "অআইউএওকখগঘচছজঝটঠড")
                or len(bangla_text.split()) > 1
            ):
                print("✅ BanglaSpeech2Text produced good results, using it")
                return bangla_result
            else:
                print("⚠️ BanglaSpeech2Text result seems unclear, trying Whisper...")
        else:
            print("⚠️ BanglaSpeech2Text failed, falling back to Whisper...")

    # Use Whisper for all other cases or as fallback
    return transcribe_with_whisper(audio_file, model_size, language)


def transcribe_with_whisper(audio_file, model_size="base", language=None):
    """
    Transcribe audio using Whisper with improved language handling.
    """
    model = load_whisper_model(model_size)
    if model is None:
        return None

    try:
        print(f"🔄 Transcribing with Whisper...")

        # Enhanced language detection and handling
        if language:
            print(f"🎯 Using specified language: {language}")
            result = model.transcribe(audio_file, language=language)
        else:
            # Let Whisper auto-detect but with improved handling
            result = model.transcribe(audio_file)

            # Check for common misdetections
            detected_lang = result.get("language", "unknown")
            transcribed_text = result.get("text", "").strip()

            # If Whisper detects Greek/other languages but text seems like Bangla
            if detected_lang in ["el", "hi", "ur", "ar"] and transcribed_text:
                print(
                    f"⚠️ Whisper detected '{detected_lang}' but checking for Bangla content..."
                )

                # If BanglaSpeech2Text is available, try it as correction
                if BANGLA_STT_AVAILABLE:
                    print("🔄 Trying BanglaSpeech2Text for correction...")
                    bangla_result = transcribe_with_bangla_stt(audio_file, model_size)
                    if bangla_result and bangla_result.get("text", "").strip():
                        print("✅ BanglaSpeech2Text provided better result")
                        return bangla_result

                # Otherwise, force Bangla language in Whisper
                print("🔄 Retrying Whisper with Bangla language forced...")
                try:
                    forced_result = model.transcribe(audio_file, language="bn")
                    if forced_result and forced_result.get("text", "").strip():
                        print("✅ Forced Bangla transcription successful")
                        return forced_result
                except:
                    print("⚠️ Forced Bangla transcription failed, using original result")

        print(f"✅ Whisper transcription completed!")
        print(f"🌐 Detected language: {result.get('language', 'unknown')}")
        return result

    except Exception as e:
        print(f"❌ Error transcribing with Whisper: {e}")
        return None


def transcribe_with_bangla_stt(audio_file, model_size="base", return_segments=False):
    """
    Transcribe audio using BanglaSpeech2Text for enhanced Bangla recognition.

    Based on GitHub documentation, BanglaSpeech2Text supports:
    - Multiple audio formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
    - Segment-wise transcription with timestamps
    - Better accuracy for Bangla compared to generic Whisper
    """
    model = load_bangla_stt_model(model_size)
    if model is None:
        return None

    try:
        print(f"🔄 Transcribing with BanglaSpeech2Text (optimized for Bangla)...")
        print(f"🎯 Using model: {model_size} - Fine-tuned Whisper for Bangla")

        # BanglaSpeech2Text transcription with optional segments
        if return_segments:
            print("📊 Generating transcription with timestamps...")
            segments = model.recognize(audio_file, return_segments=True)

            # Extract full text and segments
            full_text = " ".join([segment.text for segment in segments])
            segment_data = [
                {"start": segment.start, "end": segment.end, "text": segment.text}
                for segment in segments
            ]

            result = {
                "text": full_text,
                "language": "bn",
                "segments": segment_data,
                "model": f"BanglaSpeech2Text-{model_size}",
            }

            print(f"📝 Generated {len(segments)} segments")
        else:
            # Simple transcription
            transcription_text = model.recognize(audio_file)
            result = {
                "text": transcription_text,
                "language": "bn",  # BanglaSpeech2Text is specifically for Bangla
                "model": f"BanglaSpeech2Text-{model_size}",
            }

        print(f"✅ BanglaSpeech2Text transcription completed!")
        print(f"📊 Transcribed text length: {len(result['text'])} characters")

        return result

    except Exception as e:
        print(f"❌ Error transcribing with BanglaSpeech2Text: {e}")
        print(f"💡 Ensure audio file exists and is in supported format")
        return None


def process_voice_query(
    audio_file=None, duration=5, model_size="base", language=None, use_bangla_stt=False
):
    """
    Complete voice query processing: record -> transcribe -> search -> respond.

    Args:
        audio_file (str): Path to existing audio file (if None, will record new)
        duration (int): Recording duration if recording new audio
        model_size (str): Model size
        language (str): Language code or None for auto-detection
        use_bangla_stt (bool): Whether to use BanglaSpeech2Text for Bangla

    Returns:
        dict: Complete query results
    """
    print("\n🎙️ VOICE QUERY PROCESSING")
    print("=" * 50)

    # Step 1: Get audio file
    if audio_file is None or not os.path.exists(audio_file):
        print("🎤 No audio file provided, recording new audio...")
        audio_file = record_audio(duration)
        if audio_file is None:
            return {"success": False, "error": "Failed to record audio"}
    else:
        print(f"🔊 Using existing audio file: {audio_file}")

    # Step 2: Transcribe audio with enhanced options
    transcription = transcribe_audio(audio_file, model_size, language, use_bangla_stt)
    if transcription is None:
        return {"success": False, "error": "Failed to transcribe audio"}

    query_text = transcription["text"].strip()
    detected_language = transcription.get("language", "unknown")

    print(f"✅ Transcription completed!")
    print(f"🌐 Detected language: {detected_language}")
    print(f"📝 Text: {query_text}")

    if not query_text:
        return {"success": False, "error": "No speech detected"}

    print(f"\n🔍 Searching for: '{query_text}'")

    # Step 3: Load database and run RAG query
    db = load_database()
    if db is None:
        return {"success": False, "error": "Database not available"}

    # Step 4: Run optimized RAG query
    rag_result = run_rag_query(query_text, db=db)

    # Step 5: Combine results
    result = {
        "success": True,
        "query": query_text,
        "transcription": {
            "text": query_text,
            "language": detected_language,
            "confidence": 1.0,  # Default confidence
            "success": True,
        },
        "rag_result": rag_result,
        "audio_file": audio_file,
    }

    return result


def display_voice_query_results(result):
    """
    Display voice query results in a formatted way.

    Args:
        result (dict): Voice query results
    """
    if not result.get("success"):
        print(f"❌ Voice query failed: {result.get('error', 'Unknown error')}")
        return

    print("\n" + "=" * 60)
    print("🎙️ VOICE QUERY RESULTS")
    print("=" * 60)

    # Transcription info
    transcription = result.get("transcription", {})
    print(f"📝 Query: '{result.get('query', 'N/A')}'")
    print(f"🌐 Language: {transcription.get('language', 'unknown')}")
    print(f"🎯 Confidence: {transcription.get('confidence', 0.0):.2f}")

    # RAG result
    rag_result = result.get("rag_result", {})
    if rag_result.get("success"):
        print(f"\n🤖 AI Response:")
        print(rag_result.get("answer", "No response"))

        # Citations with proper book names
        sources = rag_result.get("sources", [])
        if sources:
            print(f"\n📚 Sources:")
            for i, source in enumerate(sources[:3], 1):
                # Extract book information
                title = source.get("title", "")
                file_name = source.get("file_name") or source.get(
                    "source_file", "Unknown"
                )
                page_num = source.get("page_number") or source.get("page", "N/A")

                # Clean up the title if available
                if title and title.startswith("[") and "]" in title:
                    # Extract clean title from format like "[9780262270830] Introduction to Algorithms, third edition"
                    clean_title = title.split("]", 1)[1].strip()
                    book_name = clean_title
                elif file_name and file_name != "Unknown":
                    # Use filename without extension as book name
                    book_name = file_name.replace(".pdf", "").replace("_", " ")
                else:
                    book_name = "Unknown"

                print(f"   {i}. {book_name} (Page {page_num})")

        print(f"\n🤖 Model: {rag_result.get('model_used', 'Unknown')}")
        if rag_result.get("processing_time"):
            print(f"⏱️  Processing time: {rag_result['processing_time']:.2f}s")
    else:
        print(f"❌ RAG query failed: {rag_result.get('error', 'Unknown error')}")

    print("=" * 60)


def interactive_voice_session():
    """
    Run an interactive voice query session with enhanced features.

    Enhanced with BanglaSpeech2Text integration for superior Bangla recognition.
    """
    print("🎤 Enhanced Interactive Voice Query Session")
    print("=" * 60)
    print("🌟 BanglaRAG Voice Input with Multi-Model ASR Support")
    print("=" * 60)

    # Show available models
    print("\n📋 Available ASR Models:")
    print("  🌍 Whisper: Multilingual (English, Bangla, others)")
    if BANGLA_STT_AVAILABLE:
        print(
            "  🇧🇩 BanglaSpeech2Text: Optimized for Bangla (WER: 11-74 depending on model)"
        )
        print("     - tiny: Fast, WER 74")
        print("     - base: Balanced, WER 46")
        print("     - small: Better, WER 18")
        print("     - large: Best accuracy, WER 11")
    else:
        print("  ❌ BanglaSpeech2Text: Not installed")

    print("\n📝 Commands:")
    print("  - Press Enter: Start recording")
    print("  - 'bangla': Switch to BanglaSpeech2Text mode")
    print("  - 'whisper': Switch to Whisper mode")
    print("  - 'model [size]': Change BanglaSpeech2Text model (tiny/base/small/large)")
    print("  - 'status': Show current settings")
    print("  - 'help': Show this help")
    print("  - 'quit': Exit session")

    # Session state
    use_bangla_stt = False
    current_model = "base"

    print(
        f"\n🎯 Current mode: {'🇧🇩 BanglaSpeech2Text' if use_bangla_stt else '🌍 Whisper'}"
    )
    if use_bangla_stt:
        print(f"📊 Model size: {current_model}")

    while True:
        try:
            user_input = input(
                f"\n🎤 Press Enter to record [{('BanglaSpeech2Text-' + current_model) if use_bangla_stt else 'Whisper'}] (or command): "
            ).strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye! Thanks for using BanglaRAG Voice Input!")
                break

            if user_input.lower() == "help":
                print("\n📖 Available Commands:")
                print("  📹 Enter: Start 5-second recording")
                print("  🇧🇩 bangla: Switch to BanglaSpeech2Text (better for Bangla)")
                print("  🌍 whisper: Switch to Whisper (multilingual)")
                print("  ⚙️  model [size]: Change model (tiny/base/small/large)")
                print("  📊 status: Show current configuration")
                print("  ❓ help: Show this help")
                print("  🚪 quit/exit/q: Exit session")
                continue

            if user_input.lower() == "status":
                print(f"\n📊 Current Configuration:")
                print(
                    f"  🎯 ASR Mode: {'🇧🇩 BanglaSpeech2Text' if use_bangla_stt else '🌍 Whisper'}"
                )
                if use_bangla_stt:
                    print(f"  📈 Model: {current_model}")
                    wer_info = {
                        "tiny": "74",
                        "base": "46",
                        "small": "18",
                        "large": "11",
                    }
                    print(
                        f"  🎯 Expected WER: {wer_info.get(current_model, 'Unknown')}"
                    )
                print(f"  🎙️  Recording: 5 seconds")
                print(f"  🌐 Language: {'Bangla' if use_bangla_stt else 'Auto-detect'}")
                continue

            if user_input.lower().startswith("model "):
                if not BANGLA_STT_AVAILABLE:
                    print("❌ BanglaSpeech2Text not available for model switching")
                    continue

                model_parts = user_input.split()
                if len(model_parts) > 1:
                    new_model = model_parts[1].lower()
                    if new_model in ["tiny", "base", "small", "large"]:
                        current_model = new_model
                        use_bangla_stt = True  # Auto-switch to BanglaSpeech2Text
                        print(
                            f"✅ Switched to BanglaSpeech2Text model: {current_model}"
                        )

                        # Reset the global model to force reload
                        global _bangla_stt_model
                        _bangla_stt_model = None
                    else:
                        print("❌ Invalid model. Use: tiny, base, small, or large")
                else:
                    print("❌ Usage: model [tiny|base|small|large]")
                continue

            if user_input.lower() == "bangla":
                if BANGLA_STT_AVAILABLE:
                    use_bangla_stt = True
                    print(
                        f"🇧🇩 Switched to BanglaSpeech2Text mode (model: {current_model})"
                    )
                    print(
                        "💡 Optimized for Bangla speech recognition with fine-tuned Whisper"
                    )
                else:
                    print("❌ BanglaSpeech2Text not available")
                    print("💡 Install with: pip install banglaspeech2text")
                continue

            if user_input.lower() == "whisper":
                use_bangla_stt = False
                print("🌍 Switched to Whisper mode (multilingual)")
                print("💡 Supports multiple languages with auto-detection")
                continue

            # Determine language based on mode
            language = "bn" if use_bangla_stt else None

            # Process voice query with selected method
            print(
                f"\n🎙️ Using: {'🇧🇩 BanglaSpeech2Text-' + current_model if use_bangla_stt else '🌍 Whisper'}"
            )
            result = process_voice_query(
                duration=5,
                language=language,
                use_bangla_stt=use_bangla_stt,
                model_size=current_model,
            )
            display_voice_query_results(result)

        except KeyboardInterrupt:
            print("\n👋 Session ended by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try 'help' for available commands")


def create_gradio_interface():
    """
    Create a Gradio web interface for BanglaSpeech2Text as shown in GitHub examples.
    """
    if not BANGLA_STT_AVAILABLE:
        print("❌ BanglaSpeech2Text not available for Gradio interface")
        print("💡 Install with: pip install banglaspeech2text")
        return None

    try:
        import gradio as gr

        print("🌐 Creating Gradio interface for BanglaRAG Voice Input...")

        # Initialize BanglaSpeech2Text model
        stt = Speech2Text("base")  # Using base model for balance of speed/accuracy

        def process_audio_gradio(audio_file):
            """Process audio through the complete RAG pipeline for Gradio."""
            if audio_file is None:
                return "❌ No audio file provided"

            try:
                # Process through the full voice query pipeline
                result = process_voice_query(
                    audio_file=audio_file,
                    use_bangla_stt=True,  # Use BanglaSpeech2Text for Gradio
                    model_size="base",
                )

                if result.get("success"):
                    rag_result = result.get("rag_result", {})
                    if rag_result.get("success"):
                        # Format response with citations
                        response = (
                            f"🤖 Answer: {rag_result.get('answer', 'No response')}\n\n"
                        )

                        sources = rag_result.get("sources", [])
                        if sources:
                            response += "📚 Sources:\n"
                            for i, source in enumerate(sources[:3], 1):
                                title = source.get("title", "")
                                if title and title.startswith("[") and "]" in title:
                                    book_name = title.split("]", 1)[1].strip()
                                else:
                                    book_name = source.get(
                                        "file_name", "Unknown"
                                    ).replace(".pdf", "")
                                page_num = source.get("page_number") or source.get(
                                    "page", "N/A"
                                )
                                response += f"   {i}. {book_name} (Page {page_num})\n"

                        response += f"\n⏱️ Processing time: {rag_result.get('processing_time', 0):.2f}s"
                        response += (
                            f"\n🤖 Model: {rag_result.get('model_used', 'Unknown')}"
                        )
                        return response
                    else:
                        return f"❌ RAG query failed: {rag_result.get('error', 'Unknown error')}"
                else:
                    return f"❌ Voice processing failed: {result.get('error', 'Unknown error')}"

            except Exception as e:
                return f"❌ Error processing audio: {str(e)}"

        # Create Gradio interface
        interface = gr.Interface(
            fn=process_audio_gradio,
            inputs=gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="🎙️ Record or Upload Audio",
            ),
            outputs=gr.Textbox(label="📝 BanglaRAG Response", lines=10),
            title="🌟 BanglaRAG Voice Input System",
            description="""
            🎤 **Enhanced Voice Input for BanglaRAG System**
            
            • 🇧🇩 **Optimized for Bangla**: Uses BanglaSpeech2Text for superior Bangla recognition
            • 🌍 **Multilingual Support**: Also handles English and other languages  
            • 📚 **Smart Citations**: Provides page-level references from textbooks
            • ⚡ **Fast Performance**: Optimized pipeline with caching
            
            **Usage**: Record audio or upload a file, then get AI responses with proper citations!
            """,
            examples=[
                ["Record: 'অ্যালগরিদম কি?'", "Ask about algorithms in Bangla"],
                [
                    "Record: 'What is dynamic programming?'",
                    "Ask about programming concepts in English",
                ],
            ],
            theme=gr.themes.Soft(),
            allow_flagging="never",
        )

        return interface

    except ImportError:
        print("❌ Gradio not available. Install with: pip install gradio")
        return None
    except Exception as e:
        print(f"❌ Error creating Gradio interface: {e}")
        return None


def test_voice_transcription():
    """
    Test voice transcription with sample audio or live recording.
    Enhanced with BanglaSpeech2Text testing.
    """
    print("🧪 Testing Enhanced Voice Transcription")
    print("=" * 50)

    # Test models if BanglaSpeech2Text is available
    if BANGLA_STT_AVAILABLE:
        print("🇧🇩 Testing BanglaSpeech2Text models...")
        models_to_test = ["tiny", "base"]  # Test smaller models for speed

        for model in models_to_test:
            print(f"\n🎯 Testing BanglaSpeech2Text model: {model}")
            print("🎤 Please speak in Bangla...")

            audio_file = record_audio(duration=3)
            if audio_file:
                result = transcribe_with_bangla_stt(audio_file, model_size=model)
                if result:
                    print(f"✅ Transcription: '{result['text']}'")
                    print(f"🌐 Language: {result.get('language', 'unknown')}")
                    print(f"🤖 Model: {result.get('model', 'Unknown')}")
                else:
                    print("❌ Transcription failed")

                # Clean up
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            else:
                print("❌ Recording failed")

            input("Press Enter to continue...")

    # Test with different languages using Whisper
    print("\n🌍 Testing Whisper multilingual...")
    test_languages = [
        {"name": "English", "code": "en"},
        {"name": "Bangla", "code": "bn"},
        {"name": "Auto-detect", "code": None},
    ]

    for lang_info in test_languages:
        print(f"\n🎯 Testing {lang_info['name']} transcription with Whisper...")

        # Record audio
        audio_file = record_audio(duration=3)
        if audio_file:
            # Transcribe
            result = transcribe_audio(audio_file, language=lang_info["code"])
            if result:
                print(f"✅ Transcription: '{result['text']}'")
                print(f"🌐 Detected Language: {result.get('language', 'unknown')}")
            else:
                print("❌ Transcription failed")

            # Clean up
            if os.path.exists(audio_file):
                os.remove(audio_file)
        else:
            print("❌ Recording failed")

        input("Press Enter to continue to next test...")


def main():
    """
    Main function to handle command line arguments and run voice input.
    """
    parser = argparse.ArgumentParser(
        description="Enhanced Voice Input for BanglaRAG System"
    )
    parser.add_argument(
        "--audio", "-a", type=str, help="Path to audio file to transcribe"
    )
    parser.add_argument(
        "--duration", "-d", type=int, default=5, help="Recording duration in seconds"
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Model size",
    )
    parser.add_argument(
        "--language", "-l", type=str, help="Language code (e.g., 'en', 'bn')"
    )
    parser.add_argument(
        "--bangla-stt", action="store_true", help="Use BanglaSpeech2Text for Bangla"
    )
    parser.add_argument("--test", action="store_true", help="Run transcription tests")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run interactive voice session"
    )
    parser.add_argument(
        "--gradio", "-g", action="store_true", help="Launch Gradio web interface"
    )

    args = parser.parse_args()

    if args.test:
        test_voice_transcription()
    elif args.gradio:
        # Launch Gradio web interface
        interface = create_gradio_interface()
        if interface:
            print("🌐 Launching Gradio web interface...")
            print("💡 Open the provided URL in your browser")
            interface.launch(share=True, server_name="0.0.0.0")
        else:
            print("❌ Failed to create Gradio interface")
    elif args.interactive:
        interactive_voice_session()
    elif args.audio:
        # Process existing audio file
        result = process_voice_query(
            audio_file=args.audio,
            model_size=args.model,
            language=args.language,
            use_bangla_stt=args.bangla_stt,
        )
        display_voice_query_results(result)
    else:
        # Record and process new audio
        result = process_voice_query(
            duration=args.duration,
            model_size=args.model,
            language=args.language,
            use_bangla_stt=args.bangla_stt,
        )
        display_voice_query_results(result)


if __name__ == "__main__":
    main()
