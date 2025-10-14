#!/usr/bin/env python3
"""
Flask API for embeddable chatbot with streaming support.
Integrates with BanglaRAG system for course-based Q&A.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import (
    Flask,
    request,
    jsonify,
    Response,
    stream_with_context,
    send_from_directory,
)
from flask_cors import CORS
import json
import time
from typing import Generator, Dict, Any
import os

from core.logging_config import BanglaRAGLogger, log_info, log_error
from services.database_service import get_database_manager
from services.llm_service import get_model_manager, get_rag_processor
from services.embedding_service import get_embedding_factory

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

logger = BanglaRAGLogger()

# Initialize services
db_manager = None
db_manager_pdf = None  # Second database for PDF book
model_manager = None
rag_processor = None


def initialize_services():
    """Initialize BanglaRAG services with PDF database ONLY."""
    global db_manager, db_manager_pdf, model_manager, rag_processor

    try:
        log_info("Initializing chatbot API services...", "api")
        from services.database_service import DatabaseFactory

        # ONLY use PDF book (Cormen algorithms) - banglarag collection
        try:
            db_manager = DatabaseFactory.create_chroma_database(
                collection_name="banglarag"
            )
            log_info("✅ PDF database (algorithm book) loaded successfully", "api")
            log_info("📚 Using ONLY the algorithm book database", "api")
        except Exception as e:
            log_error(f"❌ Failed to load PDF database: {e}", "api")
            return False

        # Set db_manager_pdf to None (not used)
        db_manager_pdf = None

        model_manager = get_model_manager()
        rag_processor = get_rag_processor()

        log_info(
            "Chatbot API services initialized with PDF database ONLY (algorithm book)",
            "api",
        )
        return True
    except Exception as e:
        log_error(f"Failed to initialize services: {e}", "api", exc_info=True)
        return False


def search_dual_databases(query: str, k: int = 3):
    """
    Search both course materials and PDF database with smart prioritization.

    ALWAYS prioritizes PDF database (algorithm book) first.
    Only uses course materials for course-specific questions (syllabus, schedule, etc.)
    or as fallback if PDF has no results.
    """
    all_results = []

    # Search ONLY the PDF database (algorithm book)
    try:
        all_results = db_manager.search_with_cache(query, k=k)
        log_info(
            f"✅ Found {len(all_results)} results from PDF database (algorithm book)",
            "api",
        )

        # Add source tag to mark as PDF
        for doc in all_results:
            if hasattr(doc, "metadata"):
                doc.metadata["search_source"] = "pdf"
                # Ensure source shows as the algorithm book
                if (
                    "source" not in doc.metadata
                    or "course_knowledge" in doc.metadata.get("source", "").lower()
                ):
                    doc.metadata["source"] = "Cormen - Introduction to Algorithms.pdf"

    except Exception as e:
        log_error(f"❌ Error searching PDF database: {e}", "api")
        all_results = []

    if not all_results:
        log_info("⚠️ No relevant results found in PDF database", "api")

    return all_results


@app.route("/")
def index():
    """Serve the course example page."""
    return send_from_directory(os.path.dirname(__file__), "course-example.html")


@app.route("/teachers")
def teachers():
    """Serve the teachers dashboard page."""
    return send_from_directory(os.path.dirname(__file__), "teachers.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)."""
    # Only serve specific file types for security
    allowed_extensions = {".html", ".css", ".js", ".txt", ".json"}
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext in allowed_extensions:
        try:
            return send_from_directory(os.path.dirname(__file__), filename)
        except:
            return jsonify({"error": "File not found"}), 404
    else:
        return jsonify({"error": "File type not allowed"}), 403


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {"status": "ok", "service": "BanglaRAG Chatbot API", "version": "2.0.0"}
    )


