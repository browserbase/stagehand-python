# This module previously contained Browserbase API functions that have been removed
# as part of the migration to local-only browser automation.
# 
# The following functions were removed:
# - _create_session: Created Browserbase sessions
# - _execute: Executed API calls to Browserbase
# - _get_replay_metrics: Fetched replay metrics from Browserbase
#
# These functions are no longer needed since Stagehand now operates exclusively
# with local browser instances and does not require external API communication.

__all__ = []
