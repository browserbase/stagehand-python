# Sessions

Types:

```python
from stagehand.types import Action, ModelConfig
```

Methods:

- <code title="post /sessions/{id}/act">client.sessions.<a href="./src/stagehand/resources/sessions.py">act</a>(id, \*\*<a href="src/stagehand/types/session_act_params.py">params</a>) -> object</code>
- <code title="post /sessions/{id}/end">client.sessions.<a href="./src/stagehand/resources/sessions.py">end</a>(id) -> object</code>
- <code title="post /sessions/{id}/agentExecute">client.sessions.<a href="./src/stagehand/resources/sessions.py">execute_agent</a>(id, \*\*<a href="src/stagehand/types/session_execute_agent_params.py">params</a>) -> object</code>
- <code title="post /sessions/{id}/extract">client.sessions.<a href="./src/stagehand/resources/sessions.py">extract</a>(id, \*\*<a href="src/stagehand/types/session_extract_params.py">params</a>) -> object</code>
- <code title="post /sessions/{id}/navigate">client.sessions.<a href="./src/stagehand/resources/sessions.py">navigate</a>(id, \*\*<a href="src/stagehand/types/session_navigate_params.py">params</a>) -> object</code>
- <code title="post /sessions/{id}/observe">client.sessions.<a href="./src/stagehand/resources/sessions.py">observe</a>(id, \*\*<a href="src/stagehand/types/session_observe_params.py">params</a>) -> object</code>
- <code title="post /sessions/start">client.sessions.<a href="./src/stagehand/resources/sessions.py">start</a>(\*\*<a href="src/stagehand/types/session_start_params.py">params</a>) -> object</code>
