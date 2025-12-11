# Sessions

Types:

```python
from stagehand.types import (
    Action,
    ModelConfig,
    SessionActResponse,
    SessionEndResponse,
    SessionExecuteAgentResponse,
    SessionExtractResponse,
    SessionNavigateResponse,
    SessionObserveResponse,
    SessionStartResponse,
)
```

Methods:

- <code title="post /sessions/{sessionId}/act">client.sessions.<a href="./src/stagehand/resources/sessions.py">act</a>(session_id, \*\*<a href="src/stagehand/types/session_act_params.py">params</a>) -> <a href="./src/stagehand/types/session_act_response.py">SessionActResponse</a></code>
- <code title="post /sessions/{sessionId}/end">client.sessions.<a href="./src/stagehand/resources/sessions.py">end</a>(session_id) -> <a href="./src/stagehand/types/session_end_response.py">SessionEndResponse</a></code>
- <code title="post /sessions/{sessionId}/agentExecute">client.sessions.<a href="./src/stagehand/resources/sessions.py">execute_agent</a>(session_id, \*\*<a href="src/stagehand/types/session_execute_agent_params.py">params</a>) -> <a href="./src/stagehand/types/session_execute_agent_response.py">SessionExecuteAgentResponse</a></code>
- <code title="post /sessions/{sessionId}/extract">client.sessions.<a href="./src/stagehand/resources/sessions.py">extract</a>(session_id, \*\*<a href="src/stagehand/types/session_extract_params.py">params</a>) -> <a href="./src/stagehand/types/session_extract_response.py">SessionExtractResponse</a></code>
- <code title="post /sessions/{sessionId}/navigate">client.sessions.<a href="./src/stagehand/resources/sessions.py">navigate</a>(session_id, \*\*<a href="src/stagehand/types/session_navigate_params.py">params</a>) -> <a href="./src/stagehand/types/session_navigate_response.py">Optional[SessionNavigateResponse]</a></code>
- <code title="post /sessions/{sessionId}/observe">client.sessions.<a href="./src/stagehand/resources/sessions.py">observe</a>(session_id, \*\*<a href="src/stagehand/types/session_observe_params.py">params</a>) -> <a href="./src/stagehand/types/session_observe_response.py">SessionObserveResponse</a></code>
- <code title="post /sessions/start">client.sessions.<a href="./src/stagehand/resources/sessions.py">start</a>(\*\*<a href="src/stagehand/types/session_start_params.py">params</a>) -> <a href="./src/stagehand/types/session_start_response.py">SessionStartResponse</a></code>
