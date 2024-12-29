"use server";

import { db } from "@/lib/db";
import { sessions } from "@/lib/db/schema";
import Browserbase from "@browserbasehq/sdk";
import { eq } from "drizzle-orm";

type Session = Partial<typeof sessions.$inferSelect>;

export const startSession = async ({
  browserbaseApiKey,
  browserbaseProjectId,
  modelApiKey,
  modelName = "gpt-4o",
  domSettleTimeoutMs,
  verbose,
  debugDom,
}: Session) => {
  if (!browserbaseApiKey || !browserbaseProjectId || !modelApiKey) {
    throw new Error("Missing required fields");
  }

  const bb = new Browserbase({
    apiKey: browserbaseApiKey,
  });

  const session = await bb.sessions.create({
    projectId: browserbaseProjectId,
    keepAlive: true,
  });

  await db.insert(sessions).values({
    id: session.id,
    browserbaseApiKey,
    browserbaseProjectId,
    modelName,
    modelApiKey,
    domSettleTimeoutMs,
    verbose,
    debugDom,
  });

  return session;
};

export const endSession = async (
  sessionId: string,
  browserbaseProjectId: string,
  browserbaseApiKey: string
) => {
  const bb = new Browserbase({
    apiKey: browserbaseApiKey,
  });

  await bb.sessions.update(sessionId, {
    projectId: browserbaseProjectId,
    status: "REQUEST_RELEASE",
  });

  await db.delete(sessions).where(eq(sessions.id, sessionId));
};

export const getSessionDebugUrl = async (
  sessionId: string,
  browserbaseApiKey: string
) => {
  const bb = new Browserbase({
    apiKey: browserbaseApiKey,
  });

  const { debuggerUrl } = await bb.sessions.debug(sessionId);

  return debuggerUrl;
};
