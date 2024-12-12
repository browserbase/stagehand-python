// app/api/stream/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const encoder = new TextEncoder();

  // Create a readable stream
  const stream = new ReadableStream({
    async start(controller) {
      // Simulate streaming data with some delay
      const messages = [
        "Hello",
        "This is",
        "a streaming",
        "response",
        "from Next.js!",
      ];

      for (const message of messages) {
        // Add the message to the stream
        controller.enqueue(encoder.encode(message + "\n"));
        // Wait for 1 second between messages
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      controller.close();
    },
  });

  // Return the stream with appropriate headers
  return new NextResponse(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
