import { NextResponse } from "next/server";
import { z } from "zod";
import { ActionLogger } from "@/lib/actionLogger";
import { initStagehand } from "../utils/initStagehand";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const url = searchParams.get("url");
  const instruction = searchParams.get("instruction");

  if (!url || !instruction) {
    return new NextResponse(
      JSON.stringify({ error: "Missing required parameters: url and instruction" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder);

      try {
        await stagehand.page.goto(url);

        const schema = z.any(); // Replace with actual schema for validation
        const data = await stagehand.extract({ instruction, schema });

        logger.log({
          category: "extract",
          message: JSON.stringify(data),
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