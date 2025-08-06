#!/usr/bin/env python3
"""
Comprehensive Automated Test Suite for BanglaRAG System

This script performs exhaustive testing of all system components:
- Core RAG functionality
- Mixed-language embedding (BanglaBERT + Nomic)
- Voice input system (Whisper + BanglaSpeech2Text)
- Database operations
- Performance metrics
- Citation accuracy
- Translation capabilities
- Error handling and fallbacks

Generates a detailed HTML report with visualizations and metrics.
"""

import os
import sys
import time
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any
import warnings

warnings.filterwarnings("ignore")

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "system_info": {},
    "component_tests": {},
    "performance_metrics": {},
    "integration_tests": {},
    "error_analysis": {},
    "recommendations": [],
}


def log_test(
    component: str,
    test_name: str,
    status: str,
    details: Any = None,
    duration: float = None,
):
    """Log test results in structured format."""
    if component not in test_results["component_tests"]:
        test_results["component_tests"][component] = []

    result = {
        "test_name": test_name,
        "status": status,  # "PASS", "FAIL", "SKIP", "WARNING"
        "details": details,
        "duration": duration,
        "timestamp": datetime.now().isoformat(),
    }

    test_results["component_tests"][component].append(result)

    # Print real-time feedback
    status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARNING": "⚠️"}
    duration_str = f" ({duration:.2f}s)" if duration else ""
    print(f"{status_emoji.get(status, '❓')} {component}: {test_name}{duration_str}")
    if details and status in ["FAIL", "WARNING"]:
        print(f"   Details: {details}")


def test_system_info():
    """Gather system information and dependencies."""
    print("\n🔍 SYSTEM INFORMATION ANALYSIS")
    print("=" * 50)

    start_time = time.time()
    info = {}

    try:
        import platform

        info["platform"] = platform.platform()
        info["python_version"] = platform.python_version()
        info["architecture"] = platform.architecture()[0]

        # Check key dependencies
        dependencies = {}

        # Core dependencies
        try:
            import ollama_llm

            dependencies["ollama_llm"] = "✅ Available"
        except ImportError as e:
            dependencies["ollama_llm"] = f"❌ Missing: {e}"

        try:
            import voice_input

            dependencies["voice_input"] = "✅ Available"
        except ImportError as e:
            dependencies["voice_input"] = f"❌ Missing: {e}"

        try:
            import embedding

            dependencies["embedding"] = "✅ Available"
        except ImportError as e:
            dependencies["embedding"] = f"❌ Missing: {e}"

        # Bangla-specific dependencies
        try:
            from banglaspeech2text import Speech2Text

            dependencies["banglaspeech2text"] = "✅ Available"
        except ImportError:
            dependencies["banglaspeech2text"] = "❌ Not installed"

        try:
            from transformers import AutoTokenizer, AutoModel

            dependencies["transformers"] = "✅ Available (for BanglaBERT)"
        except ImportError:
            dependencies["transformers"] = "❌ Missing (BanglaBERT unavailable)"

        try:
            import whisper

            dependencies["whisper"] = "✅ Available"
        except ImportError:
            dependencies["whisper"] = "❌ Missing"

        try:
            import chromadb

            dependencies["chromadb"] = "✅ Available"
        except ImportError:
            dependencies["chromadb"] = "❌ Missing"

        info["dependencies"] = dependencies

        # Check file system
        required_files = [
            "main.py",
            "voice_input.py",
            "embedding.py",
            "ollama_llm.py",
            "query_database.py",
            "create_database.py",
            "requirements.txt",
            "config.py",
            "launch.py",
        ]

        file_status = {}
        for file in required_files:
            file_status[file] = "✅ Present" if os.path.exists(file) else "❌ Missing"

        info["files"] = file_status

        test_results["system_info"] = info

        duration = time.time() - start_time
        log_test("System", "Information Gathering", "PASS", info, duration)

    except Exception as e:
        duration = time.time() - start_time
        log_test("System", "Information Gathering", "FAIL", str(e), duration)


