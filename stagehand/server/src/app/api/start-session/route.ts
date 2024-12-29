import { NextResponse } from "next/server";
import { startSession } from "@/app/actions/session";
import { headers } from "next/headers";

export async function POST(request: Request) {
  try {
    const headersList = await headers();
    const browserbaseApiKey = headersList.get("browserbase-api-key");
    const browserbaseProjectId = headersList.get("browserbase-project-id");
    const modelApiKey = headersList.get("model-api-key");

    if (!browserbaseApiKey || !browserbaseProjectId || !modelApiKey) {
      return NextResponse.json(
        { error: "Missing required API keys in headers" },
        { status: 400 }
      );
    }

    const body = await request.json();
    const { modelName, domSettleTimeoutMs, verbose, debugDom } = body;

    const session = await startSession({
      browserbaseApiKey,
      browserbaseProjectId,
      modelApiKey,
      modelName,
      domSettleTimeoutMs,
      verbose,
      debugDom,
    });

    return NextResponse.json({ sessionId: session.id });
  } catch (error) {
    console.error("Error starting session:", error);
    return NextResponse.json(
      { error: "Failed to start session" },
      { status: 500 }
    );
  }
}