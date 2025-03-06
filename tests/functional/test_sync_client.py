import os
import pytest
from dotenv import load_dotenv
from stagehand.sync.client import Stagehand
from stagehand.config import StagehandConfig
from stagehand.schemas import ActOptions, ObserveOptions, ExtractOptions

# Load environment variables
load_dotenv()


@pytest.fixture
def stagehand_client():
    """Fixture to create and manage a Stagehand client instance."""
    config = StagehandConfig(
        env=(
            "BROWSERBASE"
            if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")
            else "LOCAL"
        ),
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        debug_dom=True,
        headless=True,  # Run tests in headless mode
        dom_settle_timeout_ms=3000,
        model_name="gpt-4o-mini",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
    )

    client = Stagehand(
        config=config, server_url=os.getenv("STAGEHAND_SERVER_URL"), verbose=2
    )

    # Initialize the client
    client.init()

    yield client

    # Cleanup
    client.close()


def test_navigation(stagehand_client):
    """Test basic navigation functionality."""
    stagehand_client.page.goto("https://www.google.com")
    # Add assertions based on the page state if needed


def test_act_command(stagehand_client):
    """Test the act command functionality."""
    stagehand_client.page.goto("https://www.google.com")
    stagehand_client.page.act(ActOptions(action="search for openai"))
    # Add assertions based on the action result if needed


def test_observe_command(stagehand_client):
    """Test the observe command functionality."""
    stagehand_client.page.goto("https://www.google.com")
    result = stagehand_client.page.observe(ObserveOptions(instruction="find the search input box"))
    assert result is not None
    assert len(result) > 0
    assert hasattr(result[0], 'selector')
    assert hasattr(result[0], 'description')


def test_extract_command(stagehand_client):
    """Test the extract command functionality."""
    stagehand_client.page.goto("https://www.google.com")
    result = stagehand_client.page.extract("title")
    assert result is not None
    assert hasattr(result, 'extraction')
    assert isinstance(result.extraction, str)
    assert result.extraction is not None


def test_session_management(stagehand_client):
    """Test session management functionality."""
    assert stagehand_client.session_id is not None
    assert isinstance(stagehand_client.session_id, str)
