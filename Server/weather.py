"""
A little weather helper!

Imagine you have a robot friend. This file teaches the robot how to ask
the weather office (called the "National Weather Service") if there are
any weather warnings, like "Big storm coming!" or "It's going to snow a lot!".
"""

# "Any" is a special word that means "this could be anything at all".
from typing import Any
# "httpx" is like a mail carrier. It takes our questions to websites and brings back answers.
import httpx
# "MCPServer" is a toy kit that lets us build a helper robot that other programs can talk to.
from mcp.server.mcpserver import MCPServer

# Build our helper robot and give it the name "weather".
mcp = MCPServer("weather")


# This is the address of the weather office's house on the internet.
NWS_API_base = "https://api.weather.gov"
# This is our name tag, so the weather office knows who is knocking on its door.
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """
    Go ask the weather office a question and bring back the answer.

    It's like sending a letter to the weather office and waiting for a reply.
    If the reply comes back, we give it to whoever asked.
    If something goes wrong (the letter gets lost, or the office is closed),
    we give back "None", which means "I got nothing".

    Args:
        url: The exact address where we send our question.

    Returns:
        The weather office's answer (like a box of labeled toys),
        or None if something went wrong.
    """
    # "headers" is like the writing on the outside of our envelope.
    headers = {
        # Our name tag, so the weather office knows who sent the letter.
        "USER-Agent": USER_AGENT,
        # We are saying "Please write your answer in the kind of language we can read."
        "Accept": "application/geo+json"
    }
    # Call the mail carrier. When we're done, the mail carrier goes home by itself.
    async with httpx.AsyncClient() as Client:
        # "try" means "let's try this, and if anything breaks, don't cry, just go to 'except'."
        try:
            # Send our letter and wait for the reply. If it takes more than 30 seconds, stop waiting.
            response = await Client.get(url, headers=headers, timeout=30.0)
            # Check if the reply says "Oops, something went wrong". If it does, jump to "except".
            response.raise_for_status()
            # Open the reply and turn it into something Python can read, then give it back.
            return response.json()
        # If anything broke while we were trying...
        except Exception:
            # ...give back "None", which means "I got nothing".
            return None


def format_alert(feature: dict) -> str:
    """
    Turn one weather warning into nice, easy-to-read words.

    The weather office sends warnings in a messy box. This function takes
    things out of the box and lines them up neatly, like putting your toys
    on a shelf with labels.

    Args:
        feature: One weather warning, straight from the weather office.

    Returns:
        A neat little story about the warning.
    """
    # Inside each warning there is a smaller box called "properties" with all the details.
    pops = feature["properties"]
    # Make a neat list of details. If a detail is missing, we write "Unknown" instead.
    return f"""
                Event: {pops.get('event', 'Unknown')}
                Area: {pops.get('areaDesc', 'Unknown')}
                Severity: {pops.get('severity', 'Unknown')}
                Description: {pops.get('description', 'Unknown')}
                Instructions: {pops.get('instruction', 'Unknown')}
            """
    # Line by line, the list above says:
    #   Event       -> What is happening? (like "Flood Warning")
    #   Area        -> Where is it happening?
    #   Severity    -> How scary is it? (a little, or a lot?)
    #   Description -> The longer story of what's going on.
    #   Instructions-> What should people do to stay safe?


# This sticker tells our helper robot: "Hey, this is a job you know how to do!"
@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Find all the weather warnings for one US state.

    You tell it a state, like "CA" for California or "NY" for New York,
    and it tells you if there are any weather warnings there right now.

    Args:
        state: The two-letter short name of a US state (like "CA" or "TX").

    Returns:
        All the warnings written out neatly, or a message saying there are none.
    """
    # Build the exact address to ask: "What warnings do you have for this state?"
    url = f"{NWS_API_base}/alerts/active/area/{state}"
    # Send the question to the weather office and wait for the answer.
    data = await make_nws_request(url)

    # If we got no answer, or the answer doesn't have a "features" box (the list of warnings)...
    if not data or "features" not in data:
        # ...say we couldn't find any warnings.
        return "No alerts found"
    # If the "features" box is there but it's empty (no warnings at all)...
    if not data["features"]:
        # ...say there are no warnings. Yay, the weather is calm!
        return "No alerts found"

    # Take every warning, one by one, and turn each into neat words.
    alerts = [format_alert(feature) for feature in data["features"]]
    # Glue all the neat warnings together, with a "---" line between each one, and give them back.
    return "\n---\n".join(alerts)


# "__main__" means "someone ran this file directly" (not just borrowed parts of it).
if __name__ == "__main__":
    # Wake up the helper robot and let it listen for questions.
    mcp.run(transport="stdio")
