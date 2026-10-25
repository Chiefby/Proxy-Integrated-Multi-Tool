import os
import time
import threading
import psutil
import json
import requests
import shutil
import re
import ctypes
import tkinter as tk
import socket
import hashlib
import base64
from collections import deque
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── УСТАНОВКА ТИТУЛА ОКНА CMD ───────────────────────────────────
try:
    ctypes.windll.kernel32.SetConsoleTitleW("Multi-Tool | Proxy Integrated")
except Exception:
    pass

CONFIG_FILE = "config.json"

# ─── ЦВЕТОВЫЕ ТЕМЫ ───────────────────────────────────────────────
THEMES = {
    "Default (Green)": {
        "GREEN": "\033[92m", "WHITE": "\033[97m", "RED": "\033[91m", "YELLOW": "\033[93m", "GRAY": "\033[90m",
        "MINT": "\033[38;5;48m", "NEON": "\033[38;5;46m", "SUN": "\033[38;5;220m", "FLAME": "\033[38;5;202m",
        "LAV": "\033[38;5;141m", "SKY": "\033[38;5;117m", "ROSE": "\033[38;5;204m",
    },
    "Dracula": {
        "GREEN": "\033[38;5;141m", "WHITE": "\033[38;5;255m", "RED": "\033[38;5;203m", "YELLOW": "\033[38;5;222m", "GRAY": "\033[38;5;61m",
        "MINT": "\033[38;5;84m", "NEON": "\033[38;5;84m", "SUN": "\033[38;5;228m", "FLAME": "\033[38;5;203m",
        "LAV": "\033[38;5;81m", "SKY": "\033[38;5;81m", "ROSE": "\033[38;5;204m",
    },
    "Nord": {
        "GREEN": "\033[38;5;108m", "WHITE": "\033[38;5;231m", "RED": "\033[38;5;167m", "YELLOW": "\033[38;5;222m", "GRAY": "\033[38;5;59m",
        "MINT": "\033[38;5;109m", "NEON": "\033[38;5;108m", "SUN": "\033[38;5;222m", "FLAME": "\033[38;5;173m",
        "LAV": "\033[38;5;104m", "SKY": "\033[38;5;110m", "ROSE": "\033[38;5;167m",
    },
    "Tokyo Night": {
        "GREEN": "\033[38;5;113m", "WHITE": "\033[38;5;189m", "RED": "\033[38;5;204m", "YELLOW": "\033[38;5;215m", "GRAY": "\033[38;5;60m",
        "MINT": "\033[38;5;75m", "NEON": "\033[38;5;113m", "SUN": "\033[38;5;215m", "FLAME": "\033[38;5;204m",
        "LAV": "\033[38;5;141m", "SKY": "\033[38;5;111m", "ROSE": "\033[38;5;204m",
    },
    "Cyberpunk": {
        "GREEN": "\033[38;5;51m", "WHITE": "\033[38;5;231m", "RED": "\033[38;5;199m", "YELLOW": "\033[38;5;226m", "GRAY": "\033[38;5;240m",
        "MINT": "\033[38;5;51m", "NEON": "\033[38;5;51m", "SUN": "\033[38;5;226m", "FLAME": "\033[38;5;199m",
        "LAV": "\033[38;5;201m", "SKY": "\033[38;5;45m", "ROSE": "\033[38;5;199m",
    }
}

class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = WHITE = RED = YELLOW = GRAY = ""
    MINT = NEON = SUN = FLAME = LAV = SKY = ROSE = ""

if os.name == 'nt':
    os.system('')

def apply_theme(theme_name):
    theme = THEMES.get(theme_name, THEMES["Default (Green)"])
    for key, value in theme.items():
        setattr(C, key, value)

# ─── УТИЛИТЫ ─────────────────────────────────────────────────────
def get_banner():
    return f"""{C.GREEN}{C.BOLD}
    __  ___      ____  _    ______            __
   /  |/  /_  __/ / /_(_)  /_  __/___  ____  / /
  / /|_/ / / / / / __/ /    / / / __ \\/ __ \\/ / 
 / /  / / /_/ / / /_/ /    / / / /_/ / /_/ / /  
/_/  /_/\\__,_/_/\\__/_/    /_/  \\____/\\____/_/   
{C.RESET}{C.GRAY}                                                 created by - @chiefpriority{C.RESET}
"""

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"{C.GREEN}[+] Configuration saved to config.json{C.RESET}")

def format_proxy(proxy_str):
    if not proxy_str or proxy_str.lower() == "none": return ""
    proxy_str = proxy_str.strip()
    if "," in proxy_str:
        parts = [p.strip() for p in proxy_str.split(",")]
        if len(parts) == 4: return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    elif ":" in proxy_str:
        parts = [p.strip() for p in proxy_str.split(":")]
        if len(parts) == 4: return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        elif len(parts) == 2: return f"http://{parts[0]}:{parts[1]}"
    if "://" not in proxy_str: return f"http://{proxy_str}"
    return proxy_str

# ─── ПРОВЕРКА СТАТУСА ПРОКСИ ─────────────────────────────────────
last_ping_time = 0
cached_ping_str = ""
cached_country = ""
last_country_fetch = 0

def get_proxy_status(proxy_url):
    global last_ping_time, cached_ping_str, cached_country, last_country_fetch
    now = time.time()
    if now - last_ping_time < 3: return cached_ping_str
        
    if not proxy_url:
        cached_ping_str = f"{C.WHITE}[ Proxy: None | Direct ]{C.RESET}"
        last_ping_time = now
        return cached_ping_str
        
    safe_proxy = proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url
    ip = safe_proxy.split(':')[0]
    
    if not cached_country or now - last_country_fetch > 300:
        try:
            r_country = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
            if r_country.status_code == 200: cached_country = r_country.json().get("countryCode", "UN")
            else: cached_country = "UN"
        except: cached_country = "UN"
        last_country_fetch = now
        
    try:
        proxies = {"http": proxy_url, "https": proxy_url}
        start = time.time()
        r = requests.get("https://discord.com/api/v9/gateway", proxies=proxies, timeout=2)
        ms = int((time.time() - start) * 1000)
        
        if r.status_code == 200: cached_ping_str = f"{C.WHITE}[ Proxy: {cached_country} | {safe_proxy} | {ms}ms ]{C.RESET}"
        else: cached_ping_str = f"{C.WHITE}[ Proxy: {cached_country} | {safe_proxy} | Err {r.status_code} ]{C.RESET}"
    except Exception:
        cached_ping_str = f"{C.WHITE}[ Proxy: {cached_country} | {safe_proxy} | Dead ]{C.RESET}"
    last_ping_time = now
    return cached_ping_str

def print_bottom_right(text):
    visible_text = re.sub(r'\033\[[0-9;?]*[A-Za-z]', '', text)
    width = shutil.get_terminal_size((80, 20)).columns
    padding = max(0, width - len(visible_text) - 2)
    print(" " * padding + text)

# ─── DISCORD: AUTO SENDER ────────────────────────────────────────
def auto_sender(token, proxy_url):
    clear_console()
    raw_channels = input(f"{C.WHITE}Enter Channel ID(s) (comma-separated): {C.RESET}").strip()
    if not raw_channels: return
    channel_ids = [cid.strip() for cid in raw_channels.split(",") if cid.strip()]
    
    print(f"\n{C.WHITE}Enter the message text:{C.RESET}")
    message = ""
    clipboard_text = None
    try:
        root = tk.Tk(); root.withdraw(); clipboard_text = root.clipboard_get(); root.destroy()
    except Exception: pass

    if clipboard_text and len(clipboard_text.strip()) > 0:
        print(f"{C.GREEN}[+] Text detected in clipboard:{C.RESET}")
        print(f"{C.GRAY}{'-' * 50}{C.RESET}")
        preview = clipboard_text[:150].replace('\n', ' | ') 
        if len(clipboard_text) > 150: preview += "..."
        print(f"{C.WHITE}{preview}{C.RESET}")
        print(f"{C.GRAY}{'-' * 50}{C.RESET}")
        
        use_clip = input(f"{C.WHITE}Use this text from clipboard? (Y/n): {C.RESET}").strip().lower()
        if use_clip in ("", "y", "yes"):
            message = clipboard_text
            print(f"{C.GREEN}[+] Using text from clipboard.{C.RESET}")
        else: clipboard_text = None
            
    if not clipboard_text:
        print(f"{C.GRAY}(Type or paste text, then write 'END' on a new line to finish){C.RESET}")
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END": break
                lines.append(line)
            except EOFError: break
        message = "\n".join(lines)

    if not message.strip(): return
    try: interval_min = float(input(f"\n{C.WHITE}Interval in MINUTES (e.g., 5): {C.RESET}").strip())
    except ValueError: return

    interval_sec = interval_min * 60
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else {}

    clear_console()
    print(f"{C.GREEN}═══ AUTO SENDER ACTIVE ═══{C.RESET}\n")
    if proxy_url: print(f"{C.GRAY}Proxy:    {C.WHITE}{proxy_url.split('@')[-1]}{C.RESET}")
    print(f"{C.GRAY}Targets:  {C.WHITE}{len(channel_ids)} channel(s){C.RESET}")
    print(f"{C.GRAY}Interval: {C.WHITE}{interval_min} minutes{C.RESET}")
    print(f"{C.GRAY}Message:  {C.WHITE}{message[:30].replace('\n', ' ')}...{C.RESET}\n")
    print(f"{C.YELLOW}[!] Press Ctrl+C to stop.{C.RESET}\n")

    headers = {"Authorization": token, "Content-Type": "application/json"}

    try:
        while True:
            for cid in channel_ids:
                url = f"https://discord.com/api/v9/channels/{cid}/messages"
                try:
                    r = requests.post(url, headers=headers, json={"content": message}, proxies=proxies, timeout=15)
                    now = datetime.now().strftime("%H:%M:%S")
                    if r.status_code in (200, 201): print(f"{C.GRAY}[{now}]{C.RESET} {C.GREEN}✓ Sent to {cid}{C.RESET}")
                    elif r.status_code == 429: print(f"{C.GRAY}[{now}]{C.RESET} {C.YELLOW}⚠ Rate limited on {cid}.{C.RESET}")
                    else: print(f"{C.GRAY}[{now}]{C.RESET} {C.RED}✗ Failed {cid} (Code: {r.status_code}){C.RESET}")
                except Exception as e: print(f"{C.GRAY}[{datetime.now().strftime('%H:%M:%S')}]{C.RESET} {C.RED}✗ Error: {e}{C.RESET}")
                
                if cid != channel_ids[-1]: time.sleep(1.5) 
                    
            print(f"\n{C.WHITE}...waiting {interval_min} minutes...{C.RESET}\n")
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}[!] Auto Sender stopped by user.{C.RESET}")

# ─── DISCORD: TOKEN INFO ─────────────────────────────────────────
def discord_token_info(current_token, proxy_url):
    clear_console()
    print(f"{C.GREEN}DISCORD TOKEN INFO{C.RESET}\n")
    print(f" {C.WHITE}1. Check current token (from settings){C.RESET}")
    print(f" {C.WHITE}2. Check another token{C.RESET}")
    print(f" {C.WHITE}0. Back{C.RESET}\n")
    
    choice = input(f"{C.WHITE} > {C.RESET}").strip()
    if choice == "0": return
    
    token = ""
    if choice == "1":
        if not current_token:
            print(f"{C.RED}[-] No token saved in settings. Please input one.{C.RESET}")
            token = input(f"{C.WHITE}Enter token: {C.RESET}").strip()
        else:
            token = current_token
    elif choice == "2":
        token = input(f"{C.WHITE}Enter token to check: {C.RESET}").strip()
    else:
        return

    if not token: return
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else {}
    headers = {"Authorization": token, "Content-Type": "application/json"}

    clear_console()
    print(f"{C.GRAY}Fetching account info...{C.RESET}\n")
    try:
        r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, proxies=proxies, timeout=10)
        if r.status_code != 200:
            print(f"{C.RED}[-] Invalid token or proxy dead (Code: {r.status_code}){C.RESET}")
            input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")
            return
        
        data = r.json()
        print(f"{C.WHITE}Username:   {C.GREEN}{data.get('username')}#{data.get('discriminator', '0')}{C.RESET}")
        print(f"{C.WHITE}ID:         {C.GREEN}{data.get('id')}{C.RESET}")
        print(f"{C.WHITE}Email:      {C.GREEN}{data.get('email', 'Not linked')}{C.RESET}")
        print(f"{C.WHITE}Phone:      {C.GREEN}{data.get('phone', 'Not linked')}{C.RESET}")
        
        if data.get('premium_type', 0) > 0: print(f"{C.WHITE}Nitro:      {C.NEON}Yes (Type {data.get('premium_type')}){C.RESET}")
        else: print(f"{C.WHITE}Nitro:      {C.GRAY}No{C.RESET}")
            
        print(f"{C.WHITE}2FA:        {C.GREEN if data.get('mfa_enabled') else C.RED}{data.get('mfa_enabled')}{C.RESET}")
        print(f"{C.WHITE}Verified:   {C.GREEN if data.get('verified') else C.RED}{data.get('verified')}{C.RESET}")
    except Exception as e:
        print(f"{C.RED}[-] Network error: {e}{C.RESET}")
        input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")
        return

    try:
        r_guilds = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers, proxies=proxies, timeout=10)
        if r_guilds.status_code == 200: print(f"{C.WHITE}Servers:    {C.GREEN}{len(r_guilds.json())}{C.RESET}")
    except Exception: pass

    try:
        r_billing = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers, proxies=proxies, timeout=10)
        if r_billing.status_code == 200:
            cards = r_billing.json()
            if len(cards) > 0: print(f"{C.WHITE}Billing:    {C.NEON}{len(cards)} card(s) linked{C.RESET}")
            else: print(f"{C.WHITE}Billing:    {C.GRAY}None{C.RESET}")
    except Exception: pass

    print(f"\n{C.GRAY}Token preview: {token[:15]}...{token[-4:]}{C.RESET}")
    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── DISCORD: WEBHOOK TOOL ───────────────────────────────────────
def webhook_tool(proxy_url):
    clear_console()
    print(f"{C.GREEN}WEBHOOK TOOL{C.RESET}\n")
    url = input(f"{C.WHITE}Enter Webhook URL: {C.RESET}").strip()
    if not url: return

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else {}
    print(f"\n{C.GRAY}Fetching info...{C.RESET}\n")

    try:
        r = requests.get(url, proxies=proxies, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"{C.WHITE}Name:       {C.GREEN}{data.get('name')}{C.RESET}")
            print(f"{C.WHITE}Channel ID: {C.GREEN}{data.get('channel_id')}{C.RESET}")
            print(f"{C.WHITE}Guild ID:   {C.GREEN}{data.get('guild_id')}{C.RESET}")
            print(f"{C.WHITE}Token:      {C.GREEN}{data.get('token')}{C.RESET}")
            
            del_choice = input(f"\n{C.WHITE}Do you want to DELETE this webhook? (y/n): {C.RESET}").strip().lower()
            if del_choice == 'y':
                del_r = requests.delete(url, proxies=proxies, timeout=10)
                if del_r.status_code == 204:
                    print(f"{C.GREEN}[+] Webhook successfully deleted!{C.RESET}")
                else:
                    print(f"{C.RED}[-] Failed to delete webhook (Code: {del_r.status_code}){C.RESET}")
        else:
            print(f"{C.RED}[-] Invalid webhook or it was deleted (Code: {r.status_code}){C.RESET}")
    except Exception as e:
        print(f"{C.RED}[-] Error: {e}{C.RESET}")

    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── MAIN: MEMORY GUARD ──────────────────────────────────────────
def roblox_memory_guard():
    clear_console()
    print(f"{C.GREEN}ROBLOX MEMORY GUARD SETUP{C.RESET}\n")
    try:
        limit_in = input(f"{C.WHITE}Memory limit per process in MB [Default: 4000]: {C.RESET}").strip()
        mem_limit = int(limit_in) if limit_in else 4000
        hours_in = input(f"{C.WHITE}Close all every N hours [Default: 3]: {C.RESET}").strip()
        close_hours = float(hours_in) if hours_in else 3.0
    except ValueError: mem_limit, close_hours = 4000, 3.0

    clear_console()
    state = {"running": True, "processes": [], "closed_count": 0, "last_close": time.time(), "events": deque(maxlen=10)}
    exclude = ["account manager", "crashhandler", "crash handler", "crashpad"]

    def log(msg, color=C.SKY): state["events"].append(f"{C.GRAY}{time.strftime('%H:%M:%S')} {color}{msg}{C.RESET}")
    def fmt_clock(seconds):
        seconds = max(0, int(seconds)); h, rem = divmod(seconds, 3600); m, s = divmod(rem, 60); return f"{h}:{m:02d}:{s:02d}"

    def monitor_loop():
        while state["running"]:
            try:
                result = []
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        name = proc.info['name'].lower()
                        if "roblox" in name and not any(x in name for x in exclude):
                            mem = proc.memory_info().rss / 1024 / 1024
                            result.append({'proc': proc, 'name': proc.info['name'], 'pid': proc.info['pid'], 'mem': mem})
                    except Exception: pass
                state["processes"] = sorted(result, key=lambda x: x['mem'], reverse=True)
                
                for p in state["processes"]:
                    if p['mem'] > mem_limit:
                        p['proc'].kill(); state["closed_count"] += 1
                        log(f"closed {p['name']} #{p['pid']} - memory {int(p['mem'])}MB > {mem_limit}MB", C.GREEN)
                        break
                
                if (time.time() - state["last_close"]) / 3600 >= close_hours and state["processes"]:
                    log(f"scheduled close: {len(state['processes'])} process(es)", C.SUN)
                    for p in state["processes"]: p['proc'].kill(); state["closed_count"] += 1; time.sleep(2)
                    state["last_close"] = time.time()
                time.sleep(1)
            except Exception: time.sleep(2)

    threading.Thread(target=monitor_loop, daemon=True).start()
    print("\033[?25l", end="", flush=True)
    
    try:
        while state["running"]:
            clear_console()
            now = time.time()
            next_close_in = max(0, (close_hours * 3600) - (now - state["last_close"]))
            timer_color = C.NEON if next_close_in > 1800 else (C.SUN if next_close_in > 300 else C.FLAME)

            # Заголовок теперь C.GREEN
            print(f"{C.BOLD}{C.GREEN}⛨  Roblox Memory Guard {C.RESET}")
            print(f"{C.GRAY}{'─' * 54}{C.RESET}\n")
            print(f"  {C.GRAY}closed{C.RESET} {C.BOLD}{C.WHITE}{state['closed_count']}{C.RESET}    {C.GRAY}active{C.RESET} {C.BOLD}{C.WHITE}{len(state['processes'])}{C.RESET}    {C.GRAY}limit{C.RESET} {C.WHITE}{mem_limit} MB{C.RESET}")
            print(f"  {C.GRAY}next in  {C.RESET}{C.BOLD}{timer_color}{fmt_clock(next_close_in)}{C.RESET}    {C.GRAY}every{C.RESET} {C.WHITE}{close_hours}h{C.RESET}\n")
            print(f"  {C.GRAY}{'NAME':<24} {'PID':<8} {'MEMORY':>8}  {'STATUS'}{C.RESET}")
            print(f"  {C.GRAY}{'─' * 54}{C.RESET}")

            if state["processes"]:
                for p in state["processes"]:
                    ratio = p['mem'] / mem_limit
                    m_col, s_col, stat = (C.NEON, C.GREEN, "OK") if ratio < 0.6 else ((C.SUN, C.SUN, "HIGH") if ratio < 0.85 else ((C.FLAME, C.FLAME, "WARN") if ratio < 1.0 else (C.RED, C.RED, "CRIT")))
                    short_name = p['name'][:-4] if p['name'].lower().endswith('.exe') else p['name']
                    print(f"  {C.WHITE}{short_name[:24]:<24}{C.RESET} {C.LAV}{p['pid']:<8}{C.RESET} {m_col}{p['mem']:>6.0f} MB{C.RESET}  {C.BOLD}{s_col}{stat}{C.RESET}")
            else:
                print(f"  {C.GRAY}no roblox processes - waiting...{C.RESET}")

            print(f"\n  {C.GRAY}{'─' * 54}{C.RESET}")
            for event in list(state["events"])[-6:]: print(f"  {event}")
            print(f"\n  {C.GRAY}ctrl+c to return to menu{C.RESET}")
            time.sleep(1)
    except KeyboardInterrupt:
        state["running"] = False
        print("\033[?25h\n" + f"{C.YELLOW}[!] Memory Guard stopped.{C.RESET}")
        time.sleep(1)

# ─── MAIN: FAKE IDENTITY GEN ─────────────────────────────────────
def fake_identity():
    clear_console()
    print(f"{C.GREEN}FAKE IDENTITY GENERATOR{C.RESET}\n")
    print(f"{C.GRAY}Generating random person data...{C.RESET}\n")
    
    try:
        r = requests.get("https://randomuser.me/api/", timeout=10)
        if r.status_code == 200:
            data = r.json()['results'][0]
            print(f"{C.WHITE}Name:     {C.GREEN}{data['name']['first']} {data['name']['last']}{C.RESET}")
            print(f"{C.WHITE}Gender:   {C.GREEN}{data['gender'].capitalize()}{C.RESET}")
            print(f"{C.WHITE}DOB:      {C.GREEN}{data['dob']['date'][:10]}{C.RESET}")
            print(f"{C.WHITE}Email:    {C.GREEN}{data['email']}{C.RESET}")
            print(f"{C.WHITE}Phone:    {C.GREEN}{data['phone']}{C.RESET}")
            print(f"{C.WHITE}Username: {C.GREEN}{data['login']['username']}{C.RESET}")
            print(f"{C.WHITE}Password: {C.GREEN}{data['login']['password']}{C.RESET}")
            print(f"{C.WHITE}Address:  {C.GREEN}{data['location']['street']['number']} {data['location']['street']['name']}, {data['location']['city']}, {data['location']['country']}{C.RESET}")
        else:
            print(f"{C.RED}[-] API Error. Try again.{C.RESET}")
    except Exception as e:
        print(f"{C.RED}[-] Error: {e}{C.RESET}")

    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── MAIN: PORT SCANNER ──────────────────────────────────────────
def port_scanner():
    clear_console()
    print(f"{C.GREEN}ADVANCED PORT SCANNER{C.RESET}\n")
    target = input(f"{C.WHITE}Enter IP or Domain (e.g., 1.1.1.1 or google.com): {C.RESET}").strip()
    if not target: return

    try: ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"{C.RED}[-] Could not resolve hostname: {target}{C.RESET}")
        input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")
        return

    print(f"\n{C.GRAY}Target IP: {ip}\nScanning common ports...{C.RESET}\n")

    common_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
    open_ports = []

    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_port, p): p for p in common_ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
                print(f"{C.GREEN}[OPEN] Port {result}{C.RESET}")

    if not open_ports: print(f"{C.YELLOW}[-] No open ports found from the common list.{C.RESET}")
    else: print(f"\n{C.GREEN}[+] Scan complete. Found {len(open_ports)} open port(s).{C.RESET}")
    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── NETWORK: SOCIAL LOOKUP ──────────────────────────────────────
def social_media_lookup(proxy_url):
    clear_console()
    username = input(f"{C.WHITE}Enter target username: {C.RESET}").strip()
    if not username: return

    platforms = {
        "Twitter": f"https://twitter.com/{username}", "GitHub": f"https://github.com/{username}",
        "Instagram": f"https://instagram.com/{username}", "Reddit": f"https://reddit.com/user/{username}",
        "Telegram": f"https://t.me/{username}", "TikTok": f"https://tiktok.com/@{username}",
        "Pinterest": f"https://pinterest.com/{username}", "SoundCloud": f"https://soundcloud.com/{username}",
        "Twitch": f"https://twitch.tv/{username}", "Dribbble": f"https://dribbble.com/{username}", "Behance": f"https://behance.net/{username}"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else {}
    print(f"\n{C.GRAY}Checking {len(platforms)} platforms...{C.RESET}\n")

    def check_platform(platform, url):
        try: return platform, url, (requests.get(url, headers=headers, proxies=proxies, timeout=5).status_code == 200)
        except Exception: return platform, url, None

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_platform, p, u): p for p, u in platforms.items()}
        for future in as_completed(futures):
            platform, url, exists = future.result()
            if exists is True: print(f"{C.GREEN}[FOUND]  {platform:<12} -> {url}{C.RESET}")
            elif exists is False: print(f"{C.GRAY}[MISSING] {platform:<12} -> Not found{C.RESET}")
            else: print(f"{C.RED}[ERROR]  {platform:<12} -> Could not check{C.RESET}")

    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── NETWORK: PROXY SCANNER ──────────────────────────────────────
def proxy_scanner():
    clear_console()
    print(f"{C.GREEN}PROXY SCANNER{C.RESET}\n")
    print(f"{C.GRAY}Paste proxies (one per line). Type 'END' to start.{C.RESET}\n")

    raw_proxies = []
    while True:
        try:
            line = input().strip()
            if line.upper() == "END": break
            if line: raw_proxies.append(line)
        except EOFError: break

    if not raw_proxies: return
    print(f"\n{C.GRAY}Scanning {len(raw_proxies)} proxies...{C.RESET}\n")

    def check_proxy(raw_proxy):
        proxy_url = format_proxy(raw_proxy)
        if not proxy_url: return raw_proxy, "Invalid Format", 0, ""
        try:
            start = time.time()
            r = requests.get("http://ip-api.com/json?fields=66846719", proxies={"http": proxy_url, "https": proxy_url}, timeout=5)
            ping = int((time.time() - start) * 1000)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    return raw_proxy, "Alive", ping, f"{data.get('countryCode', 'UN')} | {data.get('isp', 'Unknown')}"
            return raw_proxy, "Dead", 0, ""
        except Exception: return raw_proxy, "Dead/Timeout", 0, ""

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_proxy, p): p for p in raw_proxies}
        alive_count = 0
        for future in as_completed(futures):
            raw, status, ping, info = future.result()
            if status == "Alive":
                alive_count += 1
                print(f"{C.GREEN}[ALIVE] {raw:<30} | {ping:>4}ms | {info}{C.RESET}")
            elif status == "Invalid Format": print(f"{C.YELLOW}[WARN]  {raw:<30} | Invalid format{C.RESET}")
            else: print(f"{C.RED}[DEAD]  {raw:<30} | {status}{C.RESET}")

    print(f"\n{C.GREEN}Done. Found {alive_count} alive proxies.{C.RESET}")
    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── NETWORK: IP/DOMAIN LOOKUP ───────────────────────────────────
def ip_domain_lookup(proxy_url):
    clear_console()
    print(f"{C.GREEN}DEEP IP/DOMAIN LOOKUP{C.RESET}\n")
    
    target = input(f"{C.WHITE}Enter IP or Domain: {C.RESET}").strip()
    if not target: return

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else {}
    
    try:
        ip = socket.gethostbyname(target)
        print(f"{C.GRAY}Resolved IP: {C.WHITE}{ip}{C.RESET}\n")
    except socket.gaierror:
        print(f"{C.RED}[-] Could not resolve hostname: {target}{C.RESET}")
        input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")
        return

    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", proxies=proxies, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                print(f"{C.WHITE}Country:     {C.GREEN}{data.get('country')} ({data.get('countryCode')}){C.RESET}")
                print(f"{C.WHITE}Region:      {C.GREEN}{data.get('regionName')}{C.RESET}")
                print(f"{C.WHITE}City:        {C.GREEN}{data.get('city')}{C.RESET}")
                print(f"{C.WHITE}ZIP Code:    {C.GREEN}{data.get('zip')}{C.RESET}")
                print(f"{C.WHITE}Latitude:    {C.GREEN}{data.get('lat')}{C.RESET}")
                print(f"{C.WHITE}Longitude:   {C.GREEN}{data.get('lon')}{C.RESET}")
                print(f"{C.WHITE}Timezone:    {C.GREEN}{data.get('timezone')}{C.RESET}")
                print(f"{C.WHITE}ISP:         {C.GREEN}{data.get('isp')}{C.RESET}")
                print(f"{C.WHITE}Organization:{C.GREEN} {data.get('org')}{C.RESET}")
                print(f"{C.WHITE}AS Number:   {C.GREEN}{data.get('as')}{C.RESET}")
            else:
                print(f"{C.RED}[-] Could not retrieve information for this IP.{C.RESET}")
        else:
            print(f"{C.RED}[-] API Request failed.{C.RESET}")
    except Exception as e:
        print(f"{C.RED}[-] Error: {e}{C.RESET}")

    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── OTHER: HASH TOOL ────────────────────────────────────────────
def hash_tool():
    clear_console()
    print(f"{C.GREEN}CRYPTO HASH & BASE64 TOOL{C.RESET}\n")
    
    text = input(f"{C.WHITE}Enter text to encode/hash: {C.RESET}").strip()
    if not text: return

    print(f"\n{C.GRAY}--- Results ---{C.RESET}")
    
    md5_hash = hashlib.md5(text.encode()).hexdigest()
    print(f"{C.WHITE}MD5:           {C.GREEN}{md5_hash}{C.RESET}")
    
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    print(f"{C.WHITE}SHA256:        {C.GREEN}{sha256_hash}{C.RESET}")
    
    b64_encode = base64.b64encode(text.encode()).decode()
    print(f"{C.WHITE}Base64 Encode: {C.GREEN}{b64_encode}{C.RESET}")
    
    try:
        b64_decode = base64.b64decode(text.encode()).decode()
        print(f"{C.WHITE}Base64 Decode: {C.GREEN}{b64_decode}{C.RESET}")
    except Exception:
        print(f"{C.WHITE}Base64 Decode: {C.GRAY}Input is not valid Base64{C.RESET}")

    input(f"\n{C.GRAY}Press Enter to return...{C.RESET}")