def test_database_operations():
    """Test database loading and querying."""
    print("\n📚 DATABASE OPERATIONS TESTING")
    print("=" * 50)

    try:
        start_time = time.time()
        from query_database import load_database, query_database

        # Test database loading
        db = load_database()
        if db:
            duration = time.time() - start_time
            log_test(
                "Database",
                "Load Database",
                "PASS",
                "Database loaded successfully",
                duration,
            )

            # Test database querying
            start_time = time.time()
            results = query_database("test query", db, k=3)
            duration = time.time() - start_time

            if results:
                log_test(
                    "Database",
                    "Query Database",
                    "PASS",
                    f"Retrieved {len(results)} results",
                    duration,
                )

                # Check metadata
                if results[0].metadata:
                    log_test(
                        "Database",
                        "Metadata Check",
                        "PASS",
                        "Metadata present in results",
                    )
                else:
                    log_test(
                        "Database",
                        "Metadata Check",
                        "WARNING",
                        "No metadata in results",
                    )
            else:
                log_test(
                    "Database",
                    "Query Database",
                    "FAIL",
                    "No results returned",
                    duration,
                )
        else:
            duration = time.time() - start_time
            log_test(
                "Database", "Load Database", "FAIL", "Failed to load database", duration
            )

    except Exception as e:
        log_test("Database", "Operations", "FAIL", f"Exception: {str(e)}")


def test_embedding_system():
    """Test mixed-language embedding system."""
    print("\n🧠 EMBEDDING SYSTEM TESTING")
    print("=" * 50)

    try:
        from embedding import (
            get_embedding_function_with_fallback,
            detect_language,
            get_mixed_language_embedding,
            embed_bangla,
            embed_english,
        )

        # Test basic embedding
        start_time = time.time()
        embedding_func = get_embedding_function_with_fallback()
        test_embedding = embedding_func.embed_query("test")
        duration = time.time() - start_time

        if test_embedding and len(test_embedding) > 0:
            log_test(
                "Embedding",
                "Basic Embedding",
                "PASS",
                f"Generated {len(test_embedding)}D embedding",
                duration,
            )
        else:
            log_test(
                "Embedding",
                "Basic Embedding",
                "FAIL",
                "No embedding generated",
                duration,
            )

        # Test language detection
        test_cases = [
            ("This is English text", "en"),
            ("এটি বাংলা টেক্সট", "bn"),
            ("Machine learning algorithms", "en"),
        ]

        for text, expected_lang in test_cases:
            start_time = time.time()
            detected = detect_language(text)
            duration = time.time() - start_time

            if detected == expected_lang:
                log_test(
                    "Embedding",
                    f"Language Detection ({expected_lang})",
                    "PASS",
                    f"Correctly detected {detected}",
                    duration,
                )
            else:
                log_test(
                    "Embedding",
                    f"Language Detection ({expected_lang})",
                    "WARNING",
                    f"Expected {expected_lang}, got {detected}",
                    duration,
                )

        # Test BanglaBERT
        try:
            start_time = time.time()
            bangla_embedding = embed_bangla("এটি একটি পরীক্ষা")
            duration = time.time() - start_time

            if bangla_embedding is not None and len(bangla_embedding) > 0:
                log_test(
                    "Embedding",
                    "BanglaBERT",
                    "PASS",
                    f"Generated {len(bangla_embedding)}D Bangla embedding",
                    duration,
                )
            else:
                log_test(
                    "Embedding",
                    "BanglaBERT",
                    "FAIL",
                    "Failed to generate Bangla embedding",
                    duration,
                )
        except Exception as e:
            log_test("Embedding", "BanglaBERT", "FAIL", f"BanglaBERT error: {str(e)}")

        # Test mixed language embedding
        start_time = time.time()
        mixed_embedding = get_mixed_language_embedding("Dynamic programming algorithms")
        duration = time.time() - start_time

        if mixed_embedding is not None:
            log_test(
                "Embedding",
                "Mixed Language",
                "PASS",
                f"Generated mixed embedding",
                duration,
            )
        else:
            log_test(
                "Embedding",
                "Mixed Language",
                "FAIL",
                "Failed mixed embedding",
                duration,
            )

    except Exception as e:
        log_test("Embedding", "System", "FAIL", f"Exception: {str(e)}")


