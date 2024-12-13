// app/api/act/route.ts
import { NextResponse } from "next/server";
import { ActionLogger } from "@/lib/actionLogger";
import { initStagehand } from "../utils/initStagehand";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get("action");

  if (!action) {
    return new NextResponse(
      JSON.stringify({ error: "Missing required parameter: action" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder);

      try {
        await stagehand.act({ action });
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