# tool_zalo_beauty_full.py
# -*- coding: utf-8 -*-
"""
Tool Zalo — full, đẹp, no-delete version
- Banner neon + gradient
- Menu 4 chế độ:
    1) Nhây (từ file nhay.txt)
    2) Ngôn (nhập 1 tin nhắn)
    3) Ngôn + Tag nhiều (chọn nhiều thành viên bằng số, cách nhau dấu phẩy)
    4) Nhây + Tag nhiều (nhay.txt + tag nhiều)
- Chọn nhóm -> clear -> hiển thị thành viên (gọn)
- Không có chức năng xóa tin nhắn của người khác / của bot
- Thực thi bằng thread, stop bằng Ctrl+C
"""

import os
import time
import threading
import random
import shutil
import socket
from datetime import datetime
from zlapi import ZaloAPI, ThreadType
from zlapi.models import Message, Mention

# ===================== UTILS & COLORS =====================
def rgb(r, g, b, t):
    return f"\033[38;2;{r};{g};{b}m{t}\033[0m"

def grad(text, c1, c2):
    out = ""
    n = max(1, len(text) - 1)
    for i, ch in enumerate(text):
        t = i / n
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        out += rgb(r, g, b, ch)
    return out

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def width():
    try:
        return shutil.get_terminal_size().columns - 4
    except:
        return 80

PALETTES = [
    ((255, 0, 255), (0, 255, 255)),
    ((255, 150, 50), (255, 80, 200)),
    ((120, 190, 255), (50, 255, 200)),
    ((180, 130, 255), (255, 100, 200)),
    ((80, 255, 160), (255, 100, 255))
]

def theme():
    return random.choice(PALETTES)

def neon_border(w, c1, c2):
    return grad("—" * w, c1, c2)

def neon_box(title="", lines=None, c1=(255,0,255), c2=(0,255,255)):
    w = width()
    b = neon_border(w, c1, c2)
    print(f"+{b}+")
    if title:
        t = grad(f" {title} ", c1, c2)
        print(f"|{t.center(w)}")
        print(f"+{b}+")
    for line in lines or []:
        inner = grad(line.strip(), (240,240,255), (200,255,255))
        print(f"| {inner:<{w-2}}")
    print(f"+{b}+")

# ===================== BANNER / LOGO =====================
def logo(c1, c2):
    art = [
        "███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ██╗  ██╗",
        "████╗  ██║██╔═══██╗██║   ██║██╔══██╗╚██╗██╔╝",
        "██╔██╗ ██║██║   ██║██║   ██║███████║ ╚███╔╝ ",
        "██║╚██╗██║██║   ██║██║   ██║██╔══██║ ██╔██╗ ",
        "██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██╔╝ ██╗",
        "╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝",
    ]
    for l in art:
        print(grad(l, c1, c2))
    print(grad("⚡ NOVAX SPAM TOOL | ZALO PREMIUM ⚡", (255,255,120), c2))

def banner_live(bot=None, c1=(255,0,255), c2=(0,255,255)):
    clear()
    logo(c1, c2)
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = "Không xác định"
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    neon_box("THÔNG TIN TOOL ZALO", [
        "👑 Admin     : Tiến Đạt (Real)",
        f"📅 Khởi chạy : {now}",
        "⚡ Phiên bản : Premium V5.0",
        "🌈 Developer : NovaX Team",
        f"🌐 Thiết bị  : {ip}"
    ], c1, c2)

# ===================== BOT WRAPPER =====================
class Bot(ZaloAPI):
    def __init__(self, imei, cookies):
        super().__init__('api_key', 'secret_key', imei, cookies)
        self.imei = imei
        self.cookies = cookies

    def fetch_groups(self):
        try:
            groups = self.fetchAllGroups()
            result = []
            for gid in groups.gridVerMap:
                ginfo = self.fetchGroupInfo(gid)
                name = ginfo.gridInfoMap[gid]["name"]
                result.append({"id": gid, "name": name})
            return result
        except Exception as e:
            print(grad(f"⚠️ Lỗi lấy nhóm: {e}", (255,80,80), (255,150,150)))
            return []

    def fetch_members(self, gid):
        try:
            info = self.fetchGroupInfo(gid)
            members = []
            for mem in info.gridInfoMap[gid]["memVerList"]:
                uid = mem.split("_")[0]
                try:
                    user_info = self.fetchUserInfo(uid)
                    name = user_info.changed_profiles[uid]["displayName"]
                    members.append({"id": uid, "name": name})
                except:
                    members.append({"id": uid, "name": f"[Ẩn danh {uid}]"})
            return members
        except Exception as e:
            print(grad(f"⚠️ Lỗi lấy thành viên: {e}", (255,80,80), (255,150,150)))
            return []

