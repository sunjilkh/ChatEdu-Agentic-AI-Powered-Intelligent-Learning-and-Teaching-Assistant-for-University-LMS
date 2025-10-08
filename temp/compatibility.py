#!/usr/bin/env python3
"""
Compatibility wrapper for BanglaRAG system.
Provides backward compatibility with existing code while using new architecture.
"""

import warnings
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Try to import from new architecture
    from services import (
        get_embedding_function_with_fallback, get_mixed_language_embedding,
        detect_language, embed_english, embed_bangla,
        load_database, query_database, create_or_update_database,
        query_ollama, get_available_models, test_ollama_connection,
        record_voice_input, transcribe_audio_file
    )
    
    from core import BanglaRAGLogger
    logger = BanglaRAGLogger.get_logger("compatibility")
    logger.info("Using new refactored architecture")
    
    # Re-export all functions for backward compatibility
    __all__ = [
        'get_embedding_function_with_fallback', 'get_mixed_language_embedding',
        'detect_language', 'embed_english', 'embed_bangla',
        'load_database', 'query_database', 'create_or_update_database',
        'query_ollama', 'get_available_models', 'test_ollama_connection',
        'record_voice_input', 'transcribe_audio_file'
    ]
    
except ImportError as e:
    # Fallback to original modules
    warnings.warn(f"New architecture not available, using original modules: {e}")
    
    # Import from original modules
    try:
        from embedding import (
            get_embedding_function_with_fallback, get_mixed_language_embedding,
            detect_language, embed_english, embed_bangla
        )
    except ImportError:
        pass
    
    try:
        from query_database import load_database, query_database
        from create_database import create_or_update_database
    except ImportError:
        pass
    
    try:
        from ollama_llm import query_ollama, get_available_models, test_ollama_connection
    except ImportError:
        pass
    
    try:
        from voice_input import record_voice_input, transcribe_audio_file
    except ImportError:
        pass


# Additional helper functions for migration
def check_new_architecture_availability():
    """Check if new architecture is available and working."""
    try:
        from services import get_model_manager
        manager = get_model_manager()
        return True
    except Exception:
        return False


def migrate_to_new_architecture():
    """Helper function to migrate existing code to new architecture."""
    if check_new_architecture_availability():
        print("✅ New architecture is available and working")
        print("🔄 Consider updating your imports to use the new services module")
        return True
    else:
        print("⚠️  New architecture not fully available, using compatibility mode")
        return False
