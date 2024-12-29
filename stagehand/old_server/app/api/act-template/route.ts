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

export async function GET() {
  // Create a readable stream
  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder);

      await stagehand.page.goto("https://github.com/browserbase/stagehand");
      await stagehand.act({ action: "click on the contributors" });
      const contributor = await stagehand.extract({
        instruction: "extract the top contributor",
        schema: z.object({
          username: z.string(),
          url: z.string(),
        }),
      });
      console.log("our favorite contributor is", contributor);

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