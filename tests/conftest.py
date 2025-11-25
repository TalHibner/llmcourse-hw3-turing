"""Shared pytest fixtures and configuration."""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Get test data directory."""
    return project_root / "tests" / "data"


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_env():
    """Provide mock environment variables."""
    original_env = os.environ.copy()

    # Set test environment variables
    test_env = {
        'ANTHROPIC_API_KEY': 'test_anthropic_key_12345',
        'OPENAI_API_KEY': 'test_openai_key_67890'
    }

    os.environ.update(test_env)

    yield test_env

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_english_text():
    """Provide sample English text for testing."""
    return "The quick brown fox jumps over the lazy dog while carrying a package."


@pytest.fixture
def sample_french_text():
    """Provide sample French text for testing."""
    return "Le renard brun rapide saute par-dessus le chien paresseux."


@pytest.fixture
def sample_hebrew_text():
    """Provide sample Hebrew text for testing."""
    return "השועל החום המהיר קופץ מעל הכלב העצלן."


@pytest.fixture
def sample_sentences():
    """Provide multiple sample sentences for testing."""
    return [
        "The weather is beautiful today with clear blue skies and warm sunshine everywhere.",
        "Scientists have discovered a new species of deep sea creatures near volcanic vents.",
        "Technology continues to evolve rapidly changing the way we communicate and work together.",
        "The ancient castle stood majestically on the hilltop overlooking the peaceful valley below."
    ]


@pytest.fixture
def sample_error_rates():
    """Provide standard error rates for testing."""
    return [0.0, 0.1, 0.25, 0.375, 0.5]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API access"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark integration tests
        if "test_pipeline" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Mark API tests
        if "api" in item.nodeid.lower() or "pipeline" in item.nodeid:
            item.add_marker(pytest.mark.api)

        # Mark slow tests
        if any(keyword in item.nodeid for keyword in ["embeddings", "pipeline", "integration"]):
            item.add_marker(pytest.mark.slow)
