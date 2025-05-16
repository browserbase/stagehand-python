"""
Environment variable loader for Stagehand evaluations.

This module loads environment variables from an .env file in the evals directory,
making them available to all submodules (act, extract, observe).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_evals_env():
    """
    Load environment variables from the .env file in the evals directory.
    This ensures all submodules have access to the same environment variables.
    """
    # Get the evals directory path (where this file is located)
    evals_dir = Path(__file__).parent.absolute()
    env_path = evals_dir / '.env'
    
    # Load from root directory as fallback if evals/.env doesn't exist
    root_env_path = evals_dir.parent / '.env'
    
    # First try to load from evals/.env
    if env_path.exists():
        print(f"Loading environment variables from {env_path}")
        load_dotenv(env_path)
    # Fall back to root .env file if it exists
    elif root_env_path.exists():
        print(f"Loading environment variables from {root_env_path}")
        load_dotenv(root_env_path)
    else:
        print("No .env file found. Please create one in the evals directory.")
        print("Required variables: MODEL_API_KEY, BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID")

    # Check for essential environment variables
    essential_vars = ['MODEL_API_KEY', 'BROWSERBASE_API_KEY', 'BROWSERBASE_PROJECT_ID']
    missing_vars = [var for var in essential_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing essential environment variables: {', '.join(missing_vars)}")
        print("Some evaluations may fail without these variables.") 