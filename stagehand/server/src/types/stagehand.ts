import type {
  ActOptions,
  ExtractOptions,
  ExtractResult,
  ObserveOptions,
  ObserveResult,
} from "@browserbasehq/stagehand";
import type { Page as PlaywrightPage } from "playwright-core";
import type { z } from "zod";

interface ActResult {
  method: string;
  element: number;
  args: unknown[];
  completed: boolean;
  step: string;
  why?: string;
}

export interface StagehandPage extends PlaywrightPage {
  act: (options: ActOptions) => Promise<ActResult>;
  extract: <T extends z.AnyZodObject>(
    options: ExtractOptions<T>
  ) => Promise<ExtractResult<T>>;
  observe: (options?: ObserveOptions) => Promise<ObserveResult[]>;
}
