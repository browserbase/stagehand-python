// app/api/stream/route.ts
import { AvailableModel, LogLine, Stagehand } from "@browserbasehq/stagehand";
import { NextResponse } from "next/server";
import { ActionLogger } from "@/lib/actionLogger";
import { z } from "zod";
const env: "BROWSERBASE" | "LOCAL" = "BROWSERBASE";
const modelName: AvailableModel = "gpt-4o";
const domSettleTimeoutMs = 10000;
const enableCaching = process.env.EVAL_ENABLE_CACHING?.toLowerCase() === "true";

const defaultStagehandOptions = {
  env,
  headless: false,
  verbose: 2 as const,
  debugDom: true,
  enableCaching,
};

const initStagehand = async (
  logger: ActionLogger,
  controller: ReadableStreamController<Uint8Array>,
  encoder: TextEncoder
): Promise<Stagehand> => {
  const stagehand = new Stagehand({
    ...defaultStagehandOptions,
    logger: (logLine: LogLine) => {
      logger.log(logLine);
    },
  });
  logger.init(stagehand, controller, encoder);
  await stagehand.init({ modelName, domSettleTimeoutMs });
  return stagehand;
};

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const url = searchParams.get('url');
  const action = searchParams.get('action');

  if (!url || !action) {
    return new NextResponse(
      JSON.stringify({ error: 'Missing required parameters: url and action' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }

  // Create a readable stream
  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder);

      try {
        await stagehand.page.goto(url);
        await stagehand.act({ action });
      } catch (error) {
        logger.log({ type: 'error', message: error.message });
      } finally {
        controller.close();
      }
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
