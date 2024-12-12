import { LogLine } from "@browserbasehq/stagehand";
import { Stagehand } from "@browserbasehq/stagehand";

function logLineToString(logLine: LogLine): string {
  const timestamp = logLine.timestamp || new Date().toISOString();
  if (logLine.auxiliary?.error) {
    return `${timestamp}::[stagehand:${logLine.category}] ${logLine.message}\n ${logLine.auxiliary.error.value}\n ${logLine.auxiliary.trace.value}`;
  }
  return `${timestamp}::[stagehand:${logLine.category}] ${logLine.message} ${
    logLine.auxiliary ? JSON.stringify(logLine.auxiliary) : ""
  }`;
}

type LogLineAction = LogLine & {
  parsedAuxiliary?: string | object;
};

function parseLogLine(logLine: LogLine): LogLineAction {
  return {
    ...logLine,
    auxiliary: undefined,
    parsedAuxiliary: logLine.auxiliary
      ? Object.fromEntries(
          Object.entries(logLine.auxiliary).map(([key, entry]) => [
            key,
            entry.type === "object" ? JSON.parse(entry.value) : entry.value,
          ])
        )
      : undefined,
  } as LogLineAction;
}

export class ActionLogger {
  initialized = false;
  logs: LogLineAction[] = [];
  stagehand?: Stagehand;
  controller?: ReadableStreamController<Uint8Array>;
  encoder?: TextEncoder;

  constructor() {}

  init(
    stagehand: Stagehand,
    controller: ReadableStreamController<Uint8Array>,
    encoder: TextEncoder
  ) {
    this.stagehand = stagehand;
    this.controller = controller;
    this.encoder = encoder;
    this.initialized = true;
    console.log("ActionLogger initialized");
  }

  log(logLine: LogLine) {
    if (!this.controller || !this.encoder) {
      throw new Error("ActionLogger not initialized");
    }
    console.log(logLineToString(logLine));
    this.controller.enqueue(
      this.encoder.encode(logLineToString(logLine) + "\n")
    );
    this.logs.push(parseLogLine(logLine));
  }

  error(logLine: LogLine) {
    console.error(logLineToString(logLine));
    this.logs.push(parseLogLine(logLine));
  }

  warn(logLine: LogLine) {
    console.warn(logLineToString(logLine));
    this.logs.push(parseLogLine(logLine));
  }

  getLogs() {
    return this.logs;
  }
}
