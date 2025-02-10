import asyncio
import os
import importlib
import inspect

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

async def run_all_evals():
    eval_functions = {}
    # The base path is the directory in which this file resides (i.e. the evals folder)
    base_path = os.path.dirname(__file__)
    # Only process evals from these sub repositories
    allowed_dirs = {"act", "extract", "observe"}
    
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

        for file in files:
            # Skip __init__.py and the runner itself
            if file.endswith(".py") and file not in ("__init__.py", "run_all_evals.py"):
                # Build module import path relative to the package root (assumes folder "evals")
                if rel_path == '.':
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

    print("Collected eval functions:")
    for name in eval_functions:
        print(" -", name)

    results = {}
    logger = SimpleLogger()
    model_name = "gpt-4o"  # default model name to pass

    # Run each eval function. If the function signature includes "use_text_extract", pass a default value.
    for module_path, func in eval_functions.items():
        sig = inspect.signature(func)
        if "use_text_extract" in sig.parameters:
            result = await func(model_name, logger, False)
        else:
            result = await func(model_name, logger)
        results[module_path] = result

    return results

if __name__ == "__main__":
    final_results = asyncio.run(run_all_evals())
    print("Evaluation Results:")
    for module, res in final_results.items():
        print(f"{module}: {res}") 