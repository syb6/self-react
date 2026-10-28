# Discord reaction listener

This application uses `discord.py-self` to watch one Discord channel and add a reaction to every message sent there.

## Local setup

1. Install Python 3.10 or newer.
2. In the project folder, install the dependency:

   ```bash
   py -m pip install -r requirements.txt
   ```

3. Start the application:

   ```bash
   py main.py
   ```

4. If `setting.json` does not exist, enter the Discord token, channel ID, and emoji.
5. If `setting.json` already exists, choose whether to change it:
   - Enter `y` or `yes` to update the token, channel ID, and emoji.
   - Enter `n`, `skip`, or press Enter to keep all existing settings.
   - When changing settings, press Enter on a prompt to keep that individual setting unchanged.

The settings file is created in the same folder as `main.py` and uses this format:

```json
{
  "token": "your_discord_token_here",
  "channel_id": 123456789012345678,
  "emoji": "👍"
}
```

Keep `setting.json` private. It contains your account token and should never be committed or shared.

## Host on bot-hosting.net

1. Open [https://bot-hosting.net/a/](https://bot-hosting.net/a/) and sign in to the dashboard.
2. Create a new Python bot/application and choose an empty Python version that supports Python 3.10+.
3. Upload the project files, or connect the Git repository containing this project.
4. Make sure these files are present in the bot's root directory:
   - `main.py`
   - `requirements.txt`
   - `setting.json` if you want to use saved settings
5. In the hosting panel, set the startup command to:

   ```bash
   python main.py
   ```

6. Install dependencies from `requirements.txt` using the panel's install button, or run:

   ```bash
   pip install -r requirements.txt
   ```

7. On the panel, configure the bot's working directory so it starts in the folder containing `main.py`.
8. Start the bot and open the console. If the bot asks for settings, enter the token, channel ID, and emoji. If `setting.json` was uploaded, choose `skip` to use the existing settings.
9. If you use an environment that restarts or recreates files, upload `setting.json` again or set it through the bot console before each start. The bot will save it alongside `main.py`.

The hosting panel's exact button names may vary, but the required inputs are the Python startup file `main.py`, the dependency file `requirements.txt`, and the startup command above.

> Use this application only with Discord accounts and servers you are authorized to access. Discord user-account automation may violate Discord's Terms of Service.
