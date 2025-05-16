#!/usr/bin/env python
"""
Stagehand Python SDK Evaluation Runner.

This script runs evaluation tests for the Stagehand Python SDK.
"""
import os
import json
import time
import argparse
import asyncio
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from dotenv import load_dotenv

from evals.run_all_evals import run_all_evals
from evals.utils import setup_environment

# Create a custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "highlight": "magenta",
    "url": "blue underline",
})

# Create a Rich console instance with our theme
console = Console(theme=custom_theme)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Stagehand Python SDK evaluations")
    parser.add_argument(
        "--eval", 
        help="Name of a specific evaluation to run (e.g., observe_taxes)",
        default=None
    )
    parser.add_argument(
        "--category", 
        help="Category of evaluations to run (act, extract, observe)",
        choices=["act", "extract", "observe"],
        default="observe"
    )
    parser.add_argument(
        "--verbose", 
        help="Verbosity level (0-3)", 
        type=int, 
        default=2
    )
    parser.add_argument(
        "--text-extract", 
        help="Use text extract instead of semantic extract", 
        action="store_true"
    )
    parser.add_argument(
        "--model",
        help="Model to use for evaluations",
        default=None
    )
    parser.add_argument(
        "--all",
        help="Run all evaluation types",
        action="store_true"
    )
    return parser.parse_args()

async def main():
    """Main async function."""
    # Parse command-line arguments
    args = parse_args()
    
    # Add a fancy header
    console.print(
        "\n",
        Panel.fit(
            "[light_gray]Stagehand 🤘 Python SDK Evaluations[/]",
            border_style="green",
            padding=(1, 10),
        ),
    )
    
    # Setup environment variables
    setup_environment()
    
    # Set verbosity level
    os.environ["VERBOSE"] = str(args.verbose)
    
    # Set text extract flag if provided
    if args.text_extract:
        os.environ["USE_TEXT_EXTRACT"] = "true"
    
    # Determine which evals to run
    only_observe = not args.all
    if args.category != "observe":
        only_observe = False
    
    # Run evaluations
    specific_eval = args.eval
    if args.category and not specific_eval:
        # If category is specified but not a specific eval, 
        # we'll include all evals from that category
        console.print(f"Running all evaluations in category: [highlight]{args.category}[/]")
    elif specific_eval:
        console.print(f"Running specific evaluation: [highlight]{specific_eval}[/]")
    else:
        console.print(f"Running {'all evaluations' if args.all else 'observe evaluations'}...")
    
    # Run the evaluations
    start_time = time.time()
    results = await run_all_evals(
        only_observe=only_observe, 
        model_name=args.model, 
        specific_eval=specific_eval
    )
    end_time = time.time()
    
    # Generate and print the summary
    console.print("\n")
    
    # Create a summary table
    table = Table(title="Evaluation Summary")
    table.add_column("Evaluation", style="cyan")
    table.add_column("Result", style="green")
    table.add_column("Error", style="red")
    
    # Count successes and failures
    successes = 0
    failures = 0
    
    for module, result in results.items():
        # Get the simplified module name (just the eval name, not the full path)
        eval_name = module.split('.')[-1]
        
        if result.get("_success"):
            status = "[success]SUCCESS[/]"
            error = ""
            successes += 1
        else:
            status = "[error]FAILURE[/]"
            error = result.get("error", "Unknown error")
            failures += 1
            
        table.add_row(eval_name, status, error)
    
    console.print(table)
    
    # Print total stats
    total = successes + failures
    success_rate = (successes / total * 100) if total > 0 else 0
    
    console.print(
        f"\nTotal evaluations: {total}, "
        f"Successful: [success]{successes}[/], "
        f"Failed: [error]{failures}[/], "
        f"Success rate: [highlight]{success_rate:.1f}%[/]"
    )
    console.print(f"Total execution time: [highlight]{end_time - start_time:.2f}s[/]")
    
    # Save results to a file
    with open("eval-results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    console.print("\nEvaluation results saved to [url]eval-results.json[/]")
    
    # Return success only if all evaluations passed
    return successes == total

if __name__ == "__main__":
    success = asyncio.run(main())
    # Exit with the appropriate code for CI integration
    exit(0 if success else 1) 