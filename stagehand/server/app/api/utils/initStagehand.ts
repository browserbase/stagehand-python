
import { AvailableModel, ConstructorParams, LogLine, Stagehand } from "@browserbasehq/stagehand";
import { ActionLogger } from "@/lib/actionLogger";

const env: "BROWSERBASE" | "LOCAL" = "BROWSERBASE";
const modelName: AvailableModel = "gpt-4o";
const domSettleTimeoutMs = 10000;
const enableCaching = process.env.EVAL_ENABLE_CACHING?.toLowerCase() === "true";

const defaultStagehandOptions = {
  env,
  headless: false, // Set to true in production
  verbose: 2 as const,
  debugDom: true,
  enableCaching,
};

export const initStagehand = async (
  logger: ActionLogger,
  controller: ReadableStreamController<Uint8Array>,
  encoder: TextEncoder,
  options: Partial<ConstructorParams> = {}
): Promise<Stagehand> => {
  const stagehand = new Stagehand({
    ...defaultStagehandOptions,
    ...options,
    logger: (logLine: LogLine) => {
      logger.log(logLine);
    },
  });

  logger.init(stagehand, controller, encoder);

  await stagehand.init({ modelName, domSettleTimeoutMs });

  return stagehand;
};