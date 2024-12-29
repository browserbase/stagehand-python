import { db } from "@/lib/db";
import { actions, sessions } from "@/lib/db/schema";
import { example } from "@/lib/example";
import { PageOverrider } from "@/lib/PageOverrider";
import { executeRequestSchema } from "@/types/execute";
import { type StagehandPage } from "@/types/stagehand";
import {
  type ActOptions,
  type ExtractOptions,
  type ObserveOptions,
  Stagehand,
} from "@browserbasehq/stagehand";
import { randomUUID } from "crypto";
import { eq } from "drizzle-orm/pg-core/expressions";
import { headers } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";
import { type z } from "zod";
import { jsonSchemaToZod } from "@/lib/utils/convertSchema";

export async function POST(request: NextRequest) {
  const { method, args } = executeRequestSchema.parse(await request.json());

  const headersList = await headers();

  const browserbaseSessionId = headersList.get("browserbase-session-id");
  const browserbaseApiKey = headersList.get("browserbase-api-key");
  const browserbaseProjectId = headersList.get("browserbase-project-id");

  if (!browserbaseSessionId) {
    return NextResponse.json(
      {
        error:
          "Browserbase session ID is required as a `browserbase-session-id` header",
      },
      { status: 400 }
    );
  } else if (!browserbaseApiKey) {
    return NextResponse.json(
      {
        error:
          "Browserbase API key is required as a `browserbase-api-key` header",
      },
      { status: 400 }
    );
  } else if (!browserbaseProjectId) {
    return NextResponse.json(
      {
        error:
          "Browserbase project ID is required as a `browserbase-project-id` header",
      },
      { status: 400 }
    );
  }

  const session = await db.query.sessions.findFirst({
    where: eq(sessions.id, browserbaseSessionId),
  });

  if (!session) {
    return NextResponse.json({ error: "Session not found" }, { status: 404 });
  }

  const action = await db
    .insert(actions)
    .values({
      method,
    })
    .returning()
    .then(([action]) => action);

  if (!action) {
    return NextResponse.json(
      { error: "Action created but not found" },
      { status: 404 }
    );
  }

  const stream = new ReadableStream({
    async start(controller) {
      function enqueueData(data: object) {
        controller.enqueue(
          `data: ${JSON.stringify({
            id: randomUUID(),
            ...data,
          })}\n\n`
        );
      }

      enqueueData({
        type: "system",
        data: {
          status: "starting",
          actionId: action.id,
        },
      });

      const stagehand = new Stagehand({
        env: "BROWSERBASE",
        browserbaseSessionID: session.id,
        apiKey: session.browserbaseApiKey,
        modelName: session.modelName,
        modelClientOptions: {
          apiKey: session.modelApiKey,
        },
        verbose: session.verbose ?? 0,
        debugDom: session.debugDom ?? false,
        domSettleTimeoutMs: session.domSettleTimeoutMs ?? 10000,
        logger(message) {
          enqueueData({
            type: "log",
            data: {
              status: "running",
              actionId: action.id,
              message,
            },
          });
        },
      });

      await stagehand.init();

      enqueueData({
        type: "system",
        data: {
          status: "connected",
          actionId: action.id,
        },
      });

      const { page } = new PageOverrider(stagehand);

      let result: unknown;

      try {
        if (method === "example") {
          result = await example(page);
        } else if (method === "act") {
          result = await page.act(args[0] as ActOptions);
        } else if (method === "extract") {
          const {
            instruction,
            schemaDefinition,
            ...rest
          } = (args[0] ?? {}) as Record<string, unknown>;

          if (schemaDefinition && typeof schemaDefinition === "object") {
            const zodSchema = jsonSchemaToZod(schemaDefinition);
            result = await page.extract({
              instruction: instruction as string,
              schema: zodSchema,
              ...rest,
            } as ExtractOptions<z.AnyZodObject>);
          } else {
            result = await page.extract(args[0] as ExtractOptions<z.AnyZodObject>);
          }
        } else if (method === "observe") {
          result = await page.observe(args[0] as ObserveOptions);
        } else {
          // @ts-expect-error - fix typing
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          result = await page[method as keyof StagehandPage](...args);
        }
      } catch (error) {
        if (error instanceof Error) {
          console.error(error);
          enqueueData({
            type: "system",
            data: {
              status: "error",
              actionId: action.id,
              error: error.message,
            },
          });
        } else {
          console.error("Unknown error", error);
          enqueueData({
            type: "system",
            data: {
              status: "error",
              actionId: action.id,
              error: "Unknown error occurred",
            },
          });
        }
      }

      enqueueData({
        type: "system",
        data: {
          status: "finished",
          actionId: action.id,
          result,
        },
      });

      controller.close();
    },
  });

  return new NextResponse(stream, {
    headers: {
      "content-type": "text/event-stream",
      connection: "keep-alive",
    },
  });
}
