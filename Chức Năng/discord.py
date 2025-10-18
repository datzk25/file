# -*- coding: utf-8 -*-
"""
🌌 NovaX Discord Spam Tool — Premium V5.0
Developer : NovaX Team
Admin     : Tiến Đạt (Real)
"""

import os
import asyncio
import requests
import socket
import shutil
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# ===== MÀU NEON / HIỆU ỨNG GRADIENT =====
def rgb(r,g,b,t): return f"\033[38;2;{r};{g};{b}m{t}\033[0m"
def grad(text,c1,c2):
    out=""; n=max(1,len(text)-1)
    for i,ch in enumerate(text):
        t=i/n
        r=int(c1[0]+(c2[0]-c1[0])*t)
        g=int(c1[1]+(c2[1]-c1[1])*t)
        b=int(c1[2]+(c2[2]-c1[2])*t)
        out+=rgb(r,g,b,ch)
    return out

def clear(): os.system("cls" if os.name=="nt" else "clear")
def width():
    try: return shutil.get_terminal_size().columns-4
    except: return 80

PALETTES=[
    ((255,0,255),(0,255,255)),
    ((255,150,50),(255,80,200)),
    ((120,190,255),(50,255,200)),
    ((180,130,255),(255,100,200)),
    ((80,255,160),(255,100,255))
]
def theme(): return PALETTES[0]
def neon_border(w,c1,c2): return grad("—"*w,c1,c2)
def neon_box(title="", lines=None, c1=(255,0,255), c2=(0,255,255)):
    w = width()
    b = neon_border(w,c1,c2)
    print(f"+{b}+")
    if title:
        t = grad(f" {title} ", c1,c2)
        print(f"|{t.center(w)}")
        print(f"+{b}+")
    for line in lines or []:
        inner = grad(line.strip(), (240,240,255),(200,255,255))
        print(f"| {inner:<{w-2}}")
    print(f"+{b}+")

# ===== BANNER =====
def banner():
    clear()
    c1,c2 = theme()
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    try:
        ip = requests.get("https://api.ipify.org").text.strip()
    except:
        ip = "Không xác định"

    logo = [
        "███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ██╗  ██╗",
        "████╗  ██║██╔═══██╗██║   ██║██╔══██╗╚██╗██╔╝",
        "██╔██╗ ██║██║   ██║██║   ██║███████║ ╚███╔╝ ",
        "██║╚██╗██║██║   ██║██║   ██║██╔══██║ ██╔██╗ ",
        "██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██╔╝ ██╗",
        "╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝",
    ]
    for l in logo: print(grad(l,c1,c2))
    print(grad("🌌 NOVAX DISCORD SPAM TOOL 🌌", (255,255,150), c2))
    neon_box("THÔNG TIN TOOL", [
        "👑 Admin     : Tiến Đạt (Real)",
        f"📅 Khởi chạy : {now}",
        "⚡ Phiên bản : Premium V5.0",
        "🌈 Developer : NovaX Team",
        f"🌐 Thiết bị  : {ip}"
    ], c1,c2)
    print()

# ===== HÀM DÙNG CHUNG =====
def clean_line_for_hash(line):
    stripped = line.lstrip('#').lstrip()
    return "# > " + stripped if stripped else ""

def input_label(label):
    print(grad(f"{label}:", (255,255,180),(255,100,255)))
    value = input(grad("➤ Nhập: ", (150,255,255),(255,180,255))).strip()
    print(f"\033[F\033[K> {Fore.CYAN}{value}{Style.RESET_ALL}")
    return value

# ===== NHÂY ROUND-ROBIN + ONLINE/OFFLINE =====
async def spam_nhay_status(tokens, channel_id, message_file, delay, mention_ids=None, name_mention=None):
    headers_list = [{"Authorization": t, "Content-Type": "application/json"} for t in tokens]
    with open(message_file, "r", encoding="utf-8-sig") as f:
        messages = [clean_line_for_hash(line) for line in f if line.strip()]
    if not messages:
        print(Fore.RED + "File nhay.txt rỗng!")
        return
    token_count = len(tokens)
    msg_idx = 0
    token_idx = 0

    while True:
        msg = messages[msg_idx]
        if mention_ids:
            tags = " ".join(f"<@{uid}>" for uid in mention_ids)
            msg = f"{msg} {tags}"
        if name_mention:
            msg = msg.replace("(name)", name_mention)

        token = tokens[token_idx]
        headers = headers_list[token_idx]
        url_typing = f"https://discord.com/api/v9/channels/{channel_id}/typing"
        url_send = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        try:
            requests.post(url_typing, headers=headers)
            await asyncio.sleep(1.5)
            r = requests.post(url_send, json={"content": msg}, headers=headers)
            if r.status_code in (200,201):
                status = Fore.GREEN + "Online ✅"
            else:
                status = Fore.RED + "Offline ❌"
        except Exception:
            status = Fore.RED + "Offline ❌"
        print(f"{Fore.YELLOW}Token {token_idx+1}{Fore.RESET} | {Fore.CYAN}ID nhóm: {channel_id}{Fore.RESET} | {status}")
        token_idx = (token_idx + 1) % token_count
        msg_idx = (msg_idx + 1) % len(messages)
        await asyncio.sleep(delay)