@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available models."""
    try:
        if not model_manager:
            return jsonify({"error": "Service not initialized"}), 503

        models = model_manager.get_available_models()
        current_model = model_manager._active_model or model_manager.preferred_model

        return jsonify(
            {"models": models, "current_model": current_model, "success": True}
        )
    except Exception as e:
        log_error(f"Error getting models: {e}", "api")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/set-model", methods=["POST"])
def set_model():
    """Set the active model."""
    try:
        data = request.json
        model_name = data.get("model")

        if not model_name:
            return jsonify({"error": "Model name required", "success": False}), 400

        if not model_manager:
            return jsonify({"error": "Service not initialized", "success": False}), 503

        # Set the active model directly
        available_models = model_manager.get_available_models()
        if model_name in available_models:
            model_manager._active_model = model_name
            success = True
        else:
            success = False

        return jsonify(
            {
                "success": success,
                "current_model": model_manager._active_model
                or model_manager.preferred_model,
            }
        )
    except Exception as e:
        log_error(f"Error setting model: {e}", "api")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Non-streaming chat endpoint."""
    try:
        data = request.json
        query = data.get("query", "").strip()
        k = data.get("k", 3)  # Number of relevant documents to retrieve

        if not query:
            return jsonify({"error": "Query is required", "success": False}), 400

        if not db_manager or not rag_processor:
            return jsonify({"error": "Service not initialized", "success": False}), 503

        # Search for relevant documents from both databases
        log_info(f"Processing query: {query}", "api")
        relevant_docs = search_dual_databases(query, k=k)

        if not relevant_docs:
            return jsonify(
                {
                    "response": "I couldn't find relevant information in the course materials to answer your question.",
                    "sources": [],
                    "success": True,
                }
            )

        # Generate response using RAG
        rag_result = rag_processor.process_rag_query(query, relevant_docs)

        if rag_result["success"]:
            sources = [
                {
                    "content": (
                        doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content
                    ),
                    "metadata": doc.metadata,
                }
                for doc in relevant_docs[:3]
            ]

            return jsonify(
                {
                    "response": rag_result["response"],
                    "sources": sources,
                    "model": (
                        model_manager.get_current_model()
                        if model_manager
                        else "unknown"
                    ),
                    "success": True,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "error": rag_result.get("error", "Failed to generate response"),
                        "success": False,
                    }
                ),
                500,
            )

    except Exception as e:
        log_error(f"Chat error: {e}", "api", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    """Streaming chat endpoint with real-time response."""
    try:
        data = request.json
        query = data.get("query", "").strip()
        k = data.get("k", 3)
        language = data.get("language", "english")  # Get selected language

        if not query:
            return jsonify({"error": "Query is required"}), 400

        if not db_manager or not model_manager:
            return jsonify({"error": "Service not initialized"}), 503

        def generate() -> Generator[str, None, None]:
            """Generate streaming response."""
            try:
                # Send initial status
                yield f"data: {json.dumps({'type': 'status', 'message': 'Searching knowledge base...'})}\n\n"

                # Search for relevant documents from both databases
                relevant_docs = search_dual_databases(query, k=k)

                if not relevant_docs:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'No relevant information found'})}\n\n"
                    return

                # Send sources
                sources = [
                    {
                        "content": (
                            doc.page_content[:200] + "..."
                            if len(doc.page_content) > 200
                            else doc.page_content
                        ),
                        "metadata": doc.metadata,
                    }
                    for doc in relevant_docs[:3]
                ]
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

                # Send generation status
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"

                # Build context from relevant documents
                context = "\n\n".join(
                    [
                        f"Document {i+1}:\n{doc.page_content}"
                        for i, doc in enumerate(relevant_docs)
                    ]
                )

                # Create prompt with language instruction
                language_instruction = ""
                if language == "bangla":
                    language_instruction = "Please answer in Bengali (বাংলা ভাষায়)."
                else:
                    language_instruction = "Please answer in English."

                prompt = f"""Based on the following course materials, answer the question. Be specific and cite the information provided. {language_instruction}

Course Materials:
{context}

Question: {query}

Answer:"""

                # Stream response from model
                current_model = (
                    model_manager._active_model or model_manager.preferred_model
                )

                # Use Ollama's streaming API
                import requests

                response = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": current_model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {"temperature": 0.7, "num_predict": 2048},
                    },
                    stream=True,
                )

                # Stream tokens as they arrive
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                token = chunk["response"]
                                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"

                            if chunk.get("done", False):
                                yield f"data: {json.dumps({'type': 'done', 'model': current_model})}\n\n"
                                break
                        except json.JSONDecodeError:
                            continue

            except Exception as e:
                log_error(f"Streaming error: {e}", "api", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    except Exception as e:
        log_error(f"Stream setup error: {e}", "api", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections", methods=["GET"])
def get_collections():
    """Get available collections."""
    try:
        if not db_manager:
            return jsonify({"error": "Service not initialized"}), 503

        # For now, return default collection
        return jsonify(
            {
                "collections": ["course_materials"],
                "current": "course_materials",
                "success": True,
            }
        )
    except Exception as e:
        log_error(f"Error getting collections: {e}", "api")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/teachers/generate-questions", methods=["POST"])
def generate_questions():
    """
    Generate questions automatically from course content.

    Request body:
    {
        "module": "MODULE 1" or "all",
        "difficulty": "easy" | "medium" | "hard" | "mixed",
        "num_questions": 5,
        "question_types": ["multiple-choice", "true-false", "short-answer", "explain"]
    }
    """
    try:
        data = request.json
        module = data.get("module", "all")
        difficulty = data.get("difficulty", "mixed")
        num_questions = data.get("num_questions", 5)
        question_types = data.get("question_types", ["multiple-choice"])

        log_info(
            f"Generating {num_questions} questions for module: {module}, "
            f"difficulty: {difficulty}, types: {question_types}",
            "api",
        )

        # Retrieve relevant course content
        if module == "all":
            query = "data structures algorithms course content"
        else:
            query = f"{module} content topics concepts"

        # Get more context for question generation
        course_chunks = db_manager.search_with_cache(
            query, k=min(num_questions * 2, 10)
        )

        if not course_chunks:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No course content found for question generation",
                    }
                ),
                404,
            )

        # Prepare context from course materials
        context = "\n\n".join(
            [
                f"SECTION: {chunk.metadata.get('module', 'Unknown')}\n{chunk.page_content}"
                for chunk in course_chunks
            ]
        )

        # Build prompt for question generation
        type_instructions = {
            "multiple-choice": "multiple choice questions with 4 options (A, B, C, D)",
            "true-false": "true/false questions",
            "short-answer": "short answer questions requiring 1-2 sentence responses",
            "explain": "explanation questions asking to describe or explain concepts",
        }

        selected_types = [
            type_instructions[t] for t in question_types if t in type_instructions
        ]
        types_text = ", ".join(selected_types)

        difficulty_guidance = {
            "easy": "Basic recall and understanding level questions",
            "medium": "Application and analysis level questions",
            "hard": "Advanced synthesis and evaluation level questions",
            "mixed": "Mix of easy, medium, and hard questions",
        }

        prompt = f"""You are an expert educator creating assessment questions for a Data Structures course.

COURSE CONTENT:
{context}

TASK: Generate {num_questions} high-quality assessment questions.

REQUIREMENTS:
- Question Types: {types_text}
- Difficulty Level: {difficulty_guidance[difficulty]}
- Module Focus: {module if module != 'all' else 'All course modules'}
- Questions must be clear, unambiguous, and directly related to the course content above
- For multiple choice: provide exactly 4 options with clear correct answer
- For true/false: provide clear reasoning for the answer
- Questions should test conceptual understanding, not just memorization

CRITICAL: You MUST respond with ONLY valid JSON - no markdown, no explanation, no code blocks.
Start your response with [ and end with ]

FORMAT (JSON only):
[
  {{
    "question": "What is the time complexity of...",
    "type": "multiple-choice",
    "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
    "answer": "O(n)",
    "difficulty": "medium",
    "module": "{module if module != 'all' else 'General'}"
  }}
]

Generate exactly {num_questions} questions. JSON ONLY - no other text:"""

        # Generate questions using LLM
        log_info("Sending prompt to LLM for question generation", "api")
        response = model_manager.generate_response(prompt)

        if not response:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No response from LLM. Please check if Ollama is running.",
                    }
                ),
                500,
            )

        log_info(f"LLM Response (first 300 chars): {response[:300]}", "api")

        # Parse JSON response with multiple strategies
        questions = []
        import re

        # Strategy 1: Clean markdown and parse as JSON array
        try:
            response_clean = response.strip()
            response_clean = re.sub(
                r"^```json\s*", "", response_clean, flags=re.IGNORECASE
            )
            response_clean = re.sub(r"^```\s*", "", response_clean)
            response_clean = re.sub(r"\s*```$", "", response_clean)

            json_match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", response_clean)
            if json_match:
                json_str = json_match.group()
                questions = json.loads(json_str)

                if not isinstance(questions, list):
                    questions = []
                else:
                    log_info(
                        f"Strategy 1 SUCCESS: Parsed {len(questions)} questions", "api"
                    )
        except Exception as e:
            log_error(f"Strategy 1 failed: {e}", "api")

        # Strategy 2: Try parsing entire cleaned response
        if not questions:
            try:
                questions = json.loads(response_clean)
                if isinstance(questions, list):
                    log_info(
                        f"Strategy 2 SUCCESS: Parsed {len(questions)} questions", "api"
                    )
                else:
                    questions = []
            except Exception as e:
                log_error(f"Strategy 2 failed: {e}", "api")

        # Strategy 3: Extract individual question objects
        if not questions:
            try:
                question_pattern = r'\{[^{}]*"question"[^{}]*"answer"[^{}]*\}'
                matches = re.finditer(question_pattern, response, re.DOTALL)

                for match in matches:
                    try:
                        q = json.loads(match.group())
                        if "question" in q and "answer" in q:
                            questions.append(q)
                    except:
                        continue

                if questions:
                    log_info(
                        f"Strategy 3 SUCCESS: Extracted {len(questions)} questions",
                        "api",
                    )
            except Exception as e:
                log_error(f"Strategy 3 failed: {e}", "api")

        # If we successfully parsed questions
        if questions:
            log_info(f"Successfully generated {len(questions)} questions", "api")

            return jsonify(
                {"success": True, "questions": questions, "count": len(questions)}
            )

        # All parsing strategies failed
        log_error(f"All parsing strategies failed", "api")
        log_error(f"Raw response (first 1000 chars): {response[:1000]}", "api")

        return (
            jsonify(
                {
                    "success": False,
                    "error": "Failed to parse generated questions from LLM",
                    "raw_response": response[:1000],
                    "hint": "The LLM may have generated an invalid format. Try again with different settings.",
                    "strategies_tried": [
                        "JSON array extraction",
                        "Direct JSON parse",
                        "Individual object extraction",
                    ],
                }
            ),
            500,
        )

    except Exception as e:
        log_error(f"Error generating questions: {e}", "api", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/teachers/generate-questions/stream", methods=["POST"])
def generate_questions_stream():
    """
    Stream questions as they're generated for real-time display.
    Uses Server-Sent Events (SSE) for streaming.
    """
    try:
        data = request.json
        module = data.get("module", "all")
        difficulty = data.get("difficulty", "mixed")
        num_questions = data.get("num_questions", 5)
        question_types = data.get("question_types", ["multiple-choice"])

        log_info(
            f"Streaming {num_questions} questions for module: {module}",
            "api",
        )

        def generate_stream():
            """Generator function for SSE streaming."""
            try:
                # Retrieve relevant course content
                if module == "all":
                    query = "data structures algorithms course content"
                else:
                    query = f"{module} content topics concepts"

                # Send initial status
                yield f"data: {json.dumps({'type': 'status', 'message': 'Searching course materials...'})}\n\n"

                course_chunks = db_manager.search_with_cache(
                    query, k=min(num_questions * 2, 10)
                )

                if not course_chunks:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'No course content found'})}\n\n"
                    return

                # Prepare context
                context = "\n\n".join(
                    [
                        f"SECTION: {chunk.metadata.get('module', 'Unknown')}\n{chunk.page_content}"
                        for chunk in course_chunks
                    ]
                )

                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating questions...'})}\n\n"

                # Build prompt for streaming
                type_instructions = {
                    "multiple-choice": "multiple choice questions with 4 options",
                    "true-false": "true/false questions",
                    "short-answer": "short answer questions",
                    "explain": "explanation questions",
                }

                selected_types = [
                    type_instructions[t]
                    for t in question_types
                    if t in type_instructions
                ]
                types_text = ", ".join(selected_types)

                difficulty_guidance = {
                    "easy": "Basic recall level",
                    "medium": "Application level",
                    "hard": "Advanced synthesis level",
                    "mixed": "Mix of easy, medium, and hard",
                }

                # Use non-streaming API but send questions as they're generated
                # Generate all questions at once, then stream them to client
                prompt = f"""You are an expert educator creating assessment questions for a Data Structures course.

COURSE CONTENT:
{context[:2000]}

TASK: Generate {num_questions} high-quality assessment questions.

REQUIREMENTS:
- Question Types: {types_text}
- Difficulty Level: {difficulty_guidance[difficulty]}
- Module Focus: {module if module != 'all' else 'All course modules'}
- Questions must be clear, unambiguous, and directly related to the course content above
- For multiple choice: provide exactly 4 options with clear correct answer
- For true/false: provide clear reasoning for the answer
- Questions should test conceptual understanding, not just memorization

CRITICAL: You MUST respond with ONLY valid JSON - no markdown, no explanation, no code blocks.
Start your response with [ and end with ]

FORMAT (JSON only):
[
  {{
    "question": "What is...",
    "type": "multiple-choice",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A",
    "difficulty": "medium",
    "module": "{module if module != 'all' else 'General'}"
  }}
]

Generate exactly {num_questions} questions. JSON ONLY - no other text:"""

                # Generate questions (this happens in one call)
                response = model_manager.generate_response(prompt)

                if not response:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'No response from LLM'})}\n\n"
                    return

                log_info(f"LLM Response (first 500 chars): {response[:500]}", "api")

                # Parse and stream questions one by one
                import re

                questions = []

                # Strategy 1: Clean and parse as JSON array
                try:
                    response_clean = response.strip()
                    # Remove markdown code blocks
                    response_clean = re.sub(
                        r"^```json\s*", "", response_clean, flags=re.IGNORECASE
                    )
                    response_clean = re.sub(r"^```\s*", "", response_clean)
                    response_clean = re.sub(r"\s*```$", "", response_clean)

                    # Try to extract JSON array
                    json_match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", response_clean)
                    if json_match:
                        json_str = json_match.group()
                        questions = json.loads(json_str)
                        log_info(
                            f"Strategy 1 SUCCESS: Parsed {len(questions)} questions",
                            "api",
                        )
                except Exception as e:
                    log_error(f"Strategy 1 failed: {e}", "api")

                # Strategy 2: Try parsing entire cleaned response
                if not questions:
                    try:
                        questions = json.loads(response_clean)
                        if isinstance(questions, list):
                            log_info(
                                f"Strategy 2 SUCCESS: Parsed {len(questions)} questions",
                                "api",
                            )
                        else:
                            questions = []
                    except Exception as e:
                        log_error(f"Strategy 2 failed: {e}", "api")

                # Strategy 3: Extract individual question objects
                if not questions:
                    try:
                        # Find all JSON objects that look like questions
                        question_pattern = r'\{[^{}]*"question"[^{}]*"answer"[^{}]*\}'
                        matches = re.finditer(question_pattern, response, re.DOTALL)

                        for match in matches:
                            try:
                                q = json.loads(match.group())
                                if "question" in q and "answer" in q:
                                    questions.append(q)
                            except:
                                continue

                        if questions:
                            log_info(
                                f"Strategy 3 SUCCESS: Extracted {len(questions)} questions",
                                "api",
                            )
                    except Exception as e:
                        log_error(f"Strategy 3 failed: {e}", "api")

                # If we got questions, stream them
                if questions:
                    for idx, question in enumerate(questions, 1):
                        # Ensure required fields
                        if "question" not in question or "answer" not in question:
                            continue

                        # Set defaults for missing fields
                        question.setdefault("type", "short-answer")
                        question.setdefault("difficulty", difficulty)
                        question.setdefault(
                            "module", module if module != "all" else "General"
                        )

                        yield f"data: {json.dumps({'type': 'question', 'data': question, 'index': idx})}\n\n"
                        time.sleep(0.3)  # Small delay for visual effect

                    # Send completion
                    yield f"data: {json.dumps({'type': 'complete', 'total': len(questions)})}\n\n"
                else:
                    # All strategies failed
                    log_error(
                        f"All parsing strategies failed. Raw response: {response[:1000]}",
                        "api",
                    )
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to parse questions. LLM may have generated invalid format. Please try again.', 'raw': response[:500]})}\n\n"

            except Exception as e:
                log_error(f"Error in streaming generation: {e}", "api", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        log_error(f"Error setting up stream: {e}", "api", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Starting BanglaRAG Chatbot API...")

    if initialize_services():
        print("✅ Services initialized successfully")
        print("🌐 API running at http://localhost:5000")
        print("📡 Endpoints:")
        print("   - GET  /api/health")
        print("   - GET  /api/models")
        print("   - POST /api/set-model")
        print("   - POST /api/chat")
        print("   - POST /api/chat/stream (SSE)")
        print("   - GET  /api/collections")
        print("   - POST /api/teachers/generate-questions")
        print("   - POST /api/teachers/generate-questions/stream (SSE) ⚡")
        print("\n📄 Pages:")
        print("   - GET  /         (Student chatbot)")
        print("   - GET  /teachers (Teachers dashboard with real-time generation)")
        print("\n🎤 Ready to receive requests!")

        app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
    else:
        print("❌ Failed to initialize services")
        sys.exit(1)
