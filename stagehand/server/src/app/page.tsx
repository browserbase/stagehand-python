"use client";

import { useSessionStore } from "@/lib/store/session";
import {
  endSession,
  getSessionDebugUrl,
  startSession,
} from "./actions/session";
import { useEffect, useState } from "react";
import { executeCommand } from "@/lib/execute";

export default function Home() {
  const {
    session,
    setSession,
    browserbaseApiKey,
    setBrowserbaseApiKey,
    browserbaseProjectId,
    setBrowserbaseProjectId,
    openaiApiKey,
    setOpenaiApiKey,
  } = useSessionStore();
  const [debugUrl, setDebugUrl] = useState<string | null>(null);
  const [selectedCommand, setSelectedCommand] = useState<string>("goto");
  const [commandInput, setCommandInput] = useState<string>("");

  const onStartSession = async () => {
    if (!browserbaseApiKey || !browserbaseProjectId || !openaiApiKey) {
      alert("Please fill in all fields");
      return;
    }

    const session = await startSession({
      browserbaseApiKey,
      browserbaseProjectId,
      modelApiKey: openaiApiKey,
    });
    setSession(session);
  };

  const onEndSession = async () => {
    if (!session || !browserbaseProjectId || !browserbaseApiKey) return;
    await endSession(session.id, browserbaseProjectId, browserbaseApiKey);
    setSession(null);
    setDebugUrl(null);
  };

  const copySessionIdToClipboard = () => {
    if (session) {
      void navigator.clipboard.writeText(session.id);
    }
  };

  useEffect(() => {
    if (!session || !browserbaseApiKey) {
      setDebugUrl(null);
      return;
    }
    getSessionDebugUrl(session.id, browserbaseApiKey)
      .then(setDebugUrl)
      .catch(() => setSession(null));
  }, [session, browserbaseApiKey, setSession]);

  return (
    <div className="font-[family-name:var(--font-geist-sans)] p-16 flex flex-row justify-between gap-12 h-screen w-screen">
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold">Stagehand API Demo</h1>
        <p className="text-sm text-gray-500">
          Click the button below to start a new session.
        </p>
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-md disabled:opacity-50"
          onClick={session ? onEndSession : onStartSession}
        >
          {session ? "End Session" : "Start Session"}
        </button>
        {session && (
          <p
            className="text-xs text-gray-500 cursor-pointer"
            onClick={copySessionIdToClipboard}
            title="Click to copy session ID"
          >
            Session ID: {session.id}
          </p>
        )}

        <input
          type="text"
          className="border rounded-md p-2 mt-2"
          placeholder="Browserbase API Key"
          value={browserbaseApiKey ?? ""}
          onChange={(e) => setBrowserbaseApiKey(e.target.value)}
        />
        <input
          type="text"
          className="border rounded-md p-2 mt-2"
          placeholder="Browserbase Project ID"
          value={browserbaseProjectId ?? ""}
          onChange={(e) => setBrowserbaseProjectId(e.target.value)}
        />
        <input
          type="text"
          className="border rounded-md p-2 mt-2"
          placeholder="OpenAI API Key"
          value={openaiApiKey ?? ""}
          onChange={(e) => setOpenaiApiKey(e.target.value)}
        />

        <div className="flex flex-row gap-2">
          <h2 className="text-sm font-bold">Execute a command</h2>
        </div>
        <select
          className="border rounded-md p-2"
          value={selectedCommand}
          onChange={(e) => setSelectedCommand(e.target.value)}
        >
          <option value="example">Example</option>
          <option value="act">Act</option>
          <option value="extract">Extract</option>
          <option value="observe">Observe</option>
          <option value="goto">Navigate</option>
          <option value="click">Click</option>
        </select>
        <input
          type="text"
          className="border rounded-md p-2 mt-2"
          placeholder="Enter command"
          value={commandInput}
          onChange={(e) => setCommandInput(e.target.value)}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-md mt-2 disabled:opacity-50"
          onClick={() => {
            if (
              session &&
              browserbaseApiKey &&
              browserbaseProjectId &&
              openaiApiKey
            ) {
              void executeCommand(
                session,
                selectedCommand,
                commandInput,
                browserbaseApiKey,
                browserbaseProjectId
              );
            }
          }}
          disabled={!session}
        >
          Execute Command
        </button>
      </div>
      <div className="flex flex-col gap-4 grow">
        <h1 className="text-2xl font-bold">Session Live View</h1>
        <div className="bg-gray-100 rounded-md flex-grow h-full">
          {debugUrl && <iframe className="w-full h-full" src={debugUrl} />}
          {!debugUrl && (
            <div className="flex flex-col items-center justify-center h-full">
              <p className="text-sm text-gray-500">
                Click the{" "}
                <span className="text-blue-500 font-medium">Start Session</span>{" "}
                button to create a session.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
