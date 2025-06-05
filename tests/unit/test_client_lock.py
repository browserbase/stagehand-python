import asyncio
import unittest.mock as mock
import os

import pytest
import pytest_asyncio

from stagehand.client import Stagehand


class TestClientLock:
    """Tests for the client-side locking mechanism in the Stagehand client."""

    @pytest_asyncio.fixture
    async def mock_stagehand(self):
        """Create a mock Stagehand instance for testing."""
        with mock.patch.dict(os.environ, {}, clear=True):
            stagehand = Stagehand(
                api_url="http://localhost:8000",
                session_id="test-session-id",
                browserbase_api_key="test-api-key",
                browserbase_project_id="test-project-id",
                env="LOCAL",  # Avoid BROWSERBASE validation
            )
            # Mock the _execute method to avoid actual API calls
            stagehand._execute = mock.AsyncMock(return_value={"result": "success"})
            yield stagehand

    @pytest.mark.asyncio
    async def test_lock_creation(self, mock_stagehand):
        """Test that locks are properly created for session IDs."""
        # Clear any existing locks first
        Stagehand._session_locks.clear()

        # Get lock for session
        lock = mock_stagehand._get_lock_for_session()

        # Verify lock was created
        assert "test-session-id" in Stagehand._session_locks
        assert isinstance(lock, asyncio.Lock)

        # Get lock again, should be the same lock
        lock2 = mock_stagehand._get_lock_for_session()
        assert lock is lock2  # Same lock object

    @pytest.mark.asyncio
    async def test_lock_per_session(self):
        """Test that different sessions get different locks."""
        # Clear any existing locks first
        Stagehand._session_locks.clear()
        
        with mock.patch.dict(os.environ, {}, clear=True):
            stagehand1 = Stagehand(
                api_url="http://localhost:8000",
                session_id="session-1",
                browserbase_api_key="test-api-key",
                browserbase_project_id="test-project-id",
                env="LOCAL",
            )

            stagehand2 = Stagehand(
                api_url="http://localhost:8000",
                session_id="session-2",
                browserbase_api_key="test-api-key",
                browserbase_project_id="test-project-id",
                env="LOCAL",
            )

            lock1 = stagehand1._get_lock_for_session()
            lock2 = stagehand2._get_lock_for_session()

            # Different sessions should have different locks
            assert lock1 is not lock2

            # Both sessions should have locks in the class-level dict
            assert "session-1" in Stagehand._session_locks
            assert "session-2" in Stagehand._session_locks

    @pytest.mark.asyncio
    async def test_concurrent_access(self, mock_stagehand):
        """Test that concurrent operations are properly serialized."""
        # Use a counter to track execution order
        execution_order = []

        async def task1():
            async with mock_stagehand._get_lock_for_session():
                execution_order.append("task1 start")
                # Simulate work
                await asyncio.sleep(0.1)
                execution_order.append("task1 end")

        async def task2():
            async with mock_stagehand._get_lock_for_session():
                execution_order.append("task2 start")
                await asyncio.sleep(0.05)
                execution_order.append("task2 end")

        # Start task2 first, but it should wait for task1 to complete
        task1_future = asyncio.create_task(task1())
        await asyncio.sleep(0.01)  # Ensure task1 gets lock first
        task2_future = asyncio.create_task(task2())

        # Wait for both tasks to complete
        await asyncio.gather(task1_future, task2_future)

        # Check execution order - tasks should not interleave
        assert execution_order == [
            "task1 start",
            "task1 end",
            "task2 start",
            "task2 end",
        ]

    @pytest.mark.asyncio
    async def test_lock_with_api_methods(self, mock_stagehand):
        """Test that the lock is used with API methods."""
        # Replace _get_lock_for_session with a mock to track calls
        original_get_lock = mock_stagehand._get_lock_for_session
        mock_stagehand._get_lock_for_session = mock.MagicMock(
            return_value=original_get_lock()
        )

        # Mock the _execute method
        mock_stagehand._execute = mock.AsyncMock(return_value={"success": True})

        # Create a real StagehandPage instead of a mock
        from stagehand.page import StagehandPage

        # Create a page with the navigate method from StagehandPage
        class TestPage(StagehandPage):
            def __init__(self, stagehand):
                self._stagehand = stagehand

            async def navigate(self, url, **kwargs):
                lock = self._stagehand._get_lock_for_session()
                async with lock:
                    return await self._stagehand._execute("navigate", {"url": url})

        # Use our test page
        mock_stagehand.page = TestPage(mock_stagehand)

        # Call navigate which should use the lock
        await mock_stagehand.page.navigate("https://example.com")

        # Verify the lock was accessed
        mock_stagehand._get_lock_for_session.assert_called_once()

        # Verify the _execute method was called
        mock_stagehand._execute.assert_called_once_with(
            "navigate", {"url": "https://example.com"}
        )

    @pytest.mark.asyncio
    async def test_lock_exception_handling(self, mock_stagehand):
        """Test that exceptions inside the lock context are handled properly."""
        # Use a counter to track execution
        execution_order = []

        async def failing_task():
            try:
                async with mock_stagehand._get_lock_for_session():
                    execution_order.append("task started")
                    raise ValueError("Simulated error")
            except ValueError:
                execution_order.append("error caught")

        async def following_task():
            async with mock_stagehand._get_lock_for_session():
                execution_order.append("following task")

        # Run the failing task
        await failing_task()

        # The following task should still be able to acquire the lock
        await following_task()

        # Verify execution order
        assert execution_order == ["task started", "error caught", "following task"]

        # Verify the lock is not held
        assert not mock_stagehand._get_lock_for_session().locked()
