#!/usr/bin/env python3
# tele_multi.py - Telegram Multi-Token Spam Tool (NovaX Version)
# - Persistent banner
# - Multi-token concurrent spam (threads)
# - Show top 20 most-recently-active chats (from getUpdates)
# - Choose chat by number (list stays until selection)
# - Optionally tag one member (choose by number)
# - Delay, random icon, saves tokens to tokens.json
# Use responsibly.

import os
import json
import requests
import time
import threading
import random
from datetime import datetime as _dt

# colorama (best-effort)
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except Exception:
    class _C:
        def __getattr__(self, name): return ''
    Fore = Style = _C()

TOKENS_FILE = 'tokens.json'
API_URL_TEMPLATE = "https://api.telegram.org/bot{token}/{method}"
STOP_EVENT = threading.Event()

# ---------------------------
# Banner & Clear
# ---------------------------
def _render_banner():
    now = _dt.now().strftime("%d-%m-%Y %H:%M:%S")
    lines = []
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}╔═══════════════════════════════════════════════════════╗")
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}║  ⚙️ 𝑵𝒐𝒗𝒂𝑿 Spam Tool | Telegram Multi-Token          ║")
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}╠═══════════════════════════════════════════════════════╣")
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 👑 Admin     : Tiến Đạt (Real)".ljust(54) + f"{Fore.MAGENTA}{Style.BRIGHT}║")
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}📅 Khởi chạy : {now}".ljust(54) + f"{Fore.MAGENTA}{Style.BRIGHT}║")
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}⚡ Phiên bản : Premium V5.0".ljust(54) + f"{Fore.MAGENTA}{Style.BRIGHT}║")
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}🌈 Developer : NovaX Team".ljust(54) + f"{Fore.MAGENTA}{Style.BRIGHT}║")
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}╚═══════════════════════════════════════════════════════╝")
    return lines

_BANNER_LINES = _render_banner()

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')
    global _BANNER_LINES
    _BANNER_LINES = _render_banner()
    for ln in _BANNER_LINES:
        print(ln)
    print()

def input_and_clear(prompt):
    """Collect input then clear screen (used for small inputs)."""
    res = input(prompt).strip()
    clear_screen()
    return res

# initial banner
clear_screen()

# ---------------------------
# Storage
# ---------------------------
def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return []
    try:
        with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_tokens(tokens):
    try:
        with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(Fore.RED + "Lỗi lưu tokens:", e)

