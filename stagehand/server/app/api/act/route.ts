// app/api/act/route.ts
import { NextResponse } from "next/server";
import { ActionLogger } from "@/lib/actionLogger";
import { initStagehand } from "../utils/initStagehand";

export async function POST(request: Request) {
  const { action, url, variables } = await request.json();

  if (!action) {
    return NextResponse.json(
      { error: "Missing required parameter: action" },
      { status: 400 }
    );
  }

  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder);

      try {
        if (url) {
          await stagehand.page.goto(url);
        }
        await stagehand.act({ action, variables });
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