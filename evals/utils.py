import difflib
import os
from .env_loader import load_evals_env


def setup_environment():
    """Set up the environment for running evaluations."""
    # Load environment variables from .env files
    load_evals_env()
    
    # If OPENAI_API_KEY is set but MODEL_API_KEY is not, copy it over
    if os.getenv("OPENAI_API_KEY") and not os.getenv("MODEL_API_KEY"):
        os.environ["MODEL_API_KEY"] = os.getenv("OPENAI_API_KEY")

    # If MODEL_API_KEY is set but OPENAI_API_KEY is not, copy it over
    if os.getenv("MODEL_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("MODEL_API_KEY")


def compare_strings(a: str, b: str) -> float:
    """
    Compare two strings and return a similarity ratio.
    This function uses difflib.SequenceMatcher to calculate the similarity between two strings.
    
    Args:
        a: First string to compare
        b: Second string to compare
        
    Returns:
        float: Similarity ratio between 0.0 and 1.0
    """
    return difflib.SequenceMatcher(None, a, b).ratio()


def validate_extraction_result(result, expected_fields=None):
    """
    Validate that an extraction result has the expected structure.
    
    Args:
        result: The extraction result to validate
        expected_fields: Optional list of fields that should be present
        
    Returns:
        bool: True if the result is valid, False otherwise
    """
    if not result:
        return False
        
    # If it's a Pydantic model, convert to dict
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    
    if not isinstance(result, dict):
        return False
    
    # Check for expected fields if provided
    if expected_fields:
        for field in expected_fields:
            if field not in result:
                return False
                
    return True