def test_voice_input_system():
    """Test voice input capabilities."""
    print("\n🎤 VOICE INPUT SYSTEM TESTING")
    print("=" * 50)

    try:
        import voice_input

        # Test Whisper availability
        try:
            model = voice_input.load_whisper_model("tiny")  # Use tiny for speed
            if model:
                log_test(
                    "Voice",
                    "Whisper Model Loading",
                    "PASS",
                    "Whisper tiny model loaded",
                )
            else:
                log_test(
                    "Voice",
                    "Whisper Model Loading",
                    "FAIL",
                    "Failed to load Whisper model",
                )
        except Exception as e:
            log_test(
                "Voice", "Whisper Model Loading", "FAIL", f"Whisper error: {str(e)}"
            )

        # Test BanglaSpeech2Text availability
        if voice_input.BANGLA_STT_AVAILABLE:
            try:
                bangla_model = voice_input.load_bangla_stt_model(
                    "tiny"
                )  # Use tiny for speed
                if bangla_model:
                    log_test(
                        "Voice",
                        "BanglaSpeech2Text Model",
                        "PASS",
                        "BanglaSpeech2Text model loaded",
                    )
                else:
                    log_test(
                        "Voice",
                        "BanglaSpeech2Text Model",
                        "FAIL",
                        "Failed to load BanglaSpeech2Text",
                    )
            except Exception as e:
                log_test(
                    "Voice",
                    "BanglaSpeech2Text Model",
                    "FAIL",
                    f"BanglaSpeech2Text error: {str(e)}",
                )
        else:
            log_test(
                "Voice",
                "BanglaSpeech2Text Model",
                "SKIP",
                "BanglaSpeech2Text not installed",
            )

        # Test audio recording capability (without actually recording)
        try:
            import pyaudio

            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            p.terminate()

            if device_count > 0:
                log_test(
                    "Voice",
                    "Audio Device Check",
                    "PASS",
                    f"Found {device_count} audio devices",
                )
            else:
                log_test(
                    "Voice", "Audio Device Check", "WARNING", "No audio devices found"
                )
        except Exception as e:
            log_test("Voice", "Audio Device Check", "FAIL", f"PyAudio error: {str(e)}")

        # Test Gradio interface creation (without launching)
        try:
            interface = voice_input.create_gradio_interface()
            if interface:
                log_test(
                    "Voice",
                    "Gradio Interface",
                    "PASS",
                    "Gradio interface created successfully",
                )
            else:
                log_test(
                    "Voice",
                    "Gradio Interface",
                    "FAIL",
                    "Failed to create Gradio interface",
                )
        except Exception as e:
            log_test("Voice", "Gradio Interface", "FAIL", f"Gradio error: {str(e)}")

    except Exception as e:
        log_test("Voice", "System", "FAIL", f"Exception: {str(e)}")


