import asyncio
import getpass
import json
import sys
from pathlib import Path

try:
    import discord
except ImportError:
    print("Error: discord.py-self is not installed.")
    print("Install it with: py -m pip install discord.py-self")
    sys.exit(1)

SETTINGS_FILE = Path(__file__).resolve().with_name("setting.json")


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return {}

    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"Warning: invalid JSON in {SETTINGS_FILE}: {error}")
        print("The settings will be replaced with values entered below.")
        return {}
    except UnicodeDecodeError as error:
        print(f"Error: {SETTINGS_FILE} is not valid UTF-8: {error}")
        return {}
    except OSError as error:
        print(f"Error: could not read {SETTINGS_FILE}: {error}")
        return {}

    if not isinstance(settings, dict):
        print(f"Warning: {SETTINGS_FILE} must contain a JSON object.")
        return {}
    return settings


def prompt_value(current, message: str, *, hidden: bool = False) -> str:
    value = str(current).strip() if current is not None else ""
    if value:
        return value

    while True:
        try:
            value = (getpass.getpass(message) if hidden else input(message)).strip()
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt
        if value:
            return value
        print("This setting cannot be empty. Please try again.")


def read_settings() -> tuple[str, int, str]:
    settings = load_settings()

    token = prompt_value(settings.get("token"), "Enter Discord token: ", hidden=True)

    while True:
        channel_input = prompt_value(settings.get("channel_id"), "Enter channel ID: ")
        if not channel_input.isdigit():
            print("Channel ID must contain digits only. Please try again.")
            settings["channel_id"] = ""
            continue

        target_channel_id = int(channel_input)
        break

    emoji = prompt_value(settings.get("emoji"), "Enter emoji: ")

    settings.update({
        "token": token,
        "channel_id": target_channel_id,
        "emoji": emoji,
    })

    try:
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        print(f"Settings saved to {SETTINGS_FILE}")
    except OSError as error:
        print(f"Error: could not save {SETTINGS_FILE}: {error}")
        sys.exit(1)

    return token, target_channel_id, emoji


async def run(token: str, target_channel_id: int, emoji: str) -> None:
    client = discord.Client(self_bot=True)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user} ({client.user.id})")
        print(f"Watching channel ID {target_channel_id} and reacting with {emoji}")

    @client.event
    async def on_message(message):
        if message.channel.id != target_channel_id:
            return

        try:
            await message.add_reaction(emoji)
            print(f"Reacted to message in channel {target_channel_id} by {message.author}")
        except discord.Forbidden:
            print("Error: missing permission to add a reaction in the target channel.")
        except discord.HTTPException as error:
            print(f"Discord API error while reacting: {error}")
        except Exception as error:
            print(f"Unexpected error while reacting: {error}")

    @client.event
    async def on_error(event, *args, **kwargs):
        print(f"Discord client error in event {event}: {sys.exc_info()[1]}")

    try:
        await client.start(token)
    except discord.LoginFailure:
        print("Error: the Discord token is invalid or expired.")
    except discord.HTTPException as error:
        print(f"Discord API connection error: {error}")
    except discord.GatewayNotFound:
        print("Error: could not find the Discord gateway.")
    except asyncio.CancelledError:
        print("Client stopped.")
    except KeyboardInterrupt:
        print("Stopping client...")
    except Exception as error:
        print(f"Unexpected Discord client error: {type(error).__name__}: {error}")
    finally:
        if not client.is_closed():
            await client.close()


def main() -> None:
    try:
        token, target_channel_id, emoji = read_settings()
        asyncio.run(run(token, target_channel_id, emoji))
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()