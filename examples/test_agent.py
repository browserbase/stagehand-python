import asyncio
import logging
import os
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from pprint import pprint
import base64
from stagehand.agent import Agent
import time
from stagehand import StagehandConfig, Stagehand
# from stagehand.sync import Stagehand
# from stagehand.logging import configure_logging  # Import from logging module
from stagehand.utils import configure_logging

from stagehand.schemas import ObserveOptions, ActOptions, ExtractOptions, AgentExecuteOptions, AgentProvider
from stagehand.a11y.utils import get_accessibility_tree, get_xpath_by_resolved_object_id

# # Configure logging with cleaner format
configure_logging(
    level=logging.INFO,
    remove_logger_name=True,  # Remove the redundant stagehand.client prefix
    quiet_dependencies=True,   # Suppress httpx and other noisy logs
)

# Create a custom theme for consistent styling
custom_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "highlight": "magenta",
        "url": "blue underline",
    }
)

# Create a Rich console instance with our theme
console = Console(theme=custom_theme)

load_dotenv()


class Joke(BaseModel):
    joke: str
    explanation: str
    setup: str
    punchline: str

class Jokes(BaseModel):
    jokes: list[Joke]

class Action(BaseModel):
    action: str
    id: int
    arguments: list[str]

# def main():
#     # Build a unified configuration object for Stagehand
#     config = StagehandConfig(
#         env="LOCAL",
#         api_key=os.getenv("BROWSERBASE_API_KEY"),
#         project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
#         model_name="gemini/gemini-2.5-flash-preview-04-17",
#         model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
#         # Use verbose=2 for medium-detail logs (1=minimal, 3=debug)
#         verbose=2,
#     )

#     stagehand = SyncStagehand(
#         config=config, 
#         env="LOCAL",
#         api_url=os.getenv("STAGEHAND_API_URL"),
#     )
#     stagehand.init()
#     stagehand.page.page.goto("https://www.google.com")
#     time.sleep(100)
#     stagehand.close()

