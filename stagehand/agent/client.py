from abc import ABC, abstractmethod
from typing import Any, Optional

# Forward declaration or direct import. Assuming direct import is fine.
# If circular dependency issues arise, a forward declaration string might be needed for CUAHandler type hint.
from ..handlers.cua_handler import CUAHandler
from ..types.agent import AgentAction, AgentConfig, AgentExecuteOptions, AgentResult


class AgentClient(ABC):
    def __init__(
        self,
        model: str,
        instructions: Optional[str],
        config: Optional[AgentConfig],
        logger: Any,
        handler: CUAHandler,
    ):
        self.model = model
        self.instructions = instructions  # System prompt/base instructions
        self.config = config if config else AgentConfig()  # Ensure config is never None
        self.logger = logger
        self.handler: CUAHandler = handler  # Client holds a reference to the handler

    @abstractmethod
    async def run_task(
        self, instruction: str, options: Optional[AgentExecuteOptions]
    ) -> AgentResult:
        """
        Manages the entire multi-step interaction with the CUA provider.
        This includes:
        - Getting initial page state (screenshot).
        - Sending initial messages to the provider.
        - Looping through provider responses and actions.
        - Calling CUAHandler to perform actions on the page.
        - Getting updated page state after actions.
        - Formatting and sending results/state back to the provider.
        - Returning the final AgentResult.
        """
        pass

    @abstractmethod
    def _format_initial_messages(
        self, instruction: str, screenshot_base64: Optional[str]
    ) -> list[Any]:
        """
        Prepares the initial list of messages to send to the CUA provider.
        Specific to each provider's API format.
        """
        pass

    @abstractmethod
    def _process_provider_response(
        self, response: Any
    ) -> tuple[Optional[AgentAction], Optional[str], bool, Optional[str]]:
        """
        Parses the raw response from the CUA provider.
        Returns:
            - AgentAction (if an action is to be performed)
            - Reasoning text (if provided by the model)
            - Boolean indicating if the task is complete
            - Message from the model (if any, e.g., final summary)
        """
        pass

    @abstractmethod
    def _format_action_feedback(
        self, action: AgentAction, action_result: dict, new_screenshot_base64: str
    ) -> list[Any]:
        """
        Formats the feedback to the provider after an action is performed.
        This typically includes the result of the action and the new page state (screenshot).
        """
        pass

    @abstractmethod
    def format_screenshot(self, screenshot_base64: str) -> Any:
        """Format a screenshot for the agent. Takes the base64 encoded screenshot and returns a client-specific message part."""
        pass

    @abstractmethod
    def key_to_playwright(self, key: str) -> str:
        """Convert a key to a playwright key if needed by the client before creating an AgentAction."""
        pass
