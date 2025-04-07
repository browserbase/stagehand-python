from typing import Dict

from ..schemas import (
    AgentConfig,
    AgentExecuteOptions,
    AgentExecuteResult,
    AgentProvider,
)

# Model to provider mapping
MODEL_TO_PROVIDER_MAP: Dict[str, AgentProvider] = {
    "computer-use-preview": AgentProvider.OPENAI,
    "claude-3-5-sonnet-20240620": AgentProvider.ANTHROPIC,
    "claude-3-7-sonnet-20250219": AgentProvider.ANTHROPIC,
    # Add more mappings as needed
}


class SyncAgent:
    """
    Synchronous class to handle agent functionality in Stagehand
    """

    def __init__(self, stagehand_client):
        """
        Initialize a SyncAgent instance.

        Args:
            stagehand_client: The sync client used to interface with the Stagehand server.
        """
        self._stagehand = stagehand_client

    def execute(
        self, agent_config: AgentConfig, execute_options: AgentExecuteOptions
    ) -> AgentExecuteResult:
        """
        Execute a task using an autonomous agent via the Stagehand server synchronously.

        Args:
            agent_config (AgentConfig): Configuration for the agent, including provider and model.
            execute_options (AgentExecuteOptions): Options for execution, including the instruction.

        Returns:
            AgentExecuteResult: The result of the agent execution.
        """
        # If provider is not set but model is, infer provider from model
        if (
            not agent_config.provider
            and agent_config.model
            and agent_config.model in MODEL_TO_PROVIDER_MAP
        ):
            agent_config.provider = MODEL_TO_PROVIDER_MAP[agent_config.model]

        # Ensure provider is correctly set as an enum if provided as a string
        if agent_config.provider and isinstance(agent_config.provider, str):
            try:
                agent_config.provider = AgentProvider(agent_config.provider.lower())
            except ValueError:
                raise ValueError(
                    f"Invalid provider: {agent_config.provider}. Must be one of: {', '.join([p.value for p in AgentProvider])}"
                )

        payload = {
            "agentConfig": agent_config.model_dump(exclude_none=True, by_alias=True),
            "executeOptions": execute_options.model_dump(
                exclude_none=True, by_alias=True
            ),
        }

        # Log the request details
        self._stagehand._log("\n==== EXECUTING AGENT REQUEST ====", level=3)
        self._stagehand._log(f"Agent Provider: {agent_config.provider}", level=3)
        self._stagehand._log(f"Agent Model: {agent_config.model}", level=3)
        self._stagehand._log(
            f"Agent Instruction: {execute_options.instruction}", level=3
        )
        self._stagehand._log(f"Full Payload: {payload}", level=3)

        result = self._stagehand._execute("agentExecute", payload)

        if isinstance(result, dict):
            # Ensure all expected fields are present
            # If not present in result, use defaults from AgentExecuteResult schema
            if "success" not in result:
                raise ValueError("Response missing required field 'success'")

            # Ensure completed is set with default if not present
            if "completed" not in result:
                result["completed"] = False

            return AgentExecuteResult(**result)
        return result
