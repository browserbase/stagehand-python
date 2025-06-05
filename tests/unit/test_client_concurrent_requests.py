import asyncio
import time
import os
import unittest.mock as mock

import pytest
import pytest_asyncio

from stagehand.client import Stagehand


class TestClientConcurrentRequests:
    """Tests focused on verifying concurrent request handling with locks."""

    @pytest_asyncio.fixture
    async def real_stagehand(self):
        """Create a Stagehand instance with a mocked _execute method that simulates delays."""
        with mock.patch.dict(os.environ, {}, clear=True):
            stagehand = Stagehand(
                api_url="http://localhost:8000",
                session_id="test-concurrent-session",
                browserbase_api_key="test-api-key",
                browserbase_project_id="test-project-id",
                env="LOCAL",  # Avoid BROWSERBASE validation
            )

            # Track timestamps and method calls to verify serialization
            execution_log = []

            # Replace _execute with a version that logs timestamps
            async def logged_execute(method, payload):
                method_name = method
                start_time = time.time()
                execution_log.append(
                    {"method": method_name, "event": "start", "time": start_time}
                )

                # Simulate API delay of 100ms
                await asyncio.sleep(0.1)

                end_time = time.time()
                execution_log.append(
                    {"method": method_name, "event": "end", "time": end_time}
                )

                return {"result": f"{method_name} completed"}

            stagehand._execute = logged_execute
            stagehand.execution_log = execution_log

            yield stagehand

            # Clean up
            Stagehand._session_locks.pop("test-concurrent-session", None)

    @pytest.mark.asyncio
    async def test_concurrent_requests_serialization(self, real_stagehand):
        """Test that concurrent requests are properly serialized by the lock."""
        # Track which tasks are running in parallel
        currently_running = set()
        max_concurrent = 0

        async def make_request(name):
            nonlocal max_concurrent
            lock = real_stagehand._get_lock_for_session()
            async with lock:
                # Add this task to the currently running set
                currently_running.add(name)
                # Update max concurrent count
                max_concurrent = max(max_concurrent, len(currently_running))

                # Simulate work
                await asyncio.sleep(0.05)

                # Remove from running set
                currently_running.remove(name)

                # Execute a request
                await real_stagehand._execute(f"request_{name}", {})

        # Create 5 concurrent tasks
        tasks = [make_request(f"task_{i}") for i in range(5)]

        # Run them all concurrently
        await asyncio.gather(*tasks)

        # Verify that only one task ran at a time (max_concurrent should be 1)
        assert max_concurrent == 1, "Multiple tasks ran concurrently despite lock"

        # Verify that the execution log shows non-overlapping operations
        events = real_stagehand.execution_log

        # Check that each request's start time is after the previous request's end time
        for i in range(
            1, len(events), 2
        ):  # Start at index 1, every 2 entries (end events)
            # Next start event is at i+1
            if i + 1 < len(events):
                current_end_time = events[i]["time"]
                next_start_time = events[i + 1]["time"]

                assert next_start_time >= current_end_time, (
                    f"Request overlap detected: {events[i]['method']} ended at {current_end_time}, "
                    f"but {events[i+1]['method']} started at {next_start_time}"
                )

    @pytest.mark.asyncio
    async def test_lock_performance_overhead(self, real_stagehand):
        """Test that the lock doesn't add significant overhead."""
        start_time = time.time()

        # Make 10 sequential requests
        for i in range(10):
            await real_stagehand._execute(f"request_{i}", {})

        sequential_time = time.time() - start_time

        # Clear the log
        real_stagehand.execution_log.clear()

        # Make 10 concurrent requests through the lock
        async def make_request(i):
            lock = real_stagehand._get_lock_for_session()
            async with lock:
                await real_stagehand._execute(f"concurrent_{i}", {})

        start_time = time.time()
        tasks = [make_request(i) for i in range(10)]
        await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time

        # The concurrent time should be similar to sequential time (due to lock)
        # But not significantly more (which would indicate lock overhead)
        # Allow 20% overhead for lock management
        assert concurrent_time <= sequential_time * 1.2, (
            f"Lock adds too much overhead: sequential={sequential_time:.3f}s, "
            f"concurrent={concurrent_time:.3f}s"
        )