def test_rag_pipeline():
    """Test complete RAG pipeline."""
    print("\n🤖 RAG PIPELINE TESTING")
    print("=" * 50)

    try:
        from ollama_llm import run_rag_query
        from query_database import load_database

        # Load database
        db = load_database()
        if not db:
            log_test(
                "RAG",
                "Database Loading",
                "FAIL",
                "Cannot load database for RAG testing",
            )
            return

        # Test queries
        test_queries = [
            ("What is dynamic programming?", "en"),
            ("অ্যালগরিদম কি?", "bn"),
            ("Explain sorting algorithms", "en"),
            ("", "empty"),  # Edge case
        ]

        performance_metrics = []

        for query, lang_type in test_queries:
            if not query:  # Empty query test
                start_time = time.time()
                result = run_rag_query(query, db=db)
                duration = time.time() - start_time

                if not result.get("success", False):
                    log_test(
                        "RAG",
                        "Empty Query Handling",
                        "PASS",
                        "Correctly handled empty query",
                        duration,
                    )
                else:
                    log_test(
                        "RAG",
                        "Empty Query Handling",
                        "WARNING",
                        "Should reject empty query",
                        duration,
                    )
                continue

            start_time = time.time()
            result = run_rag_query(query, db=db)
            duration = time.time() - start_time

            performance_metrics.append(
                {
                    "query": query,
                    "language": lang_type,
                    "duration": duration,
                    "success": result.get("success", False),
                }
            )

            if result.get("success"):
                # Check response quality
                answer = result.get("answer", "")
                sources = result.get("sources", [])

                if answer and len(answer) > 10:
                    log_test(
                        "RAG",
                        f"Query Processing ({lang_type})",
                        "PASS",
                        f"Generated {len(answer)} char response in {duration:.2f}s",
                        duration,
                    )
                else:
                    log_test(
                        "RAG",
                        f"Query Processing ({lang_type})",
                        "WARNING",
                        f"Short response: {len(answer)} chars",
                        duration,
                    )

                # Check citations
                if sources and len(sources) > 0:
                    log_test(
                        "RAG",
                        f"Citation Generation ({lang_type})",
                        "PASS",
                        f"Generated {len(sources)} citations",
                    )

                    # Check citation quality
                    for i, source in enumerate(sources[:2]):  # Check first 2 sources
                        title = source.get("title", "")
                        page = source.get("page_number") or source.get("page", "N/A")

                        if title and title != "Unknown":
                            log_test(
                                "RAG",
                                f"Citation Quality {i+1}",
                                "PASS",
                                f"Good citation: {title[:50]}...",
                            )
                        else:
                            log_test(
                                "RAG",
                                f"Citation Quality {i+1}",
                                "WARNING",
                                "Citation missing title",
                            )
                else:
                    log_test(
                        "RAG",
                        f"Citation Generation ({lang_type})",
                        "FAIL",
                        "No citations generated",
                    )
            else:
                log_test(
                    "RAG",
                    f"Query Processing ({lang_type})",
                    "FAIL",
                    f"Query failed: {result.get('error', 'Unknown error')}",
                    duration,
                )

        # Performance analysis
        if performance_metrics:
            avg_duration = sum(
                m["duration"] for m in performance_metrics if m["success"]
            ) / len([m for m in performance_metrics if m["success"]])
            success_rate = (
                sum(1 for m in performance_metrics if m["success"])
                / len(performance_metrics)
                * 100
            )

            test_results["performance_metrics"] = {
                "average_response_time": avg_duration,
                "success_rate": success_rate,
                "total_queries": len(performance_metrics),
                "details": performance_metrics,
            }

            if avg_duration < 5.0:
                log_test(
                    "RAG",
                    "Performance",
                    "PASS",
                    f"Avg response time: {avg_duration:.2f}s (< 5s target)",
                )
            elif avg_duration < 10.0:
                log_test(
                    "RAG",
                    "Performance",
                    "WARNING",
                    f"Avg response time: {avg_duration:.2f}s (acceptable)",
                )
            else:
                log_test(
                    "RAG",
                    "Performance",
                    "FAIL",
                    f"Avg response time: {avg_duration:.2f}s (too slow)",
                )

            if success_rate >= 90:
                log_test(
                    "RAG", "Reliability", "PASS", f"Success rate: {success_rate:.1f}%"
                )
            elif success_rate >= 75:
                log_test(
                    "RAG",
                    "Reliability",
                    "WARNING",
                    f"Success rate: {success_rate:.1f}%",
                )
            else:
                log_test(
                    "RAG", "Reliability", "FAIL", f"Success rate: {success_rate:.1f}%"
                )

    except Exception as e:
        log_test("RAG", "Pipeline", "FAIL", f"Exception: {str(e)}")


