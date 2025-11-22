"""
Pytest configuration and fixtures for Flask/SocketIO testing
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


@pytest.fixture(scope="session")
def app_config():
    """Flask app configuration for testing"""
    return {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'MONGO_URI': 'mongodb://localhost:27017/realtimeASR_test',
        'SESSION_TYPE': 'filesystem',
    }


@pytest.fixture
def mock_models():
    """Mock ASR and translation models"""
    from unittest.mock import MagicMock
    
    return {
        'asr': MagicMock(),
        'tokenizer': MagicMock(),
        'model': MagicMock(),
    }
