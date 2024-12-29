import { type StagehandPage } from "@/types/stagehand";

export const example = async (page: StagehandPage) => {
  // using CDP
  await page.goto("https://www.google.com");

  await page.locator("textarea[title='Search']").click();
  await page.locator("textarea[title='Search']").fill("Hello");

  // click with CDP
  await page.click('input[aria-label="Google Search"]');

  return "Hello";
};
