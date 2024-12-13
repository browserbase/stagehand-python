import { NextResponse } from "next/server";
import { ActionLogger } from "@/lib/actionLogger";
import { initStagehand } from "../utils/initStagehand";
import { ConstructorParams } from "@browserbasehq/stagehand";

export async function POST(request: Request) {
  const { url, constructorOptions } = await request.json();

  if (!url) {
    return new NextResponse(
      JSON.stringify({ error: "Missing required parameter: url" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder, constructorOptions as Partial<ConstructorParams>);

      try {
        await stagehand.page.goto(url);
        // TODO - do we need to wait for the dom to settle?
        
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