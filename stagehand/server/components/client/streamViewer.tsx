// app/components/StreamViewer.tsx
"use client";
// components/client/streamViewer.tsx
import { useState } from "react";

export default function StreamViewer() {
  const [messages, setMessages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [url, setUrl] = useState("");
  const [action, setAction] = useState("");

  const startStreaming = async () => {
    setIsLoading(true);
    setMessages([]);

    try {
      const response = await fetch("/api/streamtest");
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No reader available");
      }

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        setMessages((prev) => [
          ...prev,
          ...text.split("\n").filter((msg) => msg.trim()),
        ]);
      }
    } catch (error) {
      console.error("Streaming error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const startAct = async () => {
    setIsLoading(true);
    setMessages([]);

    try {
      const response = await fetch(
        `/api/act?url=${encodeURIComponent(url)}&action=${encodeURIComponent(action)}`
      );
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No reader available");
      }

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        setMessages((prev) => [
          ...prev,
          ...text.split("\n").filter((msg) => msg.trim()),
        ]);
      }
    } catch (error) {
      console.error("Streaming error:", error);
      setMessages((prev) => [...prev, `Error: ${error.message}`]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <div className="space-y-4 mb-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700">
            URL
          </label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label htmlFor="action" className="block text-sm font-medium text-gray-700">
            Action
          </label>
          <input
            type="text"
            id="action"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            placeholder="click the login button"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="space-x-4">
        <button
          onClick={startStreaming}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          {isLoading ? "Streaming..." : "Start Stream"}
        </button>

        <button
          onClick={startAct}
          disabled={isLoading || !url || !action}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          {isLoading ? "Acting..." : "Start Act"}
        </button>
      </div>

      <div className="mt-4 border rounded p-4 min-h-[200px] bg-gray-50">
        {messages.map((message, index) => (
          <div key={index} className="py-1 font-mono text-sm">
            {message}
          </div>
        ))}
      </div>
    </div>
  );
}