# ---------------------------
# Telegram API helpers
# ---------------------------
def api_request(token, method, params=None, timeout=10):
    url = API_URL_TEMPLATE.format(token=token, method=method)
    try:
        r = requests.post(url, data=params or {}, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if not data.get('ok'):
            return None
        return data.get('result')
    except Exception:
        return None

def api_get(token, method, params=None, timeout=10):
    url = API_URL_TEMPLATE.format(token=token, method=method)
    try:
        r = requests.get(url, params=params or {}, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if not data.get('ok'):
            return None
        return data.get('result')
    except Exception:
        return None

def get_me(token):
    return api_request(token, 'getMe')

def get_updates(token, limit=200, offset=None):
    params = {'limit': limit}
    if offset:
        params['offset'] = offset
    return api_get(token, 'getUpdates', params=params)

# ---------------------------
# New: discover_recent_chats - returns list of (chat_id, title) sorted by recent activity
# ---------------------------
def discover_recent_chats(updates, limit=20):
    """
    From getUpdates list, return list of (chat_id, title) sorted by most recent activity.
    Return at most `limit` items.
    """
    if not updates:
        return []

    chats = {}  # chat_id -> {'title': str, 'ts': int}
    for upd in updates:
        # find the message-like object
        msg = None
        for key in ('message', 'edited_message', 'channel_post', 'my_chat_member', 'chat_member'):
            if key in upd and isinstance(upd[key], dict):
                msg = upd[key]
                break
        if not msg:
            continue

        # timestamp: prefer message['date'] (int)
        ts = None
        if isinstance(msg.get('date'), int):
            ts = msg.get('date')
        else:
            ts = upd.get('update_id', 0)

        chat = msg.get('chat')
        if not chat or 'id' not in chat:
            continue
        cid = chat['id']
        title = chat.get('title') or chat.get('first_name') or chat.get('username') or str(cid)

        existing = chats.get(cid)
        if not existing or ts > existing['ts']:
            chats[cid] = {'title': title, 'ts': ts}

    # sort by ts desc and take top limit
    sorted_items = sorted(chats.items(), key=lambda kv: kv[1]['ts'], reverse=True)
    top = sorted_items[:limit]
    return [(cid, meta['title']) for cid, meta in top]

def clear_updates(token, updates):
    """Mark updates as read by requesting offset = last_update_id+1"""
    if not updates:
        return
    try:
        last_id = max(u.get('update_id', 0) for u in updates)
        api_get(token, 'getUpdates', params={'offset': last_id + 1})
    except Exception:
        pass

def get_admins(token, chat_id):
    res = api_request(token, 'getChatAdministrators', {'chat_id': chat_id})
    out = []
    if res:
        for admin in res:
            user = admin.get('user')
            if user:
                uid = user.get('id')
                uname = user.get('username') or user.get('first_name') or str(uid)
                out.append({'id': uid, 'name': uname})
    return out

def get_all_members_from_updates(token, chat_id, bot_id):
    members = {}
    updates = get_updates(token, limit=1000) or []
    for upd in updates:
        for key in ('message', 'edited_message', 'channel_post'):
            msg = upd.get(key)
            if isinstance(msg, dict):
                chat = msg.get('chat')
                if chat and chat.get('id') == chat_id:
                    user = msg.get('from')
                    if user:
                        uid = user.get('id')
                        if uid != bot_id:
                            uname = user.get('username') or user.get('first_name') or str(uid)
                            members[uid] = uname
    # add admins
    admins = get_admins(token, chat_id)
    for a in admins:
        if a['id'] != bot_id:
            members[a['id']] = a['name']
    return members

def send_message(token, chat_id, text):
    return api_request(token, 'sendMessage', {'chat_id': chat_id, 'text': text})

# ---------------------------
# UI helpers
# ---------------------------
def simple_menu():
    print(Fore.YELLOW + "Menu:")
    print(Fore.GREEN + " 1." + Style.RESET_ALL + " Add token")
    print(Fore.GREEN + " 2." + Style.RESET_ALL + " List tokens")
    print(Fore.GREEN + " 3." + Style.RESET_ALL + " Delete token")
    print(Fore.GREEN + " 4." + Style.RESET_ALL + " Use multiple tokens")
    print(Fore.GREEN + " 5." + Style.RESET_ALL + " Quit\n")

def add_token(tokens):
    token = input_and_clear(Fore.CYAN + "Nhập Bot Token: ")
    if not token:
        return tokens
    info = get_me(token)
    if not info:
        print(Fore.RED + "Token không hợp lệ.")
        return tokens
    display = f"{info.get('username') or info.get('first_name')} (id:{info.get('id')})"
    tokens.append({'token': token, 'label': display})
    save_tokens(tokens)
    print(Fore.GREEN + "Done! Token thêm: " + display)
    time.sleep(1)
    clear_screen()
    return tokens

def list_tokens(tokens):
    if not tokens:
        print(Fore.YELLOW + "Chưa có token.")
        return
    print(Fore.CYAN + "Tokens saved:")
    for i, t in enumerate(tokens, start=1):
        print(f" [{i}] {t.get('label')}")
    print()

def delete_token(tokens):
    if not tokens:
        print(Fore.YELLOW + "Chưa có token để xóa.")
        return tokens
    list_tokens(tokens)
    sel = input_and_clear("Chọn số token để xóa (leave để hủy): ")
    if sel.lower() in ('', 'leave', 'exit'):
        return tokens
    try:
        idx = int(sel) - 1
        removed = tokens.pop(idx)
        save_tokens(tokens)
        print(Fore.GREEN + "Đã xóa: " + removed.get('label'))
        time.sleep(1)
        clear_screen()
    except Exception:
        print(Fore.RED + "Lựa chọn không hợp lệ.")
    return tokens

def select_tokens_interactive(tokens):
    if not tokens:
        print(Fore.YELLOW + "Chưa có token.")
        return []
    list_tokens(tokens)
    sel = input_and_clear("Chọn token(s) (số thứ tự, cách nhau bằng ','): ")
    if not sel:
        return []
    chosen = []
    for s in sel.split(','):
        s = s.strip()
        if not s:
            continue
        try:
            idx = int(s) - 1
            chosen.append(tokens[idx])
        except Exception:
            print(Fore.RED + f"Không hợp lệ: {s}")
    clear_screen()
    return chosen

# ---------------------------
# Build per-token configs (choose chat + optional tag)
# ---------------------------
def build_run_configs(chosen_tokens):
    configs = []
    for tkobj in chosen_tokens:
        token = tkobj['token']
        label = tkobj.get('label')
        me = get_me(token)
        bot_id = me.get('id') if me else None
        if not me:
            print(Fore.RED + f"Token {label} lỗi, bỏ qua.")
            continue

        print(Fore.CYAN + f"\nToken: {label}  —  Bot: {me.get('username') or me.get('first_name')}")
        # get many updates to have recent history
        updates = get_updates(token, limit=1000) or []
        # discover top 20 recent chats
        recent = discover_recent_chats(updates, limit=20)

        if not recent:
            manual = input_and_clear("Không tìm thấy box. Nhập chat id thủ công (leave để bỏ): ")
            if manual.lower() in ('', 'leave', 'exit'):
                continue
            try:
                chat_id = int(manual)
                chat_title = str(chat_id)
            except Exception:
                print(Fore.RED + "Chat id không hợp lệ. Bỏ token này.")
                continue
        else:
            # show list and choose by number, keep display until chosen
            items = recent  # list of (cid, title)
            print("Danh sách 20 box mới nhất:")
            for i, (cid, title) in enumerate(items, start=1):
                print(f" [{i}] {title}  —  id: {cid}")

            # loop until valid selection
            while True:
                sel = input("Chọn box bằng số thứ tự: ").strip()
                if sel.isdigit():
                    num = int(sel)
                    if 1 <= num <= len(items):
                        chat_id = items[num - 1][0]
                        chat_title = items[num - 1][1]
                        break
                print(Fore.RED + "Lựa chọn không hợp lệ, thử lại...")

            # clear only after successful selection
            clear_screen()

        # optional tag
        chosen_user = None
        tag_choice = input_and_clear("Bạn có muốn tag 1 người trong nhóm này không? (yes/no): ").lower()
        if tag_choice == 'yes':
            members = get_all_members_from_updates(token, chat_id, bot_id)
            if not members:
                admins = get_admins(token, chat_id)
                if admins:
                    members = {a['id']: a['name'] for a in admins}
            if not members:
                print(Fore.YELLOW + "Không lấy được danh sách thành viên/admin. Bỏ tag.")
            else:
                member_items = list(members.items())
                print("Danh sách thành viên (trừ bot):")
                for i, (uid, name) in enumerate(member_items, start=1):
                    print(f" [{i}] {name}  —  id: {uid}")

                # choose member by number, keep display until chosen
                while True:
                    sel_u = input("Chọn 1 người để @ (số thứ tự): ").strip()
                    if sel_u.isdigit():
                        idx = int(sel_u) - 1
                        if 0 <= idx < len(member_items):
                            chosen_user = member_items[idx]
                            print(Fore.GREEN + "Chọn tag: " + chosen_user[1])
                            break
                    print(Fore.RED + "Lựa chọn không hợp lệ, thử lại...")

                clear_screen()

        clear_updates(token, updates)
        configs.append({
            'token': token,
            'label': label,
            'bot_id': bot_id,
            'chat_id': chat_id,
            'chat_title': chat_title,
            'chosen_user': chosen_user
        })

        # small pause and clear to keep terminal tidy between tokens
        time.sleep(0.3)
        clear_screen()

    return configs

# ---------------------------
# Spam worker
# ---------------------------
def spam_worker_config(cfg, message, delay, use_random_icon):
    token = cfg['token']
    label = cfg.get('label')
    chat_id = cfg['chat_id']
    chosen_user = cfg.get('chosen_user')
    me = get_me(token) or {}
    botname = me.get('username') or me.get('first_name') or label
    emoji_pool = ['🔥','✨','✅','⚠️','💥','💡','👍','👀','🎯','🚀','📢','🔔','😄','🙂']
    count = 1
    print(Fore.CYAN + f"[{botname}] Start -> chat: {cfg.get('chat_title')}")
    while not STOP_EVENT.is_set():
        prefix = random.choice(emoji_pool) + ' ' if use_random_icon else ''
        if chosen_user:
            text = f"{prefix}@{chosen_user[1]} {message}"
        else:
            text = prefix + message
        res = send_message(token, chat_id, text)
        ts = _dt.now().strftime('%H:%M:%S')
        if res:
            print(Fore.GREEN + f"[{botname}][{count}] Sent at {ts}")
        else:
            print(Fore.RED + f"[{botname}][{count}] Failed at {ts}")
        count += 1
        time.sleep(delay)

# ---------------------------
# Main
# ---------------------------
def main():
    clear_screen()
    tokens = load_tokens()
    threads = []

    while True:
        simple_menu()
        choice = input("Chọn mục: ").strip()
        if choice == '1':
            tokens = add_token(tokens)
        elif choice == '2':
            clear_screen()
            list_tokens(tokens)
        elif choice == '3':
            tokens = delete_token(tokens)
        elif choice == '4':
            chosen = select_tokens_interactive(tokens)
            if not chosen:
                continue
            configs = build_run_configs(chosen)
            if not configs:
                print(Fore.YELLOW + "Không có config hợp lệ. Quay lại menu.")
                time.sleep(1)
                clear_screen()
                continue
            message = input_and_clear("Nhập nội dung tin nhắn: ") or "Hello từ Bot"
            try:
                delay_val = input_and_clear("Delay giữa các tin nhắn (giây, vd 2.5): ")
                delay = float(delay_val)
            except Exception:
                delay = 1.0
            use_random_icon = input_and_clear("Random icon trước tin nhắn? (y/N): ").lower() == 'y'
            clear_screen()
            print(Fore.MAGENTA + "Bắt đầu spam với các token đã chọn. Ctrl+C để dừng.\n")
            # start threads
            for cfg in configs:
                t = threading.Thread(target=spam_worker_config, args=(cfg, message, delay, use_random_icon))
                t.daemon = True
                t.start()
                threads.append(t)
            try:
                while True:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nĐang dừng tất cả threads...")
                STOP_EVENT.set()
                for t in threads:
                    t.join()
                STOP_EVENT.clear()
                threads = []
                print(Fore.GREEN + "Đã dừng xong.")
                time.sleep(1)
                clear_screen()
        elif choice == '5':
            print(Fore.CYAN + "Bye.")
            break
        else:
            print(Fore.RED + "Chọn 1-5")
            time.sleep(0.5)
            clear_screen()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã thoát.")