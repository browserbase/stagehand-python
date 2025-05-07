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

from stagehand.types.a11y import AccessibilityNode

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

# Create console instance with theme
console = Console(theme=stagehand_theme)

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
        # Use Rich handler for root logger
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt=datefmt,
            handlers=[
                RichHandler(
                    rich_tracebacks=True,
                    markup=True,
                    console=console,
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
        logging.getLogger("stagehand.utils").setLevel(utils_level)

    # Set higher log levels for noisy dependencies
    if quiet_dependencies:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)


################################################################################
#
# StagehandLogger: move into it's own file
#
################################################################################
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
    ):
        """
        Initialize the logger with specified verbosity and optional external logger.

        Args:
            verbose: Verbosity level (0=error only, 1=info, 2=detailed, 3=debug)
            external_logger: Optional callback function for log events
            use_rich: Whether to use Rich for pretty output (default: True)
        """
        self.verbose = verbose
        self.external_logger = external_logger
        self.use_rich = use_rich
        self.console = console

        # Map our verbosity levels to Python's logging levels
        self.level_map = {
            0: logging.ERROR,  # Critical errors only
            1: logging.INFO,  # Standard information
            2: logging.WARNING,  # More detailed info (using WARNING level)
            3: logging.DEBUG,  # Debug information
        }

        # Map level to style names
        self.level_style = {0: "error", 1: "info", 2: "warning", 3: "debug"}

        # Update logger level based on verbosity
        self._set_verbosity(verbose)

    def _set_verbosity(self, level: int):
        """Set the logger verbosity level"""
        self.verbose = level
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
            level: Verbosity level (0=error, 1=info, 2=detailed, 3=debug)
            category: Optional category for the message
            auxiliary: Optional dictionary of auxiliary data
        """
        # Skip logging if below current verbosity level
        if level > self.verbose and level != 0:  # Always log errors (level 0)
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
                logger.warning(log_message)
            elif level == 3:
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

    def warning(
        self, message: str, category: str = None, auxiliary: dict[str, Any] = None
    ):
        """Log a warning/detailed message (level 2)"""
        self.log(message, level=2, category=category, auxiliary=auxiliary)

    def debug(
        self, message: str, category: str = None, auxiliary: dict[str, Any] = None
    ):
        """Log a debug message (level 3)"""
        self.log(message, level=3, category=category, auxiliary=auxiliary)


# Create a synchronous wrapper for the async default_log_handler
def sync_log_handler(log_data: dict[str, Any]) -> None:
    """
    Synchronous wrapper for log handling, doesn't require awaiting.
    This avoids the coroutine never awaited warnings.
    """
    # Extract relevant data from the log message
    level = log_data.get("level", 1)
    if isinstance(level, str):
        level = {"error": 0, "info": 1, "warning": 2, "debug": 3}.get(level.lower(), 1)

    message = log_data.get("message", "")
    category = log_data.get("category", "")
    auxiliary = {}

    # Process auxiliary data if present
    if "auxiliary" in log_data:
        auxiliary = log_data.get("auxiliary", {})

        # Convert string representation to actual object if needed
        if isinstance(auxiliary, str) and (
            auxiliary.startswith("{") or auxiliary.startswith("{'")
        ):
            try:
                import ast

                auxiliary = ast.literal_eval(auxiliary)
            except (SyntaxError, ValueError):
                # If parsing fails, keep as string
                pass

    # Create a temporary logger to handle
    temp_logger = StagehandLogger(verbose=3, use_rich=True, external_logger=None)

    try:
        # Use the logger to format and display the message
        temp_logger.log(message, level=level, category=category, auxiliary=auxiliary)
    except Exception as e:
        # Fall back to basic logging if formatting fails
        print(f"Error formatting log: {str(e)}")
        print(f"Original message: {message}")
        if category:
            print(f"Category: {category}")
        if auxiliary:
            print(f"Auxiliary data: {auxiliary}")


async def default_log_handler(log_data: dict[str, Any]) -> None:
    """
    Enhanced default handler for log messages from the Stagehand server.
    Uses Rich for pretty printing and JSON formatting.

    This is an async function but calls the synchronous implementation.
    """
    sync_log_handler(log_data)


def snake_to_camel(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        snake_str: The snake_case string to convert

    Returns:
        The converted camelCase string
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_dict_keys_to_camel_case(data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert all keys in a dictionary from snake_case to camelCase.
    Works recursively for nested dictionaries.

    Args:
        data: Dictionary with snake_case keys

    Returns:
        Dictionary with camelCase keys
    """
    result = {}

    for key, value in data.items():
        if isinstance(value, dict):
            value = convert_dict_keys_to_camel_case(value)
        elif isinstance(value, list):
            value = [
                (
                    convert_dict_keys_to_camel_case(item)
                    if isinstance(item, dict)
                    else item
                )
                for item in value
            ]

        # Convert snake_case key to camelCase
        camel_key = snake_to_camel(key)
        result[camel_key] = value

    return result


def format_simplified_tree(node: AccessibilityNode, level: int = 0) -> str:
    """Formats a node and its children into a simplified string representation."""
    indent = "  " * level
    name_part = f": {node.get('name')}" if node.get("name") else ""
    result = f"{indent}[{node.get('nodeId')}] {node.get('role')}{name_part}\n"

    children = node.get("children", [])
    if children:
        result += "".join(
            format_simplified_tree(child, level + 1) for child in children
        )
    return result


