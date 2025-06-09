"""
Pytest configuration and shared test fixtures.
"""
import os
import sys
import pytest
from pathlib import Path
from typing import Generator, Any, Dict

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import application modules
from config_manager import ConfigManager
from database_utils import DatabaseManager

# Type aliases
Fixture = Generator[Any, None, None]

# Test configuration
TEST_DB_PATH = ":memory:"  # Use in-memory database for tests
TEST_CONFIG = {
    "database": {
        "url": f"sqlite:///{TEST_DB_PATH}",
        "echo": False
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Provide test configuration."""
    return TEST_CONFIG

@pytest.fixture(scope="function")
def config_manager(test_config: Dict[str, Any]) -> ConfigManager:
    """Create a ConfigManager instance with test configuration."""
    return ConfigManager(config=test_config)

@pytest.fixture(scope="function")
def db_manager(config_manager: ConfigManager) -> Generator[DatabaseManager, None, None]:
    """Create a DatabaseManager instance with a test database."""
    db = DatabaseManager(config_manager)
    
    # Set up test database
    db.initialize_database()
    
    yield db
    
    # Clean up
    db.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture(scope="function")
def test_client():
    """Create a test client for the API."""
    from fastapi.testclient import TestClient
    from api.main import app
    
    with TestClient(app) as client:
        yield client

# Mark all tests in this directory with the 'unit' marker
# This allows running just unit tests with: pytest -m unit
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
