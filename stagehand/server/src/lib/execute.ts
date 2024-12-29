import { type SessionCreateResponse } from "@browserbasehq/sdk/src/resources/index.js";

export const executeCommand = async (
  session: SessionCreateResponse,
  method: string,
  input: string,
  browserbaseApiKey: string,
  browserbaseProjectId: string
) => {
  const args = [];

  if (method === "act") {
    args.push({
      action: input,
    });
  } else {
    args.push(input);
  }

  const response = await fetch("/api/execute", {
    method: "POST",
    body: JSON.stringify({ method, args }),
    headers: {
      "browserbase-session-id": session.id,
      "browserbase-api-key": browserbaseApiKey,
      "browserbase-project-id": browserbaseProjectId,
    },
  });

  return response;
};
