# Multi-Tool | Proxy Integrated

A comprehensive Python CLI multi-tool featuring Discord utilities, OSINT tools, network scanners, and Roblox process management. Built with a user-friendly interface, live proxy stats, and multiple color themes.

## Features

### Discord
- **Auto Sender:** Send messages to multiple Discord channels at custom intervals. Supports multi-line text and direct clipboard pasting.
- **Token Checker:** Fetch detailed info about any Discord token (Email, Phone, Nitro, 2FA, Server count, Billing methods).
- **Webhook Tool:** Fetch info about a webhook (Name, ID, Token) and instantly delete it if needed.

### Main
- **Roblox Memory Guard:** Monitors Roblox processes. Automatically closes them if they exceed a specified memory limit (MB) or run for too long. Ignores Crash Handlers.
- **Fake Identity Generator:** Generates realistic fake identities (Name, Address, Email, Password) via API.
- **Advanced Port Scanner:** Fast multi-threaded scanner for common network ports on any IP or domain.

### Network & OSINT
- **Social Media Lookup:** Fast multi-threaded username search across 11 popular platforms (GitHub, Twitter, Instagram, etc.).
- **Proxy Scanner:** Bulk-check proxies for validity, live ping, country, and ISP.
- **Deep IP/Domain Lookup:** Retrieves geolocation data, ISP, organization, and ASN for any IP or domain.

### Other
- **Settings Menu:** Easily change your Discord token, proxy address, or UI theme on the fly. Everything is saved locally.
- **Hash Tool:** Quickly generate MD5, SHA256 hashes and Encode/Decode Base64 text.

### General Features
- **Proxy Support:** Full integration for HTTP/SOCKS proxies. Auto-formats `ip:port:user:pass`. Shows proxy country and live ping status in the bottom right corner.
- **Custom Themes:** Choose from 5 built-in color schemes (Default Green, Dracula, Nord, Tokyo Night, Cyberpunk).

## Requirements
- Python 3.8+
- `requests`
- `psutil`

## Installation & Usage

1. Clone or download this repository.
2. Install the required libraries:
   ```bash
   pip install requests psutil
