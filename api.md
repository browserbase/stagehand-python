# Sessions

Types:

```python
from stagehand.types import (
    Action,
    ModelConfig,
    StreamEvent,
    SessionActResponse,
    SessionEndResponse,
    SessionExecuteResponse,
    SessionExtractResponse,
    SessionNavigateResponse,
    SessionObserveResponse,
    SessionStartResponse,
)
```

Methods:

- <code title="post /v1/sessions/{id}/act">client.sessions.<a href="./src/stagehand/resources/sessions.py">act</a>(id, \*\*<a href="src/stagehand/types/session_act_params.py">params</a>) -> <a href="./src/stagehand/types/session_act_response.py">SessionActResponse</a></code>
- <code title="post /v1/sessions/{id}/end">client.sessions.<a href="./src/stagehand/resources/sessions.py">end</a>(id, \*\*<a href="src/stagehand/types/session_end_params.py">params</a>) -> <a href="./src/stagehand/types/session_end_response.py">SessionEndResponse</a></code>
- <code title="post /v1/sessions/{id}/agentExecute">client.sessions.<a href="./src/stagehand/resources/sessions.py">execute</a>(id, \*\*<a href="src/stagehand/types/session_execute_params.py">params</a>) -> <a href="./src/stagehand/types/session_execute_response.py">SessionExecuteResponse</a></code>
- <code title="post /v1/sessions/{id}/extract">client.sessions.<a href="./src/stagehand/resources/sessions.py">extract</a>(id, \*\*<a href="src/stagehand/types/session_extract_params.py">params</a>) -> <a href="./src/stagehand/types/session_extract_response.py">SessionExtractResponse</a></code>
- <code title="post /v1/sessions/{id}/navigate">client.sessions.<a href="./src/stagehand/resources/sessions.py">navigate</a>(id, \*\*<a href="src/stagehand/types/session_navigate_params.py">params</a>) -> <a href="./src/stagehand/types/session_navigate_response.py">SessionNavigateResponse</a></code>
- <code title="post /v1/sessions/{id}/observe">client.sessions.<a href="./src/stagehand/resources/sessions.py">observe</a>(id, \*\*<a href="src/stagehand/types/session_observe_params.py">params</a>) -> <a href="./src/stagehand/types/session_observe_response.py">SessionObserveResponse</a></code>
- <code title="post /v1/sessions/start">client.sessions.<a href="./src/stagehand/resources/sessions.py">start</a>(\*\*<a href="src/stagehand/types/session_start_params.py">params</a>) -> <a href="./src/stagehand/types/session_start_response.py">SessionStartResponse</a></code>
