import os, time, threading, random, traceback
from datetime import datetime
from zlapi import ZaloAPI, ThreadType
from zlapi.models import Message, Mention
from colorama import Fore, Style, init

init(autoreset=True)

# =========================================
# CLEAR & BANNER
# =========================================
def clear(): os.system("cls" if os.name == "nt" else "clear")

def show_banner():
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╔═══════════════════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║  ⚙️ 𝑵𝒐𝒗𝒂𝑿 Spam Tool | Zalo Group Premium               ║")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╠═══════════════════════════════════════════════════════╣")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 👑 Admin     : Tiến Đạt (Real)")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}📅 Khởi chạy : {now}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}⚡ Phiên bản : Premium V5.0")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}🌈 Developer : NovaX Team")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╚═══════════════════════════════════════════════════════╝\n")

# =========================================
# BOT CLASS
# =========================================
class Bot(ZaloAPI):
    def __init__(self, imei, cookies):
        super().__init__('api_key', 'secret_key', imei, cookies)

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
            print(f"{Fore.RED}⚠️ Lỗi lấy nhóm: {e}")
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
            print(f"{Fore.RED}⚠️ Lỗi lấy thành viên: {e}")
            return []

# =========================================
# TAG / SPAM FUNCTION
# =========================================
def spam_nhay(bot, gid, uid, name, delay, stop_event):
    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            lines = [x.strip() for x in f if x.strip()]
    except:
        print(f"{Fore.RED}❌ Không tìm thấy file nhay.txt")
        return

    count = 0
    while not stop_event.is_set():
        for msg in lines:
            if stop_event.is_set(): return
            try:
                mention_text = f"@{name}"
                full = f"{mention_text} {msg}"
                mention = Mention(uid, offset=0, length=len(mention_text))
                bot.send(Message(text=full, mention=mention), gid, ThreadType.GROUP)
                count += 1
                print(f"{Fore.GREEN}[{count}] {full}")
            except Exception as e:
                print(f"{Fore.RED}⚠️ Lỗi: {e}")
            time.sleep(delay)

def spam_ngon(bot, gid, msg, delay, stop_event):
    count = 0
    while not stop_event.is_set():
        try:
            bot.send(Message(text=msg), gid, ThreadType.GROUP)
            count += 1
            print(f"{Fore.CYAN}[{count}] {msg}")
        except Exception as e:
            print(f"{Fore.RED}⚠️ Lỗi: {e}")
        time.sleep(delay)

def spam_ngon_tag(bot, gid, uid, name, msg, delay, stop_event):
    count = 0
    while not stop_event.is_set():
        try:
            mention_text = f"@{name}"
            full = f"{mention_text} {msg}"
            mention = Mention(uid, offset=0, length=len(mention_text))
            bot.send(Message(text=full, mention=mention), gid, ThreadType.GROUP)
            count += 1
            print(f"{Fore.MAGENTA}[{count}] {full}")
        except Exception as e:
            print(f"{Fore.RED}⚠️ Lỗi: {e}")
        time.sleep(delay)

# =========================================
# MAIN
# =========================================
def main():
    clear()
    show_banner()

    imei = input(f"{Fore.YELLOW}📱 Nhập IMEI: {Fore.WHITE}")
    cookie_str = input(f"{Fore.YELLOW}🍪 Nhập cookie (dict): {Fore.WHITE}")
    try:
        cookies = eval(cookie_str)
        if not isinstance(cookies, dict): raise
    except:
        print(f"{Fore.RED}❌ Cookie không hợp lệ!")
        return

    bot = Bot(imei, cookies)
    clear()
    show_banner()

    print(f"{Fore.CYAN}{Style.BRIGHT}🎯 Chọn chế độ:")
    print(f"{Fore.GREEN}1️⃣  Nhây (từ file nhay.txt)")
    print(f"{Fore.YELLOW}2️⃣  Ngôn (nhập thủ công)")
    print(f"{Fore.MAGENTA}3️⃣  Ngôn + Tag thật\n")

    mode = input(f"{Fore.WHITE}👉 Nhập số (1/2/3): ")

    clear()
    show_banner()
    groups = bot.fetch_groups()
    if not groups:
        print(f"{Fore.RED}❌ Không có nhóm nào!")
        return

    print(f"{Fore.CYAN}📋 Danh sách nhóm:")
    for i, g in enumerate(groups, 1):
        print(f"{Fore.GREEN}[{i}] {g['name']}")
    gidx = int(input(f"\n{Fore.YELLOW}👉 Chọn nhóm: {Fore.WHITE}")) - 1
    gid = groups[gidx]["id"]

    uid = name = None
    if mode in ["1", "3"]:
        clear()
        show_banner()
        members = bot.fetch_members(gid)
        print(f"{Fore.CYAN}👥 Thành viên nhóm:")
        for i, m in enumerate(members, 1):
            print(f"{Fore.GREEN}[{i}] {m['name']}")
        midx = int(input(f"\n{Fore.YELLOW}👉 Chọn người cần tag: {Fore.WHITE}")) - 1
        uid = members[midx]["id"]
        name = members[midx]["name"]

    delay = float(input(f"{Fore.YELLOW}⏱️ Delay (giây): {Fore.WHITE}") or 3)
    stop_event = threading.Event()

    if mode == "1":
        print(f"{Fore.MAGENTA}🚀 Bắt đầu spam nhây...")
        threading.Thread(target=spam_nhay, args=(bot, gid, uid, name, delay, stop_event), daemon=True).start()
    elif mode == "2":
        msg = input(f"{Fore.YELLOW}💬 Nhập nội dung tin nhắn: {Fore.WHITE}")
        print(f"{Fore.CYAN}🚀 Bắt đầu spam ngôn...")
        threading.Thread(target=spam_ngon, args=(bot, gid, msg, delay, stop_event), daemon=True).start()
    elif mode == "3":
        msg = input(f"{Fore.YELLOW}💬 Nhập nội dung tin nhắn: {Fore.WHITE}")
        print(f"{Fore.MAGENTA}🚀 Bắt đầu spam ngôn + tag thật...")
        threading.Thread(target=spam_ngon_tag, args=(bot, gid, uid, name, msg, delay, stop_event), daemon=True).start()
    else:
        print(f"{Fore.RED}⚠️ Chế độ không hợp lệ!")
        return

    try:
        hb = 0
        while True:
            time.sleep(300)
            hb += 1
            print(f"{Fore.YELLOW}💓 Tool vẫn hoạt động... ({hb} lần ping)")
    except KeyboardInterrupt:
        stop_event.set()
        print(f"{Fore.RED}⏹️ Dừng tool theo yêu cầu!")

# =========================================
if __name__ == "__main__":
    main()