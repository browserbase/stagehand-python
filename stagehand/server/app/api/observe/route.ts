import { NextResponse } from "next/server";
import { ActionLogger } from "@/lib/actionLogger";
import { initStagehand } from "../utils/initStagehand";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const instruction = searchParams.get("instruction") || undefined;

  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder);

      try {
        const observations = await stagehand.observe({ instruction });

        logger.log({
          category: "observe",
          message: JSON.stringify(observations),
          level: 1,
        });
      } catch (error: any) {
        logger.log({ category: "error", message: error.message, level: 0 });
      } finally {
        controller.close();
        await stagehand.close();
      }
    },
  });

  return new NextResponse(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
} 