async def main():
    # Build a unified configuration object for Stagehand
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="google/gemini-2.5-flash-preview-04-17",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
        # Use verbose=2 for medium-detail logs (1=minimal, 3=debug)
        verbose=2,
        local_browser_launch_options={"viewport": {"width": 1440, "height": 810}},
    )

    stagehand = Stagehand(
        config=config, 
        env="BROWSERBASE",
        api_url=os.getenv("STAGEHAND_API_URL"),
    )
    await stagehand.init()
    page = stagehand.page
    # await stagehand.page.page.goto("https://www.elon.edu/u/imagining/about/kidzone/jokes-laughs/")
    # await page.goto("https://deviceandbrowserinfo.com/info_device")
    await page.goto("https://www.google.com")
    # await stagehand.page.page.goto("https://iframetester.com/?url=https://browserbase.com")
    # await asyncio.sleep(40)
    screenshot = await page._page.screenshot(full_page=False)
    screenshot_base64 = base64.b64encode(screenshot).decode()
    # agent = Agent(stagehand_client=stagehand, model="claude-3-7-sonnet-latest", max_steps=40)
    # agent = Agent(stagehand_client=stagehand, model="models/computer-use-exp", max_steps=50)
    agent = Agent(stagehand_client=stagehand, model="computer-use-preview", max_steps=40)
    result = await agent.execute("Search for the cheapest tickets in stubhub for the next ilia topuria's next ufc fight in vegas. DO NOT ASK ME ANY QUESTIONS")
    # result = await agent.execute("Order a fish pet for 166 Geary street. DO NOT ASK ME ANY QUESTIONS")
    # result = await agent.execute("Go learn why Stagehand is the best web browsing framework for AI agents. Compare it to other browser use frameworks, identifying strenghts and weaknesses. DO NOT ASK ME ANY QUESTIONS")
    # result = await agent.execute("can you get me my most recent i 94? When you're in the form, I will fill the data and you can continue onwards")
    # result = await agent.execute("can you analyze the sheet and make a combined chart of the other two?")
    # result = await agent.execute("can you summarize the last 3 emails")
    pprint(result.actions)
    print(result.message)
    pprint(result.completed)
    pprint(result.usage)
    # # await stagehand.page.mouse.wheel(0, 500)
    # tree = await get_accessibility_tree(stagehand.page, stagehand.logger)
    # with open("../tree.txt", "w") as f:
    #     f.write(tree.get("simplified"))

    # print(tree.get("idToUrl"))
    # print(tree.get("iframes"))
    # await page.act("click the button with text 'Get Started'")
    # res = await page.observe("the link to the first company")
    # # await page.act(res)
    # await page.act("click on the Browserbase link")
    # await page.extract("the text 'Get Started'")
    # # await page.locator("xpath=/html/body/div/ul[2]/li[2]/a").click()
    # # await page.wait_for_load_state('networkidle')
    # new_page = await stagehand.context.new_page()
    # await new_page.goto("https://www.google.com")
    # tree = await get_accessibility_tree(new_page, stagehand.logger)
    # with open("../tree.txt", "w") as f:
    #     f.write(tree.get("simplified"))
    # await new_page.act("click the button with text 'Get Started'")
    # # response = stagehand.llm.create_response(
    # #     messages=[
    # #         {
    # #             "role": "system",
    # #             "content": "Based on the provided accessibility tree of the page, find the element and the action the user is expecting to perform. The tree consists of an enhanced a11y tree from a website with unique identifiers prepended to each element's role, and name. The actions you can take are playwright compatible locator actions."
    # #         },
    # #         {
    # #             "role": "user",
    # #             "content": [
    # #                 {
    # #                     "type": "text",
    # #                     "text": f"fill the search bar with the text 'Hello'\nPage Tree:\n{tree.get('simplified')}"
    # #                 },
    # # #                 {
    # # #                     "type": "image_url",
    # # #                     "image_url": {
    # # # #                     "url": f"data:image/png;base64,{base64.b64encode(screenshot).decode()}"
    # # # #                 }
    # # #             }
    # #             ]
    # #         }
    # #     ],
    # #     model="gemini/gemini-2.5-flash-preview-04-17",
    # #     # model="openai/gpt-4o-mini",
    # #     response_format=Action,
    # # )
    # # print(response.choices[0].message.content)
    # # action = Action.model_validate_json(response.choices[0].message.content)

    # # args = { "backendNodeId": action.id }
    # # # Correctly call send_cdp in Python and extract the 'object' key
    # # result = await new_page.send_cdp("DOM.resolveNode", args)
    # # object_info = result.get("object") # Use .get for safer access
    # # print(object_info)
    # # xpath = await get_xpath_by_resolved_object_id(await new_page.get_cdp_client(), object_info["objectId"])
    # # print(xpath)
    # # if xpath:
    # #     await new_page.locator(f"xpath={xpath}").click()
    # #     await new_page.locator(f"xpath={xpath}").fill(action.arguments[0])
    # # else:
    # #     print("No xpath found")
    # await new_page.act("fill the search bar with the text 'Hello'")
    
    # # await asyncio.sleep(2)
    # await new_page.keyboard.press("Enter")
    # await asyncio.sleep(2)

    # # await new_page.observe("find the first result")
    # res = await new_page.observe("find the second search result")
    # #testing self heal
    # res[0].selector = "xpath=//diva[123]/div[2]/a[2]"
    # res[0].method = "click"

    # await new_page.act(res[0])
    # await page.observe("find the page header")
    # await page.act("click on the first post")
    # # await new_page.act("click on the first result")
    # await asyncio.sleep(100)

    # print("Received={}".format(response.choices[0].message.content))
    # pprint(json.loads(response.choices[0].message.content))
    # print(response.choices[0].message.parsed)
    # response = stagehand.llm.create_response(
    #     messages=[{"role": "user", "content": "Hello, how are you? can you tell me a few jokes?"}],
    #     model="gemini/gemini-2.0-flash",
    #     response_format=Jokes,
    # )
    # response_content = response.choices[0].message.content
    # response_cost = response._hidden_params["response_cost"]
    # print(f"Received={response_content}")
    # print(f"Cost={response_cost}")
    # print(Jokes.model_validate(json.loads(response.choices[0].message.content)))


    await stagehand.close()


if __name__ == "__main__":
    # Add a fancy header
    console.print(
        "\n",
        Panel.fit(
            "[light_gray]Stagehand 🤘 Python Example[/]",
            border_style="green",
            padding=(1, 10),
        ),
    )
    asyncio.run(main())