def test_translation_system():
    """Test translation capabilities."""
    print("\n🌐 TRANSLATION SYSTEM TESTING")
    print("=" * 50)

    try:
        from translator import process_query_with_translation

        test_cases = [
            "অ্যালগরিদম কি?",
            "ডেটা স্ট্রাকচার সম্পর্কে বলুন",
            "What is machine learning?",  # English - should skip translation
        ]

        for query in test_cases:
            start_time = time.time()
            result = process_query_with_translation(query)
            duration = time.time() - start_time

            if result.get("success"):
                original = result.get("original_query", "")
                processed = result.get("processed_query", "")
                language = result.get("language_detected", "unknown")

                if language == "english" and original == processed:
                    log_test(
                        "Translation",
                        "English Skip",
                        "PASS",
                        f"Correctly skipped English translation",
                        duration,
                    )
                elif language == "bengali" and processed != original:
                    log_test(
                        "Translation",
                        "Bangla Translation",
                        "PASS",
                        f"Translated: {original[:30]}... → {processed[:30]}...",
                        duration,
                    )
                else:
                    log_test(
                        "Translation",
                        f"Translation ({language})",
                        "WARNING",
                        f"Unexpected behavior",
                        duration,
                    )
            else:
                log_test(
                    "Translation",
                    "Translation",
                    "FAIL",
                    f"Translation failed: {result.get('error', 'Unknown')}",
                    duration,
                )

    except Exception as e:
        log_test("Translation", "System", "FAIL", f"Exception: {str(e)}")


def test_configuration_system():
    """Test configuration and launcher."""
    print("\n⚙️ CONFIGURATION SYSTEM TESTING")
    print("=" * 50)

    try:
        # Test config loading
        import config

        # Check key configuration values
        if hasattr(config, "PREFERRED_MODEL"):
            log_test(
                "Config",
                "Model Configuration",
                "PASS",
                f"Preferred model: {config.PREFERRED_MODEL}",
            )
        else:
            log_test(
                "Config", "Model Configuration", "FAIL", "PREFERRED_MODEL not found"
            )

        if hasattr(config, "FALLBACK_MODELS"):
            log_test(
                "Config",
                "Fallback Models",
                "PASS",
                f"Fallback models: {len(config.FALLBACK_MODELS)} configured",
            )
        else:
            log_test(
                "Config", "Fallback Models", "WARNING", "FALLBACK_MODELS not found"
            )

        # Test launcher
        try:
            import launch

            log_test("Config", "Launcher Module", "PASS", "Launcher module available")
        except Exception as e:
            log_test("Config", "Launcher Module", "FAIL", f"Launcher error: {str(e)}")

    except Exception as e:
        log_test("Config", "System", "FAIL", f"Exception: {str(e)}")


def analyze_integration():
    """Analyze system integration and generate recommendations."""
    print("\n🔗 INTEGRATION ANALYSIS")
    print("=" * 50)

    # Count test results
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warnings = 0

    for component, tests in test_results["component_tests"].items():
        for test in tests:
            total_tests += 1
            if test["status"] == "PASS":
                passed_tests += 1
            elif test["status"] == "FAIL":
                failed_tests += 1
            elif test["status"] == "WARNING":
                warnings += 1

    # Calculate health score
    health_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    test_results["integration_tests"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "warnings": warnings,
        "health_score": health_score,
    }

    # Generate recommendations
    recommendations = []

    if health_score >= 90:
        recommendations.append(
            "🎉 Excellent system health! Ready for production deployment."
        )
    elif health_score >= 75:
        recommendations.append(
            "✅ Good system health. Address warnings for optimal performance."
        )
    else:
        recommendations.append(
            "⚠️ System needs attention. Address failed tests before deployment."
        )

    # Specific recommendations based on test results
    if failed_tests > 0:
        recommendations.append(
            "🔧 Fix failed components to improve system reliability."
        )

    if warnings > 3:
        recommendations.append(
            "⚠️ Multiple warnings detected. Review system configuration."
        )

    # Performance recommendations
    perf_metrics = test_results.get("performance_metrics", {})
    avg_time = perf_metrics.get("average_response_time", 0)

    if avg_time > 5:
        recommendations.append(
            "⚡ Consider performance optimization to reduce response times."
        )
    elif avg_time < 3:
        recommendations.append("🚀 Excellent performance! Response times are optimal.")

    test_results["recommendations"] = recommendations

    print(f"📊 System Health Score: {health_score:.1f}%")
    print(
        f"📈 Tests: {passed_tests} passed, {failed_tests} failed, {warnings} warnings"
    )