async def draw_observe_overlay(page, elements):
    """
    Draw an overlay on the page highlighting the observed elements.

    Args:
        page: Playwright page object
        elements: List of observation results with selectors
    """
    if not elements:
        return

    # Create a function to inject and execute in the page context
    script = """
    (elements) => {
        // First remove any existing overlays
        document.querySelectorAll('.stagehand-observe-overlay').forEach(el => el.remove());
        
        // Create container for overlays
        const container = document.createElement('div');
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100%';
        container.style.height = '100%';
        container.style.pointerEvents = 'none';
        container.style.zIndex = '10000';
        container.className = 'stagehand-observe-overlay';
        document.body.appendChild(container);
        
        // Process each element
        elements.forEach((element, index) => {
            try {
                // Parse the selector
                let selector = element.selector;
                if (selector.startsWith('xpath=')) {
                    selector = selector.substring(6);
                    
                    // Evaluate the XPath to get the element
                    const result = document.evaluate(
                        selector, document, null, 
                        XPathResult.FIRST_ORDERED_NODE_TYPE, null
                    );
                    
                    if (result.singleNodeValue) {
                        // Get the element's position
                        const el = result.singleNodeValue;
                        const rect = el.getBoundingClientRect();
                        
                        // Create the overlay
                        const overlay = document.createElement('div');
                        overlay.style.position = 'absolute';
                        overlay.style.left = rect.left + 'px';
                        overlay.style.top = rect.top + 'px';
                        overlay.style.width = rect.width + 'px';
                        overlay.style.height = rect.height + 'px';
                        overlay.style.border = '2px solid red';
                        overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                        overlay.style.boxSizing = 'border-box';
                        overlay.style.pointerEvents = 'none';
                        
                        // Add element ID
                        const label = document.createElement('div');
                        label.textContent = index + 1;
                        label.style.position = 'absolute';
                        label.style.left = '0';
                        label.style.top = '-20px';
                        label.style.backgroundColor = 'red';
                        label.style.color = 'white';
                        label.style.padding = '2px 5px';
                        label.style.borderRadius = '3px';
                        label.style.fontSize = '12px';
                        
                        overlay.appendChild(label);
                        container.appendChild(overlay);
                    }
                } else {
                    // Regular CSS selector
                    const el = document.querySelector(selector);
                    if (el) {
                        const rect = el.getBoundingClientRect();
                        
                        // Create the overlay (same as above)
                        const overlay = document.createElement('div');
                        overlay.style.position = 'absolute';
                        overlay.style.left = rect.left + 'px';
                        overlay.style.top = rect.top + 'px';
                        overlay.style.width = rect.width + 'px';
                        overlay.style.height = rect.height + 'px';
                        overlay.style.border = '2px solid red';
                        overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                        overlay.style.boxSizing = 'border-box';
                        overlay.style.pointerEvents = 'none';
                        
                        // Add element ID
                        const label = document.createElement('div');
                        label.textContent = index + 1;
                        label.style.position = 'absolute';
                        label.style.left = '0';
                        label.style.top = '-20px';
                        label.style.backgroundColor = 'red';
                        label.style.color = 'white';
                        label.style.padding = '2px 5px';
                        label.style.borderRadius = '3px';
                        label.style.fontSize = '12px';
                        
                        overlay.appendChild(label);
                        container.appendChild(overlay);
                    }
                }
            } catch (error) {
                console.error(`Error drawing overlay for element ${index}:`, error);
            }
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            document.querySelectorAll('.stagehand-observe-overlay').forEach(el => el.remove());
        }, 5000);
    }
    """

    # Execute the script in the page context
    await page.evaluate(script, elements)


# Add utility functions for extraction URL handling

def transform_url_strings_to_ids(schema):
    """
    Transforms a Pydantic schema by replacing URL fields with numeric fields.
    This is used to handle URL extraction from accessibility trees where URLs are represented by IDs.
    
    Args:
        schema: A Pydantic model class
        
    Returns:
        Tuple of (transformed_schema, url_paths) where url_paths is a list of paths to URL fields
    """
    url_paths = []
    #TODO: Implement this
    # This is a simplified version - the actual implementation would need to analyze
    # the schema and identify URL fields by inspecting field types
    
    # For now, we'll just return the original schema since URL field detection
    # is complex in Pydantic and would require reflection
    
    return schema, url_paths


def inject_urls(result, url_paths, id_to_url_mapping):
    """
    Injects URLs back into the result data structure based on paths and ID-to-URL mapping.
    
    Args:
        result: The result data structure
        url_paths: List of paths to URL fields in the structure
        id_to_url_mapping: Dictionary mapping numeric IDs to URLs
        
    Returns:
        None (modifies result in-place)
    """
    for path in url_paths:
        segments = path.get("segments", [])
        if not segments:
            continue
            
        # Navigate to the nested structure
        current = result
        for i, segment in enumerate(segments[:-1]):
            if isinstance(current, dict) and segment in current:
                current = current[segment]
            else:
                # Path doesn't exist in result, skip
                break
                
        # Get the last segment and check if it exists
        last_segment = segments[-1]
        if isinstance(current, dict) and last_segment in current:
            # Get the ID value
            id_value = current[last_segment]
            if id_value and isinstance(id_value, (int, str)) and str(id_value) in id_to_url_mapping:
                # Replace ID with URL
                current[last_segment] = id_to_url_mapping[str(id_value)]
