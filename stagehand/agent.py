from .schemas import (
    AgentConfig,
    AgentExecuteOptions,
    AgentExecuteResult,
    AgentProvider,
)

# Model to provider mapping
MODEL_TO_PROVIDER_MAP: dict[str, AgentProvider] = {
    "computer-use-preview": AgentProvider.OPENAI,
    "claude-3-5-sonnet-20240620": AgentProvider.ANTHROPIC,
    "claude-3-7-sonnet-20250219": AgentProvider.ANTHROPIC,
    # Add more mappings as needed
}


class Agent:
    """
    Class to handle agent functionality in Stagehand
    """

    def __init__(self, stagehand_client, agent_config: AgentConfig):
        """
        Initialize an Agent instance.

        Args:
            stagehand_client: The client used to interface with the Stagehand server.
            agent_config (AgentConfig): Configuration for the agent,
                                          including provider, model, options, instructions.
        """
        self._stagehand = stagehand_client
        self._config = agent_config  # Store the required config

        if not self._stagehand._initialized:
            self._stagehand.logger.error(
                "Stagehand must be initialized before creating an agent. Call await stagehand.init() first."
            )
            raise RuntimeError(
                "Stagehand must be initialized before creating an agent. Call await stagehand.init() first."
            )

        # Perform provider inference and validation
        if self._config.model and not self._config.provider:
            if self._config.model in MODEL_TO_PROVIDER_MAP:
                self._config.provider = MODEL_TO_PROVIDER_MAP[self._config.model]
            else:
                self._stagehand.logger.error(
                    f"Could not infer provider for model: {self._config.model}"
                )

        # Ensure provider is correctly set as an enum if provided as a string
        if self._config.provider and isinstance(self._config.provider, str):
            try:
                self._config.provider = AgentProvider(self._config.provider.lower())
            except ValueError as e:
                raise ValueError(
                    f"Invalid provider: {self._config.provider}. Must be one of: {', '.join([p.value for p in AgentProvider])}"
                ) from e
        elif not self._config.provider:
            raise ValueError(
                "Agent provider is required and could not be determined from the provided config."
            )

    async def execute(self, execute_options: AgentExecuteOptions) -> AgentExecuteResult:
        """
        Execute a task using the configured autonomous agent via the Stagehand server.

        Args:
            execute_options (AgentExecuteOptions): Options for execution, including the instruction.

        Returns:
            AgentExecuteResult: The result of the agent execution.
        """

        payload = {
            # Use the stored config
            "agentConfig": self._config.model_dump(exclude_none=True, by_alias=True),
            "executeOptions": execute_options.model_dump(
                exclude_none=True, by_alias=True
            ),
        }

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("agentExecute", payload)

        if isinstance(result, dict):
            # Ensure all expected fields are present
            # If not present in result, use defaults from AgentExecuteResult schema
            if "success" not in result:
                raise ValueError("Response missing required field 'success'")

            # Ensure completed is set with default if not present
            if "completed" not in result:
                result["completed"] = False

            # Add default for message if missing
            if "message" not in result:
                result["message"] = None

            return AgentExecuteResult(**result)
        elif result is None:
            # Handle cases where the server might return None or an empty response
            # Return a default failure result or raise an error
            return AgentExecuteResult(
                success=False, completed=False, message="No result received from server"
            )
        else:
            # If the result is not a dict and not None, it's unexpected
            raise TypeError(f"Unexpected result type from server: {type(result)}")