def generate_html_report():
    """Generate comprehensive HTML report."""

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BanglaRAG System - Comprehensive Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .content {{
            padding: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 5px solid #3498db;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .metric-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .test-grid {{
            display: grid;
            gap: 15px;
        }}
        .test-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-item.pass {{ border-left-color: #27ae60; }}
        .test-item.fail {{ border-left-color: #e74c3c; }}
        .test-item.warning {{ border-left-color: #f39c12; }}
        .test-item.skip {{ border-left-color: #95a5a6; }}
        .test-name {{
            font-weight: 600;
            color: #2c3e50;
        }}
        .test-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-pass {{ background: #d5f4e6; color: #27ae60; }}
        .status-fail {{ background: #ffeaea; color: #e74c3c; }}
        .status-warning {{ background: #fef9e7; color: #f39c12; }}
        .status-skip {{ background: #f4f4f4; color: #95a5a6; }}
        .recommendations {{
            background: #e8f5e8;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }}
        .recommendations h3 {{
            color: #27ae60;
            margin-top: 0;
        }}
        .recommendations ul {{
            list-style: none;
            padding: 0;
        }}
        .recommendations li {{
            padding: 8px 0;
            border-bottom: 1px solid #d5f4e6;
        }}
        .recommendations li:last-child {{
            border-bottom: none;
        }}
        .performance-chart {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        .system-info {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        .system-info table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .system-info th, .system-info td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .system-info th {{
            background: #3498db;
            color: white;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 30px;
        }}
        .health-score {{
            font-size: 3em;
            font-weight: bold;
            color: #27ae60;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 BanglaRAG System</h1>
            <p>Comprehensive Automated Test Report</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
            <!-- Health Score -->
            <div class="section">
                <div class="metric-card" style="text-align: center; max-width: 300px; margin: 0 auto;">
                    <div class="health-score">{test_results['integration_tests']['health_score']:.1f}%</div>
                    <div class="metric-label">System Health Score</div>
                </div>
            </div>
            
            <!-- Key Metrics -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{test_results['integration_tests']['total_tests']}</div>
                    <div class="metric-label">Total Tests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #27ae60;">{test_results['integration_tests']['passed']}</div>
                    <div class="metric-label">Passed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #e74c3c;">{test_results['integration_tests']['failed']}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #f39c12;">{test_results['integration_tests']['warnings']}</div>
                    <div class="metric-label">Warnings</div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            {generate_performance_section()}
            
            <!-- Component Test Results -->
            <div class="section">
                <h2>📋 Component Test Results</h2>
                {generate_component_tests_html()}
            </div>
            
            <!-- System Information -->
            <div class="section">
                <h2>💻 System Information</h2>
                <div class="system-info">
                    {generate_system_info_html()}
                </div>
            </div>
            
            <!-- Recommendations -->
            <div class="recommendations">
                <h3>🎯 Recommendations</h3>
                <ul>
                    {"".join(f"<li>{rec}</li>" for rec in test_results['recommendations'])}
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>BanglaRAG System - Advanced Bangla & English RAG with Voice Input</p>
            <p>Report generated by Comprehensive Test Suite v1.0</p>
        </div>
    </div>
</body>
</html>
"""

    return html_content


def generate_performance_section():
    """Generate performance metrics section."""
    perf = test_results.get("performance_metrics", {})
    if not perf:
        return "<p>No performance data available.</p>"

    avg_time = perf.get("average_response_time", 0)
    success_rate = perf.get("success_rate", 0)

    return f"""
    <div class="section">
        <h2>⚡ Performance Metrics</h2>
        <div class="performance-chart">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{avg_time:.2f}s</div>
                    <div class="metric-label">Avg Response Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{success_rate:.1f}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{'🎯 Excellent' if avg_time < 5 else '⚠️ Needs Work'}</div>
                    <div class="metric-label">Performance Rating</div>
                </div>
            </div>
        </div>
    </div>
    """


def generate_component_tests_html():
    """Generate HTML for component test results."""
    html = ""

    for component, tests in test_results["component_tests"].items():
        html += f"<h3>🔧 {component}</h3><div class='test-grid'>"

        for test in tests:
            status_class = test["status"].lower()
            status_text = test["status"]
            duration_text = (
                f" ({test['duration']:.2f}s)" if test.get("duration") else ""
            )

            html += f"""
            <div class="test-item {status_class}">
                <div>
                    <div class="test-name">{test['test_name']}{duration_text}</div>
                    {f"<small style='color: #7f8c8d;'>{test['details']}</small>" if test.get('details') else ""}
                </div>
                <div class="test-status status-{status_class}">{status_text}</div>
            </div>
            """

        html += "</div>"

    return html


def generate_system_info_html():
    """Generate system information HTML table."""
    info = test_results.get("system_info", {})

    html = "<table>"

    # Platform info
    html += "<tr><th colspan='2'>Platform Information</th></tr>"
    html += f"<tr><td>Platform</td><td>{info.get('platform', 'Unknown')}</td></tr>"
    html += f"<tr><td>Python Version</td><td>{info.get('python_version', 'Unknown')}</td></tr>"
    html += (
        f"<tr><td>Architecture</td><td>{info.get('architecture', 'Unknown')}</td></tr>"
    )

    # Dependencies
    if "dependencies" in info:
        html += "<tr><th colspan='2'>Dependencies</th></tr>"
        for dep, status in info["dependencies"].items():
            html += f"<tr><td>{dep}</td><td>{status}</td></tr>"

    # Files
    if "files" in info:
        html += "<tr><th colspan='2'>Required Files</th></tr>"
        for file, status in info["files"].items():
            html += f"<tr><td>{file}</td><td>{status}</td></tr>"

    html += "</table>"
    return html


def main():
    """Run comprehensive test suite."""
    print("🚀 BANGLARAG COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing all system components and generating detailed report...")
    print("=" * 60)

    # Run all tests
    test_system_info()
    test_database_operations()
    test_embedding_system()
    test_voice_input_system()
    test_rag_pipeline()
    test_translation_system()
    test_configuration_system()

    # Analyze results
    analyze_integration()

    # Generate reports
    print("\n📊 GENERATING REPORTS")
    print("=" * 50)

    # Save JSON report
    json_filename = (
        f"banglarag_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON report saved: {json_filename}")

    # Generate HTML report
    html_content = generate_html_report()
    html_filename = (
        f"banglarag_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ HTML report saved: {html_filename}")

    # Print summary
    print("\n🎯 TEST SUMMARY")
    print("=" * 50)
    integration = test_results["integration_tests"]
    print(f"📊 Health Score: {integration['health_score']:.1f}%")
    print(
        f"📈 Tests: {integration['passed']} passed, {integration['failed']} failed, {integration['warnings']} warnings"
    )

    if test_results.get("performance_metrics"):
        perf = test_results["performance_metrics"]
        print(
            f"⚡ Performance: {perf['average_response_time']:.2f}s avg response, {perf['success_rate']:.1f}% success rate"
        )

    print(f"\n📋 Detailed reports available:")
    print(f"   • JSON: {json_filename}")
    print(f"   • HTML: {html_filename}")

    print("\n🎉 Testing completed successfully!")

    return test_results


if __name__ == "__main__":
    main()