# ===================== SPAM ROUTINES =====================
def spam_nhay(bot, gid, delay, stop_event):
    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            lines = [x.strip() for x in f if x.strip()]
    except:
        print(grad("❌ Không tìm thấy file nhay.txt", (255,80,80), (255,150,150)))
        return
    count = 0
    while not stop_event.is_set():
        for msg in lines:
            if stop_event.is_set(): return
            try:
                bot.send(Message(text=msg), gid, ThreadType.GROUP)
                count += 1
                print(grad(f"[{count}] {msg}", (180,255,180), (100,255,255)))
            except Exception as e:
                print(grad(f"⚠️ Lỗi: {e}", (255,80,80), (255,150,150)))
            time.sleep(delay)

def spam_ngon(bot, gid, msg, delay, stop_event):
    count = 0
    while not stop_event.is_set():
        try:
            bot.send(Message(text=msg), gid, ThreadType.GROUP)
            count += 1
            print(grad(f"[{count}] {msg}", (180,255,180), (100,255,255)))
        except Exception as e:
            print(grad(f"⚠️ Lỗi: {e}", (255,80,80), (255,150,150)))
        time.sleep(delay)

def spam_ngon_tag_multi(bot, gid, selected_members, msg, delay, stop_event):
    """
    Gửi tag nhiều người: gửi 1 tin/mention cho từng member trong selected_members.
    (Vì đa số API không hỗ trợ mention nhiều cùng lúc; gửi từng message là ổn định.)
    """
    count = 0
    while not stop_event.is_set():
        for m in selected_members:
            if stop_event.is_set(): return
            try:
                mention_text = f"@{m['name']}"
                full = f"{mention_text} {msg}"
                bot.send(Message(text=full, mention=Mention(m['id'], offset=0, length=len(mention_text))), gid, ThreadType.GROUP)
                count += 1
                print(grad(f"[{count}] {full}", (180,255,180), (100,255,255)))
            except Exception as e:
                print(grad(f"⚠️ Lỗi gửi đến {m.get('name','?')}: {e}", (255,80,80), (255,150,150)))
            time.sleep(delay)

def spam_nhay_tag_multi(bot, gid, selected_members, delay, stop_event):
    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            lines = [x.strip() for x in f if x.strip()]
    except:
        print(grad("❌ Không tìm thấy file nhay.txt", (255,80,80), (255,150,150)))
        return
    count = 0
    while not stop_event.is_set():
        for msg in lines:
            if stop_event.is_set(): return
            for m in selected_members:
                if stop_event.is_set(): return
                try:
                    mention_text = f"@{m['name']}"
                    full = f"{mention_text} {msg}"
                    bot.send(Message(text=full, mention=Mention(m['id'], offset=0, length=len(mention_text))), gid, ThreadType.GROUP)
                    count += 1
                    print(grad(f"[{count}] {full}", (180,255,180), (100,255,255)))
                except Exception as e:
                    print(grad(f"⚠️ Lỗi gửi đến {m.get('name','?')}: {e}", (255,80,80), (255,150,150)))
                time.sleep(delay)

# ===================== MENU / HELPERS =====================
def menu(c1, c2):
    print(grad("🎯 Chọn chức năng:", c1, c2))
    print(grad("1️⃣  Nhây ", c1, c2))
    print(grad("2️⃣  Ngôn ", c1, c2))
    print(grad("3️⃣  Ngôn Tag", c1, c2))
    print(grad("4️⃣  Nhây Tag", c1, c2))
    print(grad("0️⃣  Thoát", c1, c2))

def choose_group(bot, c1, c2):
    groups = bot.fetch_groups()
    if not groups:
        print(grad("❌ Không có nhóm nào!", (255,80,80), (255,150,150)))
        return None
    lines = [f"{i+1}. {g['name']}" for i, g in enumerate(groups)]
    neon_box("📋 Danh sách nhóm", lines, c1, c2)
    try:
        gidx = int(input(grad("👉 Chọn nhóm (số): ", c1, c2)).strip()) - 1
        return groups[gidx]["id"]
    except Exception:
        print(grad("❌ Lựa chọn nhóm không hợp lệ.", (255,80,80), (255,150,150)))
        return None