# ===== NGÔN ROUND-ROBIN + ONLINE/OFFLINE =====
async def spam_ngon_status(tokens, channel_id, message_file, delay):
    headers_list = [{"Authorization": t, "Content-Type": "application/json"} for t in tokens]
    with open(message_file, "r", encoding="utf-8-sig") as f:
        messages = [line.strip() for line in f if line.strip()]
    if not messages:
        print(Fore.RED + "File tin nhắn rỗng!")
        return

    token_count = len(tokens)
    msg_idx = 0
    token_idx = 0
    while True:
        msg = messages[msg_idx]
        token = tokens[token_idx]
        headers = headers_list[token_idx]
        url_typing = f"https://discord.com/api/v9/channels/{channel_id}/typing"
        url_send = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        try:
            requests.post(url_typing, headers=headers)
            await asyncio.sleep(1.5)
            r = requests.post(url_send, json={"content": msg}, headers=headers)
            if r.status_code in (200,201):
                status = Fore.GREEN + "Online ✅"
            else:
                status = Fore.RED + "Offline ❌"
        except Exception:
            status = Fore.RED + "Offline ❌"
        print(f"{Fore.YELLOW}Token {token_idx+1}{Fore.RESET} | {Fore.CYAN}ID nhóm: {channel_id}{Fore.RESET} | {status}")
        token_idx = (token_idx + 1) % token_count
        msg_idx = (msg_idx + 1) % len(messages)
        await asyncio.sleep(delay)

# ===== MAIN =====
async def main():
    banner()
    print(grad("==== MENU CHÍNH ====", (255,255,150),(255,100,255)))
    print(Fore.YELLOW + "1. Ngôn")
    print(Fore.YELLOW + "2. Nhây")

    while True:
        choice = input_label("Chọn chế độ (1 hoặc 2)")
        if choice in ["1","2"]: break
        print(Fore.RED + "Lựa chọn không hợp lệ. Nhập lại!")

    channel_id = input_label("ID Nhóm Discord")
    token_file = input_label("File chứa token")
    with open(token_file, "r", encoding="utf-8-sig") as f:
        tokens = [t.strip() for t in f if t.strip()]
    if not tokens:
        print(Fore.RED + "File token rỗng!")
        return

    delay_input = input_label("Delay giữa mỗi tin nhắn (giây)")
    try: delay = float(delay_input)
    except ValueError:
        print(Fore.RED + "Delay không hợp lệ, mặc định 1 giây")
        delay = 1.0

    tasks = []
    if choice == "1":
        message_file = input_label("File tin nhắn")
        tasks.append(spam_ngon_status(tokens, channel_id, message_file, delay))
    else:
        print(grad("==== NHÂY MENU ====", (255,255,150),(255,100,255)))
        print(Fore.YELLOW + "1. Nhây thường")
        print(Fore.YELLOW + "2. Nhây tag")

        while True:
            sub_choice = input_label("Chọn loại Nhây (1 hoặc 2)")
            if sub_choice in ["1","2"]: break
            print(Fore.RED + "Lựa chọn không hợp lệ. Nhập lại!")

        mention_ids = []
        name_mention = None
        if sub_choice == "2":
            while True:
                uid = input_label("Nhập user ID để tag (nhập done để kết thúc)")
                if uid.lower() == "done": break
                if uid.strip(): mention_ids.append(uid.strip())
            if input_label("Có muốn réo tên trong tin nhắn không? (y/n)").lower() == "y":
                name_mention = input_label("Nhập tên để réo")
        tasks.append(spam_nhay_status(tokens, channel_id, "nhay.txt", delay, mention_ids, name_mention))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\n⏹️ Tool đã dừng.")
