import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme


class LogConfig:
    """
    Centralized configuration for logging across Stagehand.
    Manages log levels, formatting, and environment-specific settings.
    """

    def __init__(
        self,
        verbose: int = 1,
        use_rich: bool = True,
        env: str = "LOCAL",
        external_logger: Optional[Callable] = None,
        quiet_dependencies: bool = True,
    ):
        """
        Initialize logging configuration.

        Args:
            verbose: Verbosity level (0=error, 1=info, 2=debug)
            use_rich: Whether to use Rich for formatted output
            env: Environment ("LOCAL" or "BROWSERBASE")
            external_logger: Optional external logging callback
            quiet_dependencies: Whether to quiet noisy dependencies
        """
        self.verbose = verbose
        self.use_rich = use_rich
        self.env = env
        self.external_logger = external_logger
        self.quiet_dependencies = quiet_dependencies

    def get_remote_verbose(self) -> int:
        """
        Map local verbose levels to remote levels.
        Since we now use the same 3-level system, this is a direct mapping.
        """
        return self.verbose

    def should_log(self, level: int) -> bool:
        """Check if a message at the given level should be logged."""
        # Always log errors (level 0)
        if level == 0:
            return True
        # Otherwise check against verbose setting
        return level <= self.verbose


# Custom theme for Rich
stagehand_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "debug": "bold white",
        "category": "bold blue",
        "auxiliary": "white",
        "timestamp": "dim white",
        "success": "bold white",
        "pending": "bold yellow",
        "ellipsis": "bold white",
    }
)


def get_console(use_rich: bool = True) -> Console:
    """
    Get a console instance based on whether Rich formatting is enabled.

    Args:
        use_rich: If True, returns a console with theme. If False, returns a plain console.

    Returns:
        Console instance configured appropriately
    """
    if use_rich:
        return Console(theme=stagehand_theme)
    else:
        return Console(theme=None)


# Create default console instance with theme (for backward compatibility)
console = get_console(use_rich=True)

# Setup logging with Rich handler
logger = logging.getLogger(__name__)
# Only add handler if there isn't one already to avoid duplicate logs
if not logger.handlers:
    handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        console=console,
        show_time=False,  # We'll add our own timestamp
        show_level=False,  # We'll format our own level
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    # Don't propagate to root logger to avoid duplicate logs
    logger.propagate = False


def configure_logging(
    level=logging.INFO,
    format_str=None,
    datefmt="%Y-%m-%d %H:%M:%S",
    quiet_dependencies=True,
    utils_level=None,
    remove_logger_name=True,
    use_rich=True,
):
    """
    Configure logging for Stagehand with sensible defaults.

    Args:
        level: The logging level for Stagehand loggers (default: INFO)
        format_str: The format string for log messages (default: depends on remove_logger_name)
        datefmt: The date format string for log timestamps
        quiet_dependencies: If True, sets httpx, httpcore, and other noisy dependencies to WARNING level
        utils_level: Optional specific level for stagehand.utils logger (default: None, uses the main level)
        remove_logger_name: If True, use a more concise log format without showing full logger name
        use_rich: If True, use Rich for colorized, pretty-printed output
    """
    # Set default format if not provided
    if format_str is None:
        if remove_logger_name:
            format_str = "%(asctime)s - %(levelname)s - %(message)s"
        else:
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger with custom format
    if use_rich:
        # Get a console with theme for Rich handler
        rich_console = get_console(use_rich=True)
        # Use Rich handler for root logger
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt=datefmt,
            handlers=[
                RichHandler(
                    rich_tracebacks=True,
                    markup=True,
                    console=rich_console,
                    show_time=False,
                    show_level=False,
                )
            ],
        )
    else:
        # Use standard handler
        logging.basicConfig(
            level=level,
            format=format_str,
            datefmt=datefmt,
        )

    # Configure Stagehand logger to use the specified level
    logging.getLogger("stagehand").setLevel(level)

    # Set specific level for utils logger if specified
    if utils_level is not None:
        logging.getLogger("stagehand.logging").setLevel(utils_level)

    # Set higher log levels for noisy dependencies
    if quiet_dependencies:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        logging.getLogger("litellm").setLevel(logging.WARNING)
        logging.getLogger("LiteLLM").setLevel(logging.WARNING)


