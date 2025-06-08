import pytest
import pytest_asyncio

from stagehand import Stagehand, StagehandConfig


@pytest_asyncio.fixture(scope="module")
async def stagehand_local():
    """Provide a lightweight Stagehand instance running in LOCAL mode for integration tests."""
    config = StagehandConfig(env="LOCAL", headless=True, verbose=0)
    sh = Stagehand(config=config)
    await sh.init()
    yield sh
    await sh.close()


@pytest.mark.integration
@pytest.mark.local
@pytest.mark.asyncio
async def test_stagehand_local_initialization(stagehand_local):
    """Ensure that Stagehand initializes correctly in LOCAL mode."""
    assert stagehand_local._initialized is True


@pytest.mark.integration
@pytest.mark.local
@pytest.mark.asyncio
async def test_local_observe_and_act_workflow(stagehand_local):
    """Test core observe and act workflow in LOCAL mode - extracted from e2e tests."""
    stagehand = stagehand_local
    
    # Navigate to a form page for testing
    await stagehand.page.goto("https://httpbin.org/forms/post")
    
    # Test OBSERVE primitive: Find form elements
    form_elements = await stagehand.page.observe("Find all form input elements")
    
    # Verify observations
    assert form_elements is not None
    assert len(form_elements) > 0
    
    # Verify observation structure
    for obs in form_elements:
        assert hasattr(obs, "selector")
        assert obs.selector  # Not empty
    
    # Test ACT primitive: Fill form fields
    await stagehand.page.act("Fill the customer name field with 'Local Integration Test'")
    await stagehand.page.act("Fill the telephone field with '555-LOCAL'")
    await stagehand.page.act("Fill the email field with 'local@integration.test'")
    
    # Verify actions worked by observing filled fields
    filled_fields = await stagehand.page.observe("Find all filled form input fields")
    assert filled_fields is not None
    assert len(filled_fields) > 0
    
    # Test interaction with specific elements
    customer_field = await stagehand.page.observe("Find the customer name input field")
    assert customer_field is not None
    assert len(customer_field) > 0 