def choose_members_multi(bot, gid, c1, c2):
    members = bot.fetch_members(gid)
    if not members:
        print(grad("❌ Không lấy được thành viên!", (255,80,80), (255,150,150)))
        return None
    # Clear screen before showing members (neat)
    clear()
    neon_lines = [f"{i+1}. {m['name']}" for i, m in enumerate(members)]
    neon_box("👥 Thành viên nhóm (gõ số cách nhau bằng dấu phẩy, vd: 1,3,5)", neon_lines, c1, c2)
    choice = input(grad("👉 Nhập các số: ", c1, c2)).strip()
    parts = [p.strip() for p in choice.split(",") if p.strip()]
    sel = []
    for p in parts:
        try:
            idx = int(p) - 1
            if 0 <= idx < len(members):
                sel.append(members[idx])
        except:
            continue
    if not sel:
        print(grad("❌ Không có thành viên hợp lệ được chọn.", (255,80,80), (255,150,150)))
        return None
    return sel

# ===================== MAIN =====================
def main():
    c1, c2 = theme()
    clear()
    banner_live(None, c1, c2)

    imei = input(grad("📱 Nhập IMEI: ", c1, c2)).strip()
    cookie_str = input(grad("🍪 Nhập cookie dict (ví dụ {'token':'...'}): ", c1, c2)).strip()
    try:
        cookies = eval(cookie_str)
        if not isinstance(cookies, dict):
            raise ValueError("cookie phải là dict")
    except Exception:
        print(grad("❌ Cookie không hợp lệ! Dừng.", (255,80,80), (255,150,150)))
        return

    bot = Bot(imei, cookies)

    while True:
        clear()
        banner_live(bot, c1, c2)
        menu(c1, c2)
        choice = input(grad("👉 Nhập lựa chọn: ", c1, c2)).strip()
        if choice == "0":
            print(grad("⏹️ Thoát chương trình.", (255,80,80), (255,150,150)))
            break

        # Choices 1..4 require group selection
        gid = choose_group(bot, c1, c2)
        if not gid:
            input(grad("Nhấn Enter quay lại menu...", c1, c2))
            continue

        try:
            print(grad("⏱️ Delay giữa mỗi tin nhắn (giây, mặc định 2)",c1, c2))
            delay = float(input(grad("⏱️ Tốc độ : ", c1, c2)).strip() or 2)
        except:
            delay = 2.0

        stop_event = threading.Event()
        threads = []

        if choice == "1":
            # Nhây (file nhay.txt) - no tag
            t = threading.Thread(target=spam_nhay, args=(bot, gid, delay, stop_event), daemon=True)
            t.start()
            threads.append(t)

        elif choice == "2":
            # Ngôn (manual single message) - no tag
            print(grad("Nhập nội dung tin nhắn cần gửi ",c1, c2))
            msg = input(grad("Nhập Tin Nhắn :", c1, c2)).strip()
            if not msg:
                print(grad("❌ Tin nhắn trống. Hủy.", (255,80,80), (255,150,150)))
                input(grad("Nhấn Enter quay lại menu...", c1, c2))
                continue
            t = threading.Thread(target=spam_ngon, args=(bot, gid, msg, delay, stop_event), daemon=True)
            t.start()
            threads.append(t)

        elif choice == "3":
            # Ngôn + tag many
            selected = choose_members_multi(bot, gid, c1, c2)
            if not selected:
                input(grad("Nhấn Enter quay lại menu...", c1, c2))
                continue
            print(grad("Nhập nội dung tin nhắn cần gửi ",c1, c2))
            msg = input(grad("Nhập Tin Nhắn :", c1, c2)).strip()
            if not msg:
                print(grad("❌ Tin nhắn trống. Hủy.", (255,80,80), (255,150,150)))
                input(grad("Nhấn Enter quay lại menu...", c1, c2))
                continue
            t = threading.Thread(target=spam_ngon_tag_multi, args=(bot, gid, selected, msg, delay, stop_event), daemon=True)
            t.start()
            threads.append(t)

        elif choice == "4":
            # Nhây + tag many
            selected = choose_members_multi(bot, gid, c1, c2)
            if not selected:
                input(grad("Nhấn Enter quay lại menu...", c1, c2))
                continue
            t = threading.Thread(target=spam_nhay_tag_multi, args=(bot, gid, selected, delay, stop_event), daemon=True)
            t.start()
            threads.append(t)

        else:
            print(grad("⚠️ Lựa chọn không hợp lệ!", (255,80,80), (255,150,150)))
            time.sleep(1)
            continue

        print(grad("\n🚀 Bắt đầu spam. Nhấn Ctrl+C để dừng.", c1, c2))
        try:
            hb = 0
            while True:
                time.sleep(300)
                hb += 1
                print(grad(f"💓 Tool vẫn hoạt động... ({hb} lần ping)", c1, c2))
        except KeyboardInterrupt:
            stop_event.set()
            print(grad("⏹️ Dừng theo yêu cầu. Trở về menu.", (255,80,80), (255,150,150)))
            time.sleep(1)
            continue

if __name__ == "__main__":
    main()