class StagehandLogger:
    """
    Enhanced Python equivalent of the TypeScript StagehandLogger class.
    Provides structured logging with improved formatting using Rich.
    """

    def __init__(
        self,
        verbose: int = 1,
        external_logger: Optional[Callable] = None,
        use_rich: bool = True,
        config: Optional[LogConfig] = None,
    ):
        """
        Initialize the logger with specified verbosity and optional external logger.

        Args:
            verbose: Verbosity level (0=error only, 1=info, 2=debug)
            external_logger: Optional callback function for log events
            use_rich: Whether to use Rich for pretty output (default: True)
            config: Optional LogConfig instance. If provided, overrides other parameters.
        """
        if config:
            self.config = config
        else:
            self.config = LogConfig(
                verbose=verbose,
                use_rich=use_rich,
                external_logger=external_logger,
            )

        self.console = get_console(self.config.use_rich)

        # Map our verbosity levels to Python's logging levels
        self.level_map = {
            0: logging.ERROR,  # Critical errors only
            1: logging.INFO,  # Standard information
            2: logging.DEBUG,  # Debug information
        }

        # Map level to style names
        self.level_style = {0: "error", 1: "info", 2: "debug"}

        # Update logger level based on verbosity
        self._set_verbosity(self.config.verbose)

    @property
    def verbose(self):
        """Get verbose level from config"""
        return self.config.verbose

    @property
    def use_rich(self):
        """Get use_rich setting from config"""
        return self.config.use_rich

    @property
    def external_logger(self):
        """Get external logger from config"""
        return self.config.external_logger

    def _set_verbosity(self, level: int):
        """Set the logger verbosity level"""
        self.config.verbose = level
        logger.setLevel(self.level_map.get(level, logging.INFO))

    def _format_json(self, data: dict) -> str:
        """Format JSON data nicely with syntax highlighting"""
        if not self.use_rich:
            return json.dumps(data, indent=2)

        # Create a nice-looking JSON string with syntax highlighting
        json_str = json.dumps(data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)
        return syntax

    def _format_message_with_json(self, message: str) -> str:
        """
        Parse and format any JSON-like structures within a message string.
        This helps with pretty-printing log messages that contain raw JSON or Python dict representations.
        """
        # Handle case where message is already a dictionary
        if isinstance(message, dict):
            # Format the dict as JSON
            if self.use_rich:
                json_str = json.dumps(message, indent=2)
                return f"\n{json_str}"
            else:
                return json.dumps(message, indent=2)

        if not isinstance(message, str):
            # If not a string and not a dict, convert to string
            return str(message)

        import re

        # Function to replace dict-like patterns with formatted JSON
        def replace_dict(match):
            try:
                # Handle Python dictionary format by safely evaluating it
                # This converts string representation of Python dict to actual dict
                import ast

                dict_str = match.group(0)
                dict_obj = ast.literal_eval(dict_str)

                # Format the dict as JSON
                if self.use_rich:
                    json_str = json.dumps(dict_obj, indent=2)
                    return f"\n{json_str}"
                else:
                    return json.dumps(dict_obj, indent=2)
            except (SyntaxError, ValueError):
                # If parsing fails, return the original string
                return match.group(0)

        # Pattern to match Python dictionary literals
        pattern = r"(\{[^{}]*(\{[^{}]*\}[^{}]*)*\})"

        # Replace dictionary patterns with formatted JSON
        return re.sub(pattern, replace_dict, message)

    def _format_fastify_log(
        self, message: str, auxiliary: dict[str, Any] = None
    ) -> tuple:
        """
        Special formatting for logs that come from the Fastify server.
        These often contain Python representations of JSON objects.

        Returns:
            tuple: (formatted_message, formatted_auxiliary)
        """
        # Handle case where message is already a dictionary
        if isinstance(message, dict):
            # Extract the actual message and other fields
            extracted_message = message.get("message", "")
            category = message.get("category", "")

            # Format any remaining data for display
            formatted_json = json.dumps(message, indent=2)

            if self.use_rich:
                Syntax(formatted_json, "json", theme="monokai", word_wrap=True)
                if category:
                    extracted_message = f"[{category}] {extracted_message}"

                # Handle ellipses in message separately
                if "..." in extracted_message:
                    extracted_message = extracted_message.replace(
                        "...", "[ellipsis]...[/ellipsis]"
                    )

                return extracted_message, None
            else:
                if category and not extracted_message.startswith(f"[{category}]"):
                    extracted_message = f"[{category}] {extracted_message}"
                return extracted_message, None

        # Check if this appears to be a string representation of a JSON object
        elif isinstance(message, str) and (
            message.startswith("{'") or message.startswith("{")
        ):
            try:
                # Try to parse the message as a Python dict using ast.literal_eval
                # This is safer than eval() for parsing Python literal structures
                import ast

                data = ast.literal_eval(message)

                # Extract the actual message and other fields
                extracted_message = data.get("message", "")
                category = data.get("category", "")

                # Format any remaining data for display
                formatted_json = json.dumps(data, indent=2)

                if self.use_rich:
                    Syntax(formatted_json, "json", theme="monokai", word_wrap=True)
                    if category:
                        extracted_message = f"[{category}] {extracted_message}"

                    # Handle ellipses in message separately
                    if "..." in extracted_message:
                        extracted_message = extracted_message.replace(
                            "...", "[ellipsis]...[/ellipsis]"
                        )

                    return extracted_message, None
                else:
                    if category and not extracted_message.startswith(f"[{category}]"):
                        extracted_message = f"[{category}] {extracted_message}"
                    return extracted_message, None
            except (SyntaxError, ValueError):
                # If parsing fails, use the original message
                pass

        # For regular string messages that contain ellipses
        elif isinstance(message, str) and "..." in message:
            formatted_message = message.replace("...", "[ellipsis]...[/ellipsis]")
            return formatted_message, auxiliary

        # Default: return the original message and auxiliary
        return message, auxiliary

    def _format_auxiliary_compact(self, auxiliary: dict[str, Any]) -> str:
        """Format auxiliary data in a compact, readable way"""
        if not auxiliary:
            return {}

        # Clean and format the auxiliary data
        formatted = {}

        for key, value in auxiliary.items():
            # Skip internal keys in normal logging
            if key in ["requestId", "elementId", "type"]:
                continue

            # Handle nested values that come from the API
            if isinstance(value, dict) and "value" in value:
                extracted = value.get("value")
                type_info = value.get("type")

                # Skip empty values
                if not extracted:
                    continue

                # For nested objects with 'value' and 'type', use a cleaner representation
                if isinstance(extracted, (dict, list)) and type_info == "object":
                    # For complex objects, keep the whole structure
                    formatted[key] = extracted
                # Handle different types of values
                elif key in ["sessionId", "url", "sessionUrl", "debugUrl"]:
                    # Keep these values as is
                    formatted[key] = extracted
                elif isinstance(extracted, str) and len(extracted) > 40:
                    # Truncate long strings
                    formatted[key] = f"{extracted[:37]}..."
                else:
                    formatted[key] = extracted
            else:
                # Handle direct values
                formatted[key] = value

        return formatted

    def log(
        self,
        message: str,
        level: int = 1,
        category: str = None,
        auxiliary: dict[str, Any] = None,
    ):
        """
        Log a message with structured data, with Rich formatting.

        Args:
            message: The message to log
            level: Verbosity level (0=error, 1=info, 2=debug)
            category: Optional category for the message
            auxiliary: Optional dictionary of auxiliary data
        """
        # Skip logging if below current verbosity level
        if not self.config.should_log(level):
            return

        # Call external logger if provided (handle async function)
        if self.external_logger and self.external_logger is not default_log_handler:
            # Format log data similar to TS LogLine structure
            log_data = {
                "message": {"message": message, "level": level},
                "timestamp": datetime.now().isoformat(),
            }
            if category:
                log_data["category"] = category
            if auxiliary:
                log_data["auxiliary"] = auxiliary

            # Handle async callback properly
            if asyncio.iscoroutinefunction(self.external_logger):
                # Create a task but don't wait for it - this avoids blocking
                # Must be called from an async context
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.external_logger(log_data))
                    else:
                        self.external_logger(log_data)
                except RuntimeError:
                    # No event loop running, log a warning
                    self.external_logger(log_data)
            else:
                # Synchronous callback, just call directly
                self.external_logger(log_data)
            return

        # Get level style
        level_style = self.level_style.get(level, "info")

        # Check for Fastify server logs and format them specially
        formatted_message, formatted_auxiliary = self._format_fastify_log(
            message, auxiliary
        )

        # Process the auxiliary data if it wasn't handled by the Fastify formatter
        if formatted_auxiliary is None:
            aux_data = None
        else:
            # For regular messages, apply JSON formatting
            formatted_message = self._format_message_with_json(formatted_message)
            aux_data = (
                self._format_auxiliary_compact(formatted_auxiliary or auxiliary)
                if auxiliary
                else {}
            )

        # Format the log message
        if self.use_rich:
            # Format the timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Special handling for specific categories
            if category in ["action", "navigation"]:
                # Success marker for completed actions
                if (
                    "Navigated to" in formatted_message
                    or "Clicked on" in formatted_message
                ):
                    self.console.print(
                        f"[timestamp]{timestamp}[/timestamp] [success]✓[/success] {formatted_message}"
                    )
                else:
                    # Pending action marker
                    self.console.print(
                        f"[timestamp]{timestamp}[/timestamp] [pending]→[/pending] {formatted_message}"
                    )
                return

            # For captcha category, show a more compact format
            if category == "captcha":
                self.console.print(
                    f"[timestamp]{timestamp}[/timestamp] [info]⏳[/info] {formatted_message}"
                )
                return

            # Create the line prefix
            line_prefix = f"[timestamp]{timestamp}[/timestamp] [{level_style}]{level_style.upper()}[/{level_style}]"

            # Add category if present
            if category:
                line_prefix += f" [category]{category}[/category]"

            # Add the message
            log_line = f"{line_prefix} - {formatted_message}"

            # Handle ellipses in the log line
            if "..." in log_line and "[ellipsis]" not in log_line:
                log_line = log_line.replace("...", "[ellipsis]...[/ellipsis]")

            # Add auxiliary data if we have it and it's processed
            if aux_data:
                if isinstance(aux_data, dict) and len(aux_data) <= 2:
                    # Show simple data inline
                    items = []
                    for k, v in aux_data.items():
                        if isinstance(v, str) and len(v) > 50:
                            # Truncate long strings for inline display
                            items.append(f"{k}={v[:47]}...")
                        else:
                            items.append(f"{k}={v}")

                    # Add as inline content with soft styling
                    if items:
                        log_line += f" [auxiliary]({', '.join(items)})[/auxiliary]"
                elif aux_data is not None:
                    # We'll print auxiliary data separately
                    self.console.print(log_line)

                    # Create a table for structured display of auxiliary data
                    table = Table(show_header=False, box=None, padding=(0, 1, 0, 1))
                    table.add_column("Key", style="cyan")
                    table.add_column("Value")

                    for k, v in aux_data.items():
                        if isinstance(v, (dict, list)):
                            # Format complex value as JSON
                            table.add_row(k, str(self._format_json(v)))
                        elif isinstance(v, str) and v.startswith(
                            ("http://", "https://")
                        ):
                            # Highlight URLs
                            table.add_row(k, f"[link]{v}[/link]")
                        else:
                            table.add_row(k, str(v))

                    # Print the table with a subtle panel
                    self.console.print(Panel(table, expand=False, border_style="dim"))
                    return

            # Print the log line
            self.console.print(log_line)

        else:
            # Standard logging
            prefix = f"[{category}] " if category else ""
            log_message = f"{prefix}{formatted_message}"

            # Add auxiliary data in a clean format if present
            if auxiliary:
                # Format auxiliary data
                aux_parts = []
                for key, value in auxiliary.items():
                    # Unpack nested values similar to TS implementation
                    if isinstance(value, dict) and "value" in value:
                        extracted_value = value["value"]
                        # Handle different value types appropriately
                        if (
                            isinstance(extracted_value, str)
                            and len(extracted_value) > 80
                        ):
                            # Keep URLs and IDs intact
                            if any(
                                term in key.lower() for term in ["url", "id", "link"]
                            ):
                                aux_parts.append(f"{key}={extracted_value}")
                            else:
                                aux_parts.append(f"{key}={extracted_value[:77]}...")
                        else:
                            aux_parts.append(f"{key}={str(extracted_value)}")
                    else:
                        # For direct values
                        if isinstance(value, str) and len(value) > 80:
                            aux_parts.append(f"{key}={value[:77]}...")
                        else:
                            aux_parts.append(f"{key}={str(value)}")

                # Add formatted auxiliary data
                if aux_parts:
                    log_message += f" ({', '.join(aux_parts)})"

            # Log with appropriate level
            if level == 0:
                logger.error(log_message)
            elif level == 1:
                logger.info(log_message)
            elif level == 2:
                logger.debug(log_message)

    # Convenience methods
    def error(
        self, message: str, category: str = None, auxiliary: dict[str, Any] = None
    ):
        """Log an error message (level 0)"""
        self.log(message, level=0, category=category, auxiliary=auxiliary)

    def info(
        self, message: str, category: str = None, auxiliary: dict[str, Any] = None
    ):
        """Log an info message (level 1)"""
        self.log(message, level=1, category=category, auxiliary=auxiliary)

    def debug(
        self, message: str, category: str = None, auxiliary: dict[str, Any] = None
    ):
        """Log a debug message (level 2)"""
        self.log(message, level=2, category=category, auxiliary=auxiliary)


