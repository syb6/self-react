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


def prompt_value(current, message: str, *, hidden: bool = False, allow_empty: bool = False) -> str:
    current_value = str(current).strip() if current is not None else ""

    while True:
        try:
            value = (getpass.getpass(message) if hidden else input(message)).strip()
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt

        if value:
            return value
        if allow_empty and current_value:
            return current_value
        if allow_empty and not current_value:
            return ""
        print("This setting cannot be empty. Please try again.")


def ask_to_change_settings() -> str:
    while True:
        answer = input(
            "A setting.json file was found. Change settings? [y/N/skip]: "
        ).strip().lower()
        if answer in ("", "n", "no", "skip", "s"):
            return "skip"
        if answer in ("y", "yes"):
            return "change"
        print("Please enter y, n, or skip.")


def normalize_settings(settings: dict) -> tuple[str, int, str]:
    token = str(settings.get("token", "")).strip()
    channel_value = str(settings.get("channel_id", "")).strip()
    emoji = str(settings.get("emoji", "")).strip()

    if not token:
        raise ValueError("Missing Discord token in setting.json.")
    if not channel_value.isdigit():
        raise ValueError("Channel ID in setting.json must contain digits only.")
    if not emoji:
        raise ValueError("Missing emoji in setting.json.")

    return token, int(channel_value), emoji


def read_settings() -> tuple[str, int, str]:
    settings = load_settings()
    settings_exist = SETTINGS_FILE.exists() and bool(settings)

    if settings_exist:
        action = ask_to_change_settings()
        if action == "skip":
            return normalize_settings(settings)

    current_token = settings.get("token")
    token = prompt_value(
        current_token,
        "Enter Discord token (leave blank to keep the current token): " if current_token else "Enter Discord token: ",
        hidden=True,
        allow_empty=bool(current_token),
    )

    while True:
        current_channel = settings.get("channel_id")
        channel_input = prompt_value(
            current_channel,
            "Enter channel ID (leave blank to keep the current ID): " if current_channel else "Enter channel ID: ",
            allow_empty=bool(current_channel),
        )
        if channel_input.isdigit():
            target_channel_id = int(channel_input)
            break
        print("Channel ID must contain digits only. Please try again.")

    current_emoji = settings.get("emoji")
    emoji = prompt_value(
        current_emoji,
        "Enter emoji (leave blank to keep the current emoji): " if current_emoji else "Enter emoji: ",
        allow_empty=bool(current_emoji),
    )

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