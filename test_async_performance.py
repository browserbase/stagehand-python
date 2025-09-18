"""Test script to verify async LLM calls are non-blocking"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from stagehand.llm.client import LLMClient
from stagehand.llm.inference import observe, extract


async def simulate_slow_llm_response(delay=1.0):
    """Simulate a slow LLM API response"""
    await asyncio.sleep(delay)
    return MagicMock(
        usage=MagicMock(prompt_tokens=100, completion_tokens=50),
        choices=[MagicMock(message=MagicMock(content='{"elements": []}'))]
    )


async def test_parallel_execution():
    """Test that multiple LLM calls can run in parallel"""
    print("\n🧪 Testing parallel async execution...")

    # Create mock LLM client
    mock_logger = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.error = MagicMock()

    llm_client = LLMClient(
        stagehand_logger=mock_logger,
        default_model="gpt-4o"
    )

    # Mock the async create_response to simulate delay
    async def mock_create_response(**kwargs):
        return await simulate_slow_llm_response(1.0)

    llm_client.create_response = mock_create_response

    # Measure time for parallel execution
    start_time = time.time()

    # Run 3 observe calls in parallel
    tasks = [
        observe("Find button 1", "DOM content 1", llm_client, logger=mock_logger),
        observe("Find button 2", "DOM content 2", llm_client, logger=mock_logger),
        observe("Find button 3", "DOM content 3", llm_client, logger=mock_logger),
    ]

    results = await asyncio.gather(*tasks)
    parallel_time = time.time() - start_time

    print(f"✅ Parallel execution of 3 calls took: {parallel_time:.2f}s")
    print(f"   Expected ~1s (running in parallel), not 3s (sequential)")

    # Verify results
    assert len(results) == 3
    for i, result in enumerate(results, 1):
        assert "elements" in result
        print(f"   Result {i}: {result}")

    # Test sequential execution for comparison
    print("\n🧪 Testing sequential execution for comparison...")
    start_time = time.time()

    result1 = await observe("Find button 1", "DOM content 1", llm_client, logger=mock_logger)
    result2 = await observe("Find button 2", "DOM content 2", llm_client, logger=mock_logger)
    result3 = await observe("Find button 3", "DOM content 3", llm_client, logger=mock_logger)

    sequential_time = time.time() - start_time
    print(f"✅ Sequential execution of 3 calls took: {sequential_time:.2f}s")
    print(f"   Expected ~3s (running sequentially)")

    # Parallel should be significantly faster
    assert parallel_time < sequential_time * 0.5, "Parallel execution should be much faster than sequential"

    print(f"\n🎉 Async implementation is working correctly!")
    print(f"   Parallel speedup: {sequential_time/parallel_time:.2f}x faster")


async def test_real_llm_async():
    """Test with real LiteLLM to ensure the async implementation works"""
    print("\n🧪 Testing with real LiteLLM (using mock responses)...")

    import litellm
    from unittest.mock import patch

    # Mock litellm.acompletion to return test data
    async def mock_acompletion(**kwargs):
        await asyncio.sleep(0.1)  # Small delay to simulate API call
        return MagicMock(
            usage=MagicMock(prompt_tokens=100, completion_tokens=50),
            choices=[MagicMock(message=MagicMock(content='{"elements": [{"selector": "#test"}]}'))]
        )

    with patch('litellm.acompletion', new=mock_acompletion):
        mock_logger = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.debug = MagicMock()
        mock_logger.error = MagicMock()

        llm_client = LLMClient(
            stagehand_logger=mock_logger,
            default_model="gpt-4o"
        )

        # Test that the actual async call works
        response = await llm_client.create_response(
            messages=[{"role": "user", "content": "test"}],
            model="gpt-4o"
        )

        assert response is not None
        print(f"✅ Real LiteLLM async call successful")
        print(f"   Response: {response.choices[0].message.content}")


async def main():
    """Run all tests"""
    print("=" * 50)
    print("ASYNC IMPLEMENTATION VERIFICATION")
    print("=" * 50)

    try:
        await test_parallel_execution()
        await test_real_llm_async()

        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED - ASYNC IS WORKING!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())