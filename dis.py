# -*- coding: utf-8 -*-
import os
import asyncio
import requests
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# ===== BANNER =====
def print_banner():
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╔═══════════════════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║  ⚙️  𝑵𝒐𝒗𝒂𝑿 Spam Tool | Zalo Group Premium         ║")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╠═══════════════════════════════════════════════════════╣")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 👑 Admin     : Tiến Đạt (Real)")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 📅 Khởi chạy : {now}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} ⚡ Phiên bản : Premium V5.0")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 🌈 Developer : NovaX Team")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╚═══════════════════════════════════════════════════════╝\n")

# ===== HÀM DÙNG CHUNG =====
def clean_line_for_hash(line):
    stripped = line.lstrip('#').lstrip()
    return "# > " + stripped if stripped else ""

def input_label(label):
    """
    Nhập giá trị 1 lần:
    - Trước khi nhập: hiển thị label
    - Dòng nhập: ➤ Nhập:
    - Sau khi nhập: xoá dòng ➤ Nhập và in > giá trị
    """
    print(f"{Fore.YELLOW}{label}:{Style.RESET_ALL}")
    value = input(f"➤ Nhập: {Fore.CYAN}").strip()
    # Xoá dòng input và in > giá trị
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

        # HIỂN THỊ MÀU
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
    os.system('cls' if os.name=='nt' else 'clear')
    print_banner()

    # ===== MENU CHÍNH =====
    print(Fore.MAGENTA + Style.BRIGHT + "==== MENU CHÍNH ====")
    print(Fore.YELLOW + "1. Ngôn (spam file tự chọn)")
    print(Fore.YELLOW + "2. Nhây (spam nhay.txt)")

    while True:
        choice = input_label("Chọn chế độ (1 hoặc 2)")
        if choice in ["1","2"]:
            break
        print(Fore.RED + "Lựa chọn không hợp lệ. Nhập lại!")

    # Nhập ID kênh
    channel_id = input_label("ID Nhóm")

    # Nhập file token
    token_file = input_label("File chứa token")
    with open(token_file, "r", encoding="utf-8-sig") as f:
        tokens = [t.strip() for t in f if t.strip()]
    if not tokens:
        print(Fore.RED + "File token rỗng!")
        return

    # Nhập delay
    delay_input = input_label("Delay giữa mỗi tin nhắn (giây)")
    try:
        delay = float(delay_input)
    except ValueError:
        print(Fore.RED + "Delay không hợp lệ, mặc định 1 giây")
        delay = 1.0

    tasks = []

    if choice == "1":  # NGÔN
        message_file = input_label("File tin nhắn")
        tasks.append(spam_ngon_status(tokens, channel_id, message_file, delay))

    elif choice == "2":  # NHÂY
        print(Fore.MAGENTA + Style.BRIGHT + "\n==== NHÂY MENU ====")
        print(Fore.YELLOW + "1. Nhây thường")
        print(Fore.YELLOW + "2. Nhây tag")

        while True:
            sub_choice = input_label("Chọn loại Nhây (1 hoặc 2)")
            if sub_choice in ["1","2"]:
                break
            print(Fore.RED + "Lựa chọn không hợp lệ. Nhập lại!")

        mention_ids = []
        name_mention = None
        if sub_choice == "2":
            while True:
                uid = input_label("Nhập user ID để tag (nhập done để kết thúc)")
                if uid.lower() == "done":
                    break
                if uid.strip():
                    mention_ids.append(uid.strip())
            if input_label("Có muốn réo tên trong tin nhắn không? (y/n)").lower() == "y":
                name_mention = input_label("Nhập tên để réo")

        tasks.append(spam_nhay_status(tokens, channel_id, "nhay.txt", delay, mention_ids, name_mention))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\nTool đã dừng.")