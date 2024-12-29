import type { StagehandPage } from "@/types/stagehand";
import type { GotoOptions, Stagehand } from "@browserbasehq/stagehand";
import type { CDPSession } from "playwright-core";
import { LocatorOverrider } from "./LocatorOverrider";

export class PageOverrider {
  private stagehand: Stagehand;
  private cdpClient!: CDPSession;
  private locatorOverrider: LocatorOverrider;

  constructor(stagehand: Stagehand) {
    this.stagehand = stagehand;
    this.locatorOverrider = new LocatorOverrider(stagehand);
  }

  async getCDPClient() {
    if (!this.cdpClient) {
      this.cdpClient = await this.stagehand.context.newCDPSession(
        this.stagehand.page
      );
    }

    return this.cdpClient;
  }

  get page(): StagehandPage {
    return new Proxy(this.stagehand.page, {
      get: (target: StagehandPage, prop: keyof StagehandPage) => {
        if (prop === "goto") {
          return async (url: string, options?: GotoOptions) => {
            return this.goto(url, options);
          };
        } else if (prop === "click") {
          return async (selector: string) => {
            return this.click(selector);
          };
        } else if (prop === "locator") {
          return this.locatorOverrider.locator;
        }

        return Reflect.get(target, prop) as StagehandPage[keyof StagehandPage];
      },
    });
  }

  private async goto(
    url: string,
    options?: {
      referer?: string;
      timeout?: number;
      waitUntil?: "load" | "domcontentloaded" | "networkidle" | "commit";
    }
  ) {
    const cdpClient = await this.getCDPClient();

    await cdpClient.send("Page.navigate", {
      url,
      referrer: options?.referer,
    });
  }

  private async click(selector: string) {
    const cdpClient = await this.getCDPClient();
    const { x, y } = await this.stagehand.page.evaluate((selector) => {
      const element = document.querySelector(selector);
      if (!element) {
        throw new Error(`Element not found for selector: ${selector}`);
      }
      const rect = element.getBoundingClientRect();
      return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    }, selector);

    await cdpClient.send("Input.dispatchMouseEvent", {
      type: "mousePressed",
      x,
      y,
      button: "left",
      clickCount: 1,
    });

    await cdpClient.send("Input.dispatchMouseEvent", {
      type: "mouseReleased",
      x,
      y,
      button: "left",
      clickCount: 1,
    });
  }
}
