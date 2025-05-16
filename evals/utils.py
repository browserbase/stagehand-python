import difflib
import os
import sys
from typing import Any, Optional

from .env_loader import load_evals_env

# Try to import LiteLLM, which is used for model inference
try:
    import litellm
except ImportError:
    litellm = None


class SimpleModelClient:
    """A simple wrapper around LiteLLM for model inference."""

    def __init__(self, model_name: str):
        """
        Initialize a simple model client.

        Args:
            model_name: The name of the model to use
        """
        self.model_name = model_name

        # Check if LiteLLM is available
        if litellm is None:
            print("WARNING: LiteLLM not installed. Run: pip install litellm>=0.1.1")

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """
        Generate a completion for the given prompt.

        Args:
            prompt: The prompt to generate a completion for
            system_prompt: Optional system prompt to use
            temperature: Temperature parameter (controls randomness)
            max_tokens: Maximum number of tokens to generate

        Returns:
            dictionary with completion results, including 'text' key
        """
        if litellm is None:
            raise ImportError(
                "LiteLLM is required for completion. Install with: pip install litellm"
            )

        # Ensure LiteLLM has an API key
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("MODEL_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY or MODEL_API_KEY environment variable must be set"
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await litellm.acompletion(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Format response like the Stagehand LLM client expects
            return {
                "text": response["choices"][0]["message"]["content"],
                "model": self.model_name,
                "finish_reason": response["choices"][0].get("finish_reason", "stop"),
                "raw_response": response,
            }
        except Exception as e:
            print(f"Error during model completion: {e}", file=sys.stderr)
            # Return a minimal response with error info
            return {
                "text": f"Error: {str(e)}",
                "model": self.model_name,
                "error": str(e),
            }


def setup_environment():
    """Set up the environment for running evaluations."""
    # First, load environment variables from .env files
    load_evals_env()
    
    # If OPENAI_API_KEY is set but MODEL_API_KEY is not, copy it over
    if os.getenv("OPENAI_API_KEY") and not os.getenv("MODEL_API_KEY"):
        os.environ["MODEL_API_KEY"] = os.getenv("OPENAI_API_KEY")

    # If MODEL_API_KEY is set but OPENAI_API_KEY is not, copy it over
    if os.getenv("MODEL_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("MODEL_API_KEY")

    # Check for required dependencies
    try:
        import litellm  # noqa: F401

        print("LiteLLM is available for LOCAL mode")
    except ImportError:
        print(
            "WARNING: LiteLLM not installed. LOCAL mode requires it for model inference."
        )
        print("Install with: pip install litellm>=0.1.1")


def compare_strings(a: str, b: str) -> float:
    """
    Compare two strings and return a similarity ratio.
    This function uses difflib.SequenceMatcher to calculate the similarity between two strings.
    """
    return difflib.SequenceMatcher(None, a, b).ratio()


def ensure_stagehand_config(stagehand):
    """
    Ensures the stagehand instance has a config attribute.
    This is a workaround for an issue where stagehand created using the constructor directly
    (not via StagehandConfig) doesn't have a config attribute.

    Args:
        stagehand: The Stagehand instance to check/modify

    Returns:
        The stagehand instance with guaranteed config attribute
    """
    print(f"DEBUG ensure_stagehand_config: Input type: {type(stagehand)}")
    print(f"DEBUG ensure_stagehand_config: Input dir: {dir(stagehand)}")
    print(
        f"DEBUG ensure_stagehand_config: Has config before: {hasattr(stagehand, 'config')}"
    )

    try:
        if not hasattr(stagehand, "config"):
            print("DEBUG ensure_stagehand_config: Creating config attribute")

            # Try to safely access attributes needed for config
            model_name = getattr(
                stagehand, "model_name", "gpt-4o"
            )  # Provide default if not found
            dom_settle_timeout_ms = getattr(stagehand, "dom_settle_timeout_ms", 3000)
            env = getattr(stagehand, "env", "LOCAL")

            print(
                f"DEBUG ensure_stagehand_config: Using model_name={model_name}, dom_settle_timeout_ms={dom_settle_timeout_ms}, env={env}"
            )

            # Create a simple config property with the necessary values from the stagehand object
            stagehand.config = type(
                "StagehandConfig",
                (),
                {
                    "model_name": model_name,
                    "dom_settle_timeout_ms": dom_settle_timeout_ms,
                    "env": env,
                },
            )

            print(
                f"DEBUG ensure_stagehand_config: Verify creation - has config after: {hasattr(stagehand, 'config')}"
            )
    except Exception as e:
        print(f"ERROR in ensure_stagehand_config: {str(e)}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")

    return stagehand
