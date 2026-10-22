Multi-Tool | Proxy Integrated

A simple Python command-line utility that includes a Discord Auto Sender, Memory Guard and a lot of features, for process managment.

Features:

Auto Sender
Allows you to send messages to multiple Discord channels at a specific interval. You can paste large, multi-line text directly from your clipboard, and the tool will send it without breaking the formatting.

Proxy Support
You can run the tool through an HTTP or SOCKS proxy. It automatically formats IP, Port, Login, and Password. It also shows the proxy country and live ping status at the bottom right of the screen.

Roblox Memory Guard
Monitors your Roblox processes. You can set a specific memory limit (MB) and a timer (hours). The tool will automatically close Roblox if it exceeds the limit or the time runs out. It safely ignores Crash Handlers.

Settings Menu
Easily change your Discord token or proxy address at any time without needing to restart the program. The configuration is saved locally in a config.json file.

Requirements:
- Python 3
- requests
- psutil

How to use:
1. Install the required libraries (pip install requests psutil).
2. Run the script.
3. Enter your Discord token and proxy when prompted (it will remember them).
4. Select a module from the main menu.
