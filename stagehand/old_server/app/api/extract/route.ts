// app/api/extract/route.ts
import { NextResponse } from "next/server";
import { ActionLogger } from "@/lib/actionLogger";
import { initStagehand } from "../utils/initStagehand";
import { ConstructorParams } from "@browserbasehq/stagehand";
import { jsonSchemaToZod } from "../utils/convertSchema";
import { AnyZodObject } from "zod";
export async function POST(request: Request) {
  const { instruction, url, schemaDefinition, constructorOptions } = await request.json();

  if (!instruction || !schemaDefinition) {
    return NextResponse.json(
      { error: "Missing required parameters: instruction and schemaDefinition" },
      { status: 400 }
    );
  }

  const zodSchema = jsonSchemaToZod(schemaDefinition) as AnyZodObject;

  const stream = new ReadableStream({
    async start(controller) {
      const logger = new ActionLogger();
      const encoder = new TextEncoder();
      const stagehand = await initStagehand(logger, controller, encoder, constructorOptions as Partial<ConstructorParams>);

      try {
        if (url) {
          await stagehand.page.goto(url);
        }
        const data = await stagehand.extract({ instruction, schema: zodSchema });
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
      "Connection": "keep-alive",
    },
  });
}