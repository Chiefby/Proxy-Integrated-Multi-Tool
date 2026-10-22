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
from collections import deque
from datetime import datetime

# ─── УСТАНОВКА ТИТУЛА ОКНА CMD ───────────────────────────────────
try:
    ctypes.windll.kernel32.SetConsoleTitleW("Multi-Tool | Proxy Integrated")
except Exception:
    pass

CONFIG_FILE = "config.json"

# ─── ЦВЕТА MULTI-TOOL ────────────────────────────────────────────
class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    WHITE = '\033[97m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GRAY = '\033[90m'
    MINT = "\033[38;5;48m"
    NEON = "\033[38;5;46m"
    SUN = "\033[38;5;220m"
    FLAME = "\033[38;5;202m"
    LAV = "\033[38;5;141m"
    SKY = "\033[38;5;117m"
    ROSE = "\033[38;5;204m"

if os.name == 'nt':
    os.system('')

BANNER = f"""{C.GREEN}{C.BOLD}
    __  ___      ____  _    ______            __
   /  |/  /_  __/ / /_(_)  /_  __/___  ____  / /
  / /|_/ / / / / / __/ /    / / / __ \\/ __ \\/ / 
 / /  / / /_/ / / /_/ /    / / / /_/ / /_/ / /  
/_/  /_/\\__,_/_/\\__/_/    /_/  \\____/\\____/_/   
{C.RESET}{C.GRAY}                                                   created by - @chiefpriority{C.RESET}
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
    if not proxy_str or proxy_str.lower() == "none":
        return ""
    proxy_str = proxy_str.strip()
    if "," in proxy_str:
        parts = [p.strip() for p in proxy_str.split(",")]
        if len(parts) == 4:
            return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    elif ":" in proxy_str:
        parts = [p.strip() for p in proxy_str.split(":")]
        if len(parts) == 4: 
            return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        elif len(parts) == 2: 
            return f"http://{parts[0]}:{parts[1]}"
    if "://" not in proxy_str:
        return f"http://{proxy_str}"
    return proxy_str

# ─── ПРОВЕРКА СТАТУСА ПРОКСИ (СТРАНА + ПИНГ) ─────────────────────
last_ping_time = 0
cached_ping_str = ""
cached_country = ""
last_country_fetch = 0

def get_proxy_status(proxy_url):
    global last_ping_time, cached_ping_str, cached_country, last_country_fetch
    now = time.time()
    
    if now - last_ping_time < 3:
        return cached_ping_str
        
    if not proxy_url:
        cached_ping_str = f"{C.WHITE}[ Proxy: None | Direct ]{C.RESET}"
        last_ping_time = now
        return cached_ping_str
        
    safe_proxy = proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url
    ip = safe_proxy.split(':')[0]
    
    if not cached_country or now - last_country_fetch > 300:
        try:
            r_country = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
            if r_country.status_code == 200:
                data = r_country.json()
                cached_country = data.get("countryCode", "UN")
            else:
                cached_country = "UN"
        except:
            cached_country = "UN"
        last_country_fetch = now
        
    try:
        proxies = {"http": proxy_url, "https": proxy_url}
        start = time.time()
        r = requests.get("https://discord.com/api/v9/gateway", proxies=proxies, timeout=2)
        ms = int((time.time() - start) * 1000)
        
        if r.status_code == 200:
            cached_ping_str = f"{C.WHITE}[ Proxy: {cached_country} | {safe_proxy} | {ms}ms ]{C.RESET}"
        else:
            cached_ping_str = f"{C.WHITE}[ Proxy: {cached_country} | {safe_proxy} | Err {r.status_code} ]{C.RESET}"
    except Exception:
        cached_ping_str = f"{C.WHITE}[ Proxy: {cached_country} | {safe_proxy} | Dead ]{C.RESET}"
        
    last_ping_time = now
    return cached_ping_str

def print_bottom_right(text):
    visible_text = re.sub(r'\033\[[0-9;?]*[A-Za-z]', '', text)
    width = shutil.get_terminal_size((80, 20)).columns
    padding = max(0, width - len(visible_text) - 2)
    print(" " * padding + text)

# ─── AUTO SENDER ─────────────────────────────────────────────────
def auto_sender(token, proxy_url):
    clear_console()
    
    # 1. Ввод каналов
    raw_channels = input(f"{C.WHITE}Enter Channel ID(s) (comma-separated): {C.RESET}").strip()
    if not raw_channels: return
    channel_ids = [cid.strip() for cid in raw_channels.split(",") if cid.strip()]
    
    # 2. Ввод текста (с проверкой буфера обмена)
    print(f"\n{C.WHITE}Enter the message text:{C.RESET}")
    
    message = ""
    clipboard_text = None
    try:
        root = tk.Tk()
        root.withdraw()
        clipboard_text = root.clipboard_get()
        root.destroy()
    except Exception:
        pass

    if clipboard_text and len(clipboard_text.strip()) > 0:
        print(f"{C.GREEN}[+] Text detected in clipboard:{C.RESET}")
        print(f"{C.GRAY}{'-' * 50}{C.RESET}")
        preview = clipboard_text[:200].replace('\n', ' | ') 
        if len(clipboard_text) > 200: preview += "..."
        print(f"{C.WHITE}{preview}{C.RESET}")
        print(f"{C.GRAY}{'-' * 50}{C.RESET}")
        
        use_clip = input(f"{C.WHITE}Use this text from clipboard? (Y/n): {C.RESET}").strip().lower()
        if use_clip in ("", "y", "yes"):
            message = clipboard_text
            print(f"{C.GREEN}[+] Using text from clipboard.{C.RESET}")
        else:
            clipboard_text = None
            
    if not clipboard_text:
        print(f"{C.GRAY}(Type or paste text, then write 'END' on a new line to finish){C.RESET}")
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            except EOFError:
                break
        message = "\n".join(lines)

    if not message.strip():
        print(f"{C.RED}[-] Message cannot be empty.{C.RESET}")
        time.sleep(2)
        return

    # 3. Ввод интервала
    try:
        interval_min = float(input(f"\n{C.WHITE}Interval in MINUTES (e.g., 5): {C.RESET}").strip())
    except ValueError: 
        return

    interval_sec = interval_min * 60
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else {}

    # ─── ОЧИСТКА ЭКРАНА ПЕРЕД НАЧАЛОМ ОТПРАВКИ ───
    clear_console()
    
    # Небольшая чистая шапка, чтобы было понятно, что происходит
    print(f"{C.GREEN}═══ AUTO SENDER ACTIVE ═══{C.RESET}\n")
    if proxy_url:
        safe_proxy = proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url
        print(f"{C.GRAY}Proxy:    {C.WHITE}{safe_proxy}{C.RESET}")
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
                    response = requests.post(url, headers=headers, json={"content": message}, proxies=proxies, timeout=15)
                    now = datetime.now().strftime("%H:%M:%S")
                    if response.status_code in (200, 201):
                        print(f"{C.GRAY}[{now}]{C.RESET} {C.GREEN}✓ Sent to {cid}{C.RESET}")
                    elif response.status_code == 429:
                        print(f"{C.GRAY}[{now}]{C.RESET} {C.YELLOW}⚠ Rate limited on {cid}.{C.RESET}")
                    else:
                        print(f"{C.GRAY}[{now}]{C.RESET} {C.RED}✗ Failed {cid} (Code: {response.status_code}){C.RESET}")
                except Exception as e:
                    print(f"{C.GRAY}[{datetime.now().strftime('%H:%M:%S')}]{C.RESET} {C.RED}✗ Error: {e}{C.RESET}")
                
                if cid != channel_ids[-1]: 
                    time.sleep(1.5) 
                    
            print(f"\n{C.WHITE}...waiting {interval_min} minutes...{C.RESET}\n")
            time.sleep(interval_sec)
            
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}[!] Auto Sender stopped by user.{C.RESET}")

# ─── ROBLOX MEMORY GUARD ─────────────────────────────────────────
def roblox_memory_guard():
    clear_console()
    print(f"{C.GREEN}ROBLOX MEMORY GUARD SETUP{C.RESET}\n")
    
    try:
        limit_in = input(f"{C.WHITE}Memory limit per process in MB [Default: 4000]: {C.RESET}").strip()
        mem_limit = int(limit_in) if limit_in else 4000
        
        hours_in = input(f"{C.WHITE}Close all every N hours [Default: 3]: {C.RESET}").strip()
        close_hours = float(hours_in) if hours_in else 3.0
    except ValueError:
        print(f"{C.RED}[-] Invalid input. Using defaults.{C.RESET}")
        time.sleep(2)
        mem_limit, close_hours = 4000, 3.0

    clear_console()

    state = {
        "running": True,
        "processes": [],
        "closed_count": 0,
        "last_close": time.time(),
        "events": deque(maxlen=10)
    }
    
    keyword = "roblox"
    exclude = ["account manager", "crashhandler", "crash handler", "crashpad"]

    def log(msg, color=C.SKY):
        timestamp = time.strftime("%H:%M:%S")
        line = f"{C.GRAY}{timestamp} {color}{msg}{C.RESET}"
        state["events"].append(line)

    def fmt_clock(seconds):
        seconds = max(0, int(seconds))
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h}:{m:02d}:{s:02d}"

    def find_roblox():
        result = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                name = proc.info['name'].lower()
                if keyword in name and not any(x in name for x in exclude):
                    mem = proc.memory_info().rss / 1024 / 1024
                    result.append({'proc': proc, 'name': proc.info['name'], 'pid': proc.info['pid'], 'mem': mem})
            except Exception:
                pass
        return sorted(result, key=lambda x: x['mem'], reverse=True)

    def kill_process(proc, reason):
        try:
            proc.kill()
            state["closed_count"] += 1
            log(f"closed {proc.info['name']} #{proc.info['pid']} - {reason}", C.GREEN)
            return True
        except Exception as e:
            log(f"failed to close {proc.info['name']}: {e}", C.ROSE)
            return False

    def monitor_loop():
        while state["running"]:
            try:
                state["processes"] = find_roblox()
                for p in state["processes"]:
                    if p['mem'] > mem_limit:
                        kill_process(p['proc'], f"memory {int(p['mem'])}MB > {mem_limit}MB")
                        state["processes"] = find_roblox()
                        break
                if (time.time() - state["last_close"]) / 3600 >= close_hours and state["processes"]:
                    log(f"scheduled close: {len(state['processes'])} process(es)", C.SUN)
                    for p in state["processes"]:
                        kill_process(p['proc'], "scheduled")
                        time.sleep(2)
                    state["last_close"] = time.time()
                time.sleep(1)
            except Exception as e:
                log(f"error: {e}", C.ROSE)
                time.sleep(2)

    log(f"started - limit {mem_limit}MB | close every {close_hours}h", C.SKY)
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    print("\033[?25l", end="", flush=True)
    
    try:
        while state["running"]:
            now = time.time()
            next_close_in = max(0, (close_hours * 3600) - (now - state["last_close"]))

            if next_close_in > 30 * 60: timer_color = C.NEON
            elif next_close_in > 5 * 60: timer_color = C.SUN
            else: timer_color = C.FLAME

            print("\033[H", end="")

            print(f"{C.BOLD}{C.MINT}⛨  Roblox Memory Guard {C.RESET}")
            print(f"{C.GRAY}{'─' * 54}{C.RESET}\n")

            print(f"  {C.GRAY}closed{C.RESET} {C.BOLD}{C.WHITE}{state['closed_count']}{C.RESET}"
                  f"    {C.GRAY}active{C.RESET} {C.BOLD}{C.WHITE}{len(state['processes'])}{C.RESET}"
                  f"    {C.GRAY}limit{C.RESET} {C.WHITE}{mem_limit} MB{C.RESET}")
            
            print(f"  {C.GRAY}next in  {C.RESET}{C.BOLD}{timer_color}{fmt_clock(next_close_in)}{C.RESET}"
                  f"    {C.GRAY}every{C.RESET} {C.WHITE}{close_hours}h{C.RESET}\n")

            print(f"  {C.GRAY}{'NAME':<24} {'PID':<8} {'MEMORY':>8}  {'STATUS'}{C.RESET}")
            print(f"  {C.GRAY}{'─' * 54}{C.RESET}")

            if state["processes"]:
                for p in state["processes"]:
                    ratio = p['mem'] / mem_limit
                    if ratio < 0.60: mem_color, status_color, status = C.NEON, C.GREEN, "OK"
                    elif ratio < 0.85: mem_color, status_color, status = C.SUN, C.SUN, "HIGH"
                    elif ratio < 1.0: mem_color, status_color, status = C.FLAME, C.FLAME, "WARN"
                    else: mem_color, status_color, status = C.RED, C.RED, "CRIT"

                    short_name = p['name'][:-4] if p['name'].lower().endswith('.exe') else p['name']
                    print(f"  {C.WHITE}{short_name[:24]:<24}{C.RESET} "
                          f"{C.LAV}{p['pid']:<8}{C.RESET} "
                          f"{mem_color}{p['mem']:>6.0f} MB{C.RESET}  "
                          f"{C.BOLD}{status_color}{status}{C.RESET}")
            else:
                print(f"  {C.GRAY}no roblox processes - waiting...{C.RESET}")

            print(f"\n  {C.GRAY}{'─' * 54}{C.RESET}")
            recent = list(state["events"])[-6:]
            for event in recent: print(f"  {event}")
            if not recent: print(f"  {C.GRAY}no events yet{C.RESET}")

            print(f"\n  {C.GRAY}ctrl+c to return to menu{C.RESET}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        state["running"] = False
        print("\033[?25h")
        print(f"\n{C.YELLOW}[!] Memory Guard stopped. Returning to menu...{C.RESET}")
        time.sleep(1)

# ─── ГЛАВНОЕ МЕНЮ ───────────────────────────────────────────────
def main():
    clear_console()
    config = load_config()
    token = config.get("token", "")
    proxy_url = config.get("proxy", "")

    if not token:
        print(BANNER)
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

    while True:
        clear_console()
        print(BANNER)
        
        print(f" {C.WHITE}1. Auto Sender (Discord){C.RESET}")
        print(f" {C.WHITE}2. Roblox Memory Guard{C.RESET}")
        print(f" {C.WHITE}3. Settings{C.RESET}")
        print(f" {C.WHITE}4. Exit{C.RESET}")
        print()

        print_bottom_right(get_proxy_status(proxy_url))

        choice = input(f"{C.WHITE} > {C.RESET}").strip()

        if choice == "1":
            auto_sender(token, proxy_url)
            input(f"\n{C.GRAY}Press Enter to return to menu...{C.RESET}")
        
        elif choice == "2":
            roblox_memory_guard()
        
        elif choice == "3":
            while True:
                clear_console()
                print(BANNER)
                print() 
                
                masked_token = f"...{token[-4:]}" if token else "None"
                display_proxy = proxy_url.split('@')[-1] if '@' in proxy_url else (proxy_url or "None")
                
                print(f" {C.WHITE}1. Change Token (Current: {masked_token}){C.RESET}")
                print(f" {C.WHITE}2. Change Proxy (Current: {display_proxy}){C.RESET}")
                print(f" {C.WHITE}0. Back to Main Menu{C.RESET}\n")
                
                sub_choice = input(f"{C.WHITE} > {C.RESET}").strip()
                
                if sub_choice == "1":
                    new_token = input(f"\n{C.WHITE}Enter new token (leave blank to cancel): {C.RESET}").strip()
                    if new_token:
                        config["token"] = new_token
                        token = new_token
                        save_config(config)
                        input(f"{C.GREEN}[+] Token updated. Press Enter...{C.RESET}")
                        
                elif sub_choice == "2":
                    new_proxy = input(f"\n{C.WHITE}Enter new proxy (leave blank for None): {C.RESET}").strip()
                    config["proxy"] = format_proxy(new_proxy)
                    proxy_url = config["proxy"]
                    save_config(config)
                    last_ping_time = 0
                    input(f"{C.GREEN}[+] Proxy updated. Press Enter...{C.RESET}")
                    
                elif sub_choice == "0":
                    break
        
        elif choice == "4":
            print(f"\n{C.WHITE}Goodbye!{C.RESET}")
            break
        else:
            print(f"{C.RED}[-] Invalid choice.{C.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