def sync_log_handler(log_data: dict[str, Any]) -> None:
    """
    Enhanced log handler for messages from the Stagehand server.
    Uses Rich for pretty printing and JSON formatting.

    The log_data structure from the server is:
    {
        "message": {  // This is the actual LogLine object
            "message": "...",
            "level": 0|1|2,
            "category": "...",
            "auxiliary": {...}
        },
        "status": "running"
    }
    """
    try:
        # Extract the actual LogLine object from the nested structure
        log_line = log_data.get("message", {})

        # Handle case where log_data might directly be the LogLine (fallback)
        if not isinstance(log_line, dict) or not log_line:
            # If message field is not a dict or is empty, treat log_data as the LogLine
            log_line = log_data

        # Extract data from the LogLine object
        level = log_line.get("level", 1)
        message = log_line.get("message", "")
        category = log_line.get("category", "")
        auxiliary = log_line.get("auxiliary", {})

        # Handle level conversion if it's a string
        if isinstance(level, str):
            level = {"error": 0, "info": 1, "warning": 1, "warn": 1, "debug": 2}.get(
                level.lower(), 1
            )

        # Ensure level is within valid range
        level = max(0, min(2, int(level))) if level is not None else 1

        # Handle cases where message might be a complex object
        if isinstance(message, dict):
            # If message is a dict, convert to string for display
            if "message" in message:
                # Handle nested message structure
                actual_message = message.get("message", "")
                if not level and "level" in message:
                    level = message.get("level", 1)
                if not category and "category" in message:
                    category = message.get("category", "")
                message = actual_message
            else:
                # Convert dict to JSON string
                message = json.dumps(message, indent=2)

        # Create a temporary logger to handle the message
        temp_logger = StagehandLogger(verbose=2, use_rich=True, external_logger=None)

        # Use the logger to format and display the message
        temp_logger.log(message, level=level, auxiliary=auxiliary)

    except Exception as e:
        # Fall back to basic logging if formatting fails
        print(f"Error formatting log: {str(e)}")
        print(f"Original log_data: {log_data}")


async def default_log_handler(log_data: dict[str, Any]) -> None:
    """
    Default handler for log messages from the Stagehand server.
    This is just a wrapper around sync_log_handler for backward compatibility.
    """
    sync_log_handler(log_data)
