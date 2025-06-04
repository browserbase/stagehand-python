import asyncio
import importlib
import inspect
import os

from .env_loader import load_evals_env

# Load environment variables at module import time
load_evals_env()

# A simple logger to collect logs for the evals
class SimpleLogger:
    def __init__(self):
        self._logs = []

    def info(self, message):
        self._logs.append(message)
        print("INFO:", message)

    def error(self, message):
        self._logs.append(message)
        print("ERROR:", message)

    def get_logs(self):
        return self._logs


async def run_all_evals(only_observe=True, model_name=None, specific_eval=None):
    """
    Run all evaluation functions found in the evals directory structure.

    Args:
        only_observe: If True, only run evaluations in the observe directory
        model_name: Model name to use (defaults to environment variable or gpt-4o)
        specific_eval: If provided, only run this specific eval (e.g. "observe_taxes")

    Returns:
        Dictionary mapping module names to evaluation results
    """
    eval_functions = {}
    # The base path is the directory in which this file resides (i.e. the evals folder)
    base_path = os.path.dirname(__file__)
    # Determine which directories to process
    allowed_dirs = {"observe"} if only_observe else {"act", "extract", "observe"}

    if specific_eval:
        print(f"Running specific eval: {specific_eval}")
    else:
        print(f"Running evaluations from these directories: {', '.join(allowed_dirs)}")

    # For specific eval, extract subdirectory
    specific_dir = None
    specific_file = None
    if specific_eval:
        if specific_eval.startswith("observe_"):
            specific_dir = "observe"
            specific_file = f"{specific_eval}.py"
        elif specific_eval.startswith("act_"):
            specific_dir = "act"
            specific_file = f"{specific_eval}.py"
        elif specific_eval.startswith("extract_"):
            specific_dir = "extract"
            specific_file = f"{specific_eval}.py"
        else:
            # Try to infer the directory from the eval name
            if "observe" in specific_eval:
                specific_dir = "observe"
            elif "act" in specific_eval:
                specific_dir = "act"
            elif "extract" in specific_eval:
                specific_dir = "extract"
            else:
                print(
                    f"Warning: Could not determine directory for {specific_eval}, will search all allowed directories"
                )

            # Add .py extension if needed
            specific_file = (
                f"{specific_eval}.py"
                if not specific_eval.endswith(".py")
                else specific_eval
            )

    # Recursively walk through the evals directory and its children
    for root, _, files in os.walk(base_path):
        # Determine the relative path from the base
        rel_path = os.path.relpath(root, base_path)
        # Skip the base folder itself
        if rel_path == ".":
            continue
        # Only process directories that start with an allowed subdirectory
        first_dir = rel_path.split(os.sep)[0]
        if first_dir not in allowed_dirs:
            continue

        # If specific dir is specified, only process that directory
        if specific_dir and first_dir != specific_dir:
            continue

        for file in files:
            # Skip __init__.py and the runner itself
            if file.endswith(".py") and file not in (
                "__init__.py",
                "run_all_evals.py",
                "test_observe.py",
            ):
                # If specific file is specified, only process that file
                if specific_file and file != specific_file:
                    continue

                # Build module import path relative to the package root (assumes folder "evals")
                if rel_path == ".":
                    module_path = f"evals.{file[:-3]}"
                else:
                    # Replace OS-specific path separators with dots ('.')
                    module_path = f"evals.{rel_path.replace(os.sep, '.')}.{file[:-3]}"
                try:
                    module = importlib.import_module(module_path)
                except Exception as e:
                    print(f"Skipping module {module_path} due to import error: {e}")
                    continue
                # The convention is that the main eval function has the same name as the file
                func_name = file[:-3]
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    if inspect.iscoroutinefunction(func):
                        eval_functions[module_path] = func

    if not eval_functions:
        if specific_eval:
            print(f"Error: No evaluation function found for {specific_eval}")
        else:
            print("Error: No evaluation functions found")
        return {}

    print("Collected eval functions:")
    for name in eval_functions:
        print(" -", name)

    results = {}
    logger = SimpleLogger()

    # Determine model name to use
    if not model_name:
        model_name = os.getenv("MODEL_NAME") or os.getenv("OPENAI_MODEL") or "gpt-4o"
    print(f"Using model: {model_name}")

    # Check if required environment variables are set
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("MODEL_API_KEY"):
        print(
            "WARNING: Neither OPENAI_API_KEY nor MODEL_API_KEY environment variables are set"
        )

    # In LOCAL mode, we need to check if required env variables are set
    if not os.getenv("BROWSERBASE_API_KEY") or not os.getenv("BROWSERBASE_PROJECT_ID"):
        print(
            "Running in LOCAL mode (no BROWSERBASE_API_KEY or BROWSERBASE_PROJECT_ID set)"
        )
        if not os.getenv("OPENAI_API_KEY"):
            print("WARNING: OPENAI_API_KEY is required for LOCAL mode")

    # Run each eval function. If the function signature includes "use_text_extract", pass a default value.
    for module_path, func in eval_functions.items():
        print(f"\n----- Running {module_path} -----")
        try:
            sig = inspect.signature(func)
            if "use_text_extract" in sig.parameters:
                result = await func(model_name, logger, False)
            else:
                result = await func(model_name, logger)
            results[module_path] = result
            print(f"Result: {'SUCCESS' if result.get('_success') else 'FAILURE'}")
        except Exception as e:
            print(f"Error running {module_path}: {e}")
            results[module_path] = {"_success": False, "error": str(e)}

    return results


if __name__ == "__main__":
    import argparse

    from evals.utils import setup_environment

    # Set up the environment
    setup_environment()

    parser = argparse.ArgumentParser(description="Run Stagehand evaluations")
    parser.add_argument("--model", type=str, help="Model name to use")
    parser.add_argument(
        "--all", action="store_true", help="Run all eval types (not just observe)"
    )
    parser.add_argument(
        "--eval", type=str, help="Run a specific eval by name (e.g., observe_taxes)"
    )
    args = parser.parse_args()

    final_results = asyncio.run(
        run_all_evals(
            only_observe=not args.all, model_name=args.model, specific_eval=args.eval
        )
    )

    # Print summary of results
    print("\n\n===== Evaluation Results Summary =====")
    successes = sum(1 for res in final_results.values() if res.get("_success"))
    total = len(final_results)
    print(f"Total: {total}, Successful: {successes}, Failed: {total - successes}")

    for module, res in final_results.items():
        status = "SUCCESS" if res.get("_success") else "FAILURE"
        error = (
            f": {res.get('error')}"
            if not res.get("_success") and "error" in res
            else ""
        )
        print(f"{module}: {status}{error}")
