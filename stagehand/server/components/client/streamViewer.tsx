// app/components/StreamViewer.tsx
"use client";

import { useState } from "react";

export default function StreamViewer() {
  const [messages, setMessages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

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
      const response = await fetch("/api/act");
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

  return (
    <div className="p-4 max-w-md mx-auto">
      <button
        onClick={startStreaming}
        disabled={isLoading}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
      >
        {isLoading ? "Streaming..." : "Start Stream"}
      </button>

      <button
        onClick={startAct}
        disabled={isLoading}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
      >
        {isLoading ? "Streaming..." : "Start Act"}
      </button>
      <div className="mt-4 border rounded p-4 min-h-[200px]">
        {messages.map((message, index) => (
          <div key={index} className="py-1">
            {message}
          </div>
        ))}
      </div>
    </div>
  );
}
