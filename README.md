# Discord reaction listener

This application uses the `discord.py-self` package through Discord's `discord` Python module.

1. Install dependencies with `py -m pip install -r requirements.txt`.
2. Run `python main.py`.
3. If `setting.json` is missing or any setting is empty, enter the Discord token, channel ID, and emoji in the console.
4. The settings are saved to `setting.json` in the project folder on first run.

The `setting.json` format is:

```json
{
  "token": "your_discord_token_here",
  "channel_id": 123456789012345678,
  "emoji": "👍"
}
```
