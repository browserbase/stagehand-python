import { type StagehandPage } from "@/types/stagehand";
import { type Stagehand } from "@browserbasehq/stagehand";

export class LocatorOverrider {
  private stagehand: Stagehand;

  constructor(stagehand: Stagehand) {
    this.stagehand = stagehand;
  }

  get locator() {
    return (
      selector: string,
      options?: Parameters<StagehandPage["locator"]>[1]
    ) => {
      const originalLocator = this.stagehand.page.locator(selector, options);

      return new Proxy(originalLocator, {
        get: (target, prop): unknown => {
          if (prop === "click") {
            return async () => {
              return this.click(target);
            };
          }

          return Reflect.get(target, prop);
        },
      });
    };
  }

  private async click(locator: ReturnType<StagehandPage["locator"]>) {
    return locator.click();
  }
}