# ─── ГЛАВНОЕ МЕНЮ ───────────────────────────────────────────────
def main():
    global config
    config = load_config()
    apply_theme(config.get("theme", "Default (Green)"))
    
    token = config.get("token", "")
    proxy_url = config.get("proxy", "")

    clear_console()
    if not token:
        print(get_banner())
        print(f"{C.WHITE}[!] No token found.{C.RESET}")
        token = input(f"{C.WHITE}Enter your Discord token: {C.RESET}").strip()
        config["token"] = token
        save_config(config)
    if not proxy_url:
        print(f"{C.WHITE}[!] No proxy found (Press Enter to skip).{C.RESET}")
        new_proxy = input(f"{C.WHITE}Enter proxy (ip,port,user,pass): {C.RESET}").strip()
        proxy_url = format_proxy(new_proxy)
        config["proxy"] = proxy_url
        save_config(config)

    def pad(text, width):
        vis_len = len(re.sub(r'\033\[[0-9;?]*[A-Za-z]', '', text))
        return text + " " * max(0, width - vis_len)

    while True:
        clear_console()
        print(get_banner())
        
        c1, c2, c3 = 22, 22, 22
        
        # ИСПОЛЬЗУЕМ C.GREEN ВМЕСТО C.MINT ДЛЯ ЗАГОЛОВКОВ
        print(f" {C.GREEN}{C.BOLD}{'DISCORD':<{c1}} {'MAIN':<{c2}} {'NETWORK & OSINT':<{c3}} OTHER{C.RESET}")
        print(f" {C.GRAY}{'─'*(c1-2):<{c1}} {'─'*(c2-2):<{c2}} {'─'*(c3-2):<{c3}} {'─'*15}{C.RESET}")
        
        # Ряд 1
        r1_c1 = f"{C.WHITE}1. Auto Sender{C.RESET}"
        r1_c2 = f"{C.WHITE}4. Memory Guard{C.RESET}"
        r1_c3 = f"{C.WHITE}7. Social Lookup{C.RESET}"
        r1_c4 = f"{C.WHITE}10. Settings{C.RESET}"
        print(f" {pad(r1_c1, c1)}{pad(r1_c2, c2)}{pad(r1_c3, c3)}{r1_c4}")
        
        # Ряд 2
        r2_c1 = f"{C.WHITE}2. Token Checker{C.RESET}"
        r2_c2 = f"{C.WHITE}5. Fake ID Gen{C.RESET}"
        r2_c3 = f"{C.WHITE}8. Proxy Scanner{C.RESET}"
        r2_c4 = f"{C.WHITE}11. Hash Tool{C.RESET}"
        print(f" {pad(r2_c1, c1)}{pad(r2_c2, c2)}{pad(r2_c3, c3)}{r2_c4}")
        
        # Ряд 3
        r3_c1 = f"{C.WHITE}3. Webhook Tool{C.RESET}"
        r3_c2 = f"{C.WHITE}6. Port Scanner{C.RESET}"
        r3_c3 = f"{C.WHITE}9. IP Lookup{C.RESET}"
        r3_c4 = f"{C.WHITE}12. Exit{C.RESET}"
        print(f" {pad(r3_c1, c1)}{pad(r3_c2, c2)}{pad(r3_c3, c3)}{r3_c4}")
        
        print("\n" * 2)
        print_bottom_right(get_proxy_status(proxy_url))

        choice = input(f"{C.WHITE} > {C.RESET}").strip()

        if choice == "1": auto_sender(token, proxy_url)
        elif choice == "2": discord_token_info(token, proxy_url)
        elif choice == "3": webhook_tool(proxy_url)
        
        elif choice == "4": roblox_memory_guard()
        elif choice == "5": fake_identity()
        elif choice == "6": port_scanner()
        
        elif choice == "7": social_media_lookup(proxy_url)
        elif choice == "8": proxy_scanner()
        elif choice == "9": ip_domain_lookup(proxy_url)
        
        elif choice == "10":
            while True:
                clear_console()
                print(get_banner())
                
                masked_token = f"...{token[-4:]}" if token else "None"
                display_proxy = proxy_url.split('@')[-1] if '@' in proxy_url else (proxy_url or "None")
                current_theme = config.get("theme", "Default (Green)")
                
                print(f" {C.WHITE}1. Change Token (Current: {masked_token}){C.RESET}")
                print(f" {C.WHITE}2. Change Proxy (Current: {display_proxy}){C.RESET}")
                print(f" {C.WHITE}3. Change Theme (Current: {C.GREEN}{current_theme}{C.RESET})")
                print(f" {C.WHITE}0. Back to Main Menu{C.RESET}\n")
                
                sub_choice = input(f"{C.WHITE} > {C.RESET}").strip()
                
                if sub_choice == "1":
                    new_token = input(f"\n{C.WHITE}Enter new token (leave blank to cancel): {C.RESET}").strip()
                    if new_token:
                        config["token"] = new_token; token = new_token
                        save_config(config)
                        input(f"{C.GREEN}[+] Token updated. Press Enter...{C.RESET}")
                elif sub_choice == "2":
                    new_proxy = input(f"\n{C.WHITE}Enter new proxy (leave blank for None): {C.RESET}").strip()
                    config["proxy"] = format_proxy(new_proxy); proxy_url = config["proxy"]
                    save_config(config); last_ping_time = 0
                    input(f"{C.GREEN}[+] Proxy updated. Press Enter...{C.RESET}")
                elif sub_choice == "3":
                    clear_console()
                    print(f"{C.GREEN}AVAILABLE THEMES{C.RESET}\n")
                    theme_names = list(THEMES.keys())
                    for i, t_name in enumerate(theme_names):
                        print(f" {C.WHITE}{i+1}. {t_name}{C.RESET}")
                    
                    try:
                        t_choice = int(input(f"\n{C.WHITE}Select theme [1-{len(theme_names)}]: {C.RESET}").strip())
                        if 1 <= t_choice <= len(theme_names):
                            selected_theme = theme_names[t_choice-1]
                            config["theme"] = selected_theme
                            save_config(config)
                            apply_theme(selected_theme)
                            input(f"{C.GREEN}[+] Theme changed to {selected_theme}. Press Enter...{C.RESET}")
                    except ValueError:
                        pass
                elif sub_choice == "0": break
                
        elif choice == "11": hash_tool()
        elif choice == "12":
            print(f"\n{C.WHITE}Goodbye!{C.RESET}")
            break
        else:
            time.sleep(1)

if __name__ == "__main__":
    main()
