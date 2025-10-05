import requests
import time
import re
import os
from datetime import datetime
from colorama import Fore, Style, init
import threading
import random

# ================= INIT =================
init(autoreset=True)

# ================= EMOJIS =================
EMOJIS = [
"😂","😍","👍","🔥","💯","🥰","😎","😉","😜","🤩",
"😅","🤔","😇","😁","🙌","🥳","😱","😏","🤪","😋",
"🤗","😌","😛","😝","😤","🤤","😴","🤫","🤭","😐",
"😶","😕","🙃","🫣","😬","🥺","😪","🤮","🤧","🥵",
"🥶","😳","😵","😵‍💫","🫠","😷","🤒","🤕","🤑","🤠",
"😈","👿","👹","👺","💀","☠️","👻","👽","👾","🤖",
"🎃","😺","😸","😹","😻","😼","😽","🙀","😿","😾",
"💖","💗","💓","💞","💕","💘","💝","💟","❣️","💌",
"💤","💢","💥","💫","💦","💨","🕳️","💣","💬","👁️‍🗨️",
"🗨️","🗯️","💭","🛑","⚡","☀️","🌙","⭐","🌟","✨",
"⚜️","🌈","🔥","💧","🌊","🍀","🌹","🌺","🌸","🌼"
]

# ================= MESSENGER CLASS =================
class Messenger:
    FB_URLS = [
        "https://www.facebook.com",
        "https://mbasic.facebook.com",
        "https://m.facebook.com",
        "https://free.facebook.com",
        "https://touch.facebook.com"
    ]
    
    def __init__(self, cookie, counter_ref):
        self.cookie = cookie
        self.user_id = self.get_user_id()
        self.fb_dtsg = None
        self.counter_ref = counter_ref
        self.init_params()
    
    def get_user_id(self):
        m = re.search(r"c_user=(\d+)", self.cookie)
        if not m: 
            raise Exception("Cookie không hợp lệ")
        return m.group(1)
    
    def init_params(self):
        self.refresh_fb_dtsg(initial=True)
    
    def refresh_fb_dtsg(self, initial=False):
        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0'}
        try:
            for url in self.FB_URLS:
                r = requests.get(url, headers=headers, timeout=10)
                match = re.search(r'name="fb_dtsg" value="(.*?)"', r.text)
                if match:
                    self.fb_dtsg = match.group(1)
                    if not initial:
                        print(f"{Fore.CYAN}🔄 Refresh fb_dtsg thành công UID {self.user_id}{Style.RESET_ALL}")
                    return True
            if not initial:
                print(f"{Fore.RED}❌ Refresh fb_dtsg thất bại UID {self.user_id}{Style.RESET_ALL}")
            return False
        except:
            if not initial:
                print(f"{Fore.RED}❌ Refresh fb_dtsg lỗi UID {self.user_id}{Style.RESET_ALL}")
            return False
    
    def send_message(self, recipient_id, message, use_emoji=True):
        msg_to_send = message
        if use_emoji:
            emoji = random.choice(EMOJIS)
            msg_to_send += " " + emoji

        if not self.fb_dtsg:
            if not self.refresh_fb_dtsg():
                with self.counter_ref["lock"]:
                    self.counter_ref["fail"] += 1
                    sent = self.counter_ref["sent"]
                    fail = self.counter_ref["fail"]
                print(f"{Fore.RED}❌ Fail | Box: {recipient_id} | Tổng gửi: {sent} | Fail: {fail}{Style.RESET_ALL}")
                return False

        ts = int(time.time() * 1000)
        data = {
            'fb_dtsg': self.fb_dtsg,
            '__user': self.user_id,
            'body': msg_to_send,
            'action_type': 'ma-type:user-generated-message',
            'timestamp': ts,
            'offline_threading_id': str(ts),
            'message_id': str(ts),
            'thread_fbid': recipient_id,
            'source': 'source:chat:web',
            'client': 'mercury'
        }
        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            r = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers, timeout=15)
            with self.counter_ref["lock"]:
                if r.status_code == 200:
                    self.counter_ref["sent"] += 1
                else:
                    self.counter_ref["fail"] += 1
                sent = self.counter_ref["sent"]
                fail = self.counter_ref["fail"]

            if r.status_code == 200:
                print(f"{Fore.GREEN}✅ Thành công | Box: {recipient_id} | Tổng gửi: {sent} | Fail: {fail}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Thất bại | Box: {recipient_id} | Tổng gửi: {sent} | Fail: {fail} | HTTP:{r.status_code}{Style.RESET_ALL}")
                return False
        except Exception as exc:
            with self.counter_ref["lock"]:
                self.counter_ref["fail"] += 1
                sent = self.counter_ref["sent"]
                fail = self.counter_ref["fail"]
            print(f"{Fore.RED}❌ Exception | Box: {recipient_id} | Tổng gửi: {sent} | Fail: {fail} | Err: {exc}{Style.RESET_ALL}")
            return False

# ================= INTERACTIVE SETUP =================
def interactive_setup():
    print(f"{Fore.MAGENTA}=== Nhập Cookie (gõ 'done' để kết thúc) ==={Style.RESET_ALL}")
    cookies = []
    while True:
        c = input("Cookie: ").strip()
        if not c:
            continue
        if c.lower() == "done":
            break
        cookies.append(c)

    print(f"{Fore.MAGENTA}=== Nhập Recipient IDs (gõ 'done' để kết thúc) ==={Style.RESET_ALL}")
    recipient_ids = []
    while True:
        rid = input("Recipient ID: ").strip()
        if not rid:
            continue
        if rid.lower() == "done":
            break
        recipient_ids.append(rid)

    msg_file = input(f"{Fore.CYAN}Nhập tên file tin nhắn (ví dụ 'ngon.txt'): {Style.RESET_ALL}").strip()
    if not msg_file:
        msg_file = "ngon.txt"
    if not os.path.exists(msg_file):
        with open(msg_file, 'w', encoding='utf-8') as f:
            f.write("Nội dung mẫu - sửa theo ý bạn.")
        print(f"{Fore.YELLOW}Tạo file mẫu {msg_file}.{Style.RESET_ALL}")
    with open(msg_file, 'r', encoding='utf-8') as f:
        message = f.read().rstrip("\n")
        if not message:
            message = "Nội dung mẫu"

    while True:
        d = input(f"{Fore.CYAN}Delay giữa mỗi tin nhắn (giây) [mặc định 5]: {Style.RESET_ALL}").strip()
        if not d:
            delay = 5.0
            break
        try:
            delay = float(d)
            break
        except:
            print("Nhập số hợp lệ.")

    while True:
        use_emoji = input(f"{Fore.CYAN}Random icon (emoji) không? (yes/no) [mặc định yes]: {Style.RESET_ALL}").strip().lower()
        if not use_emoji or use_emoji == "yes":
            use_emoji = True
            break
        elif use_emoji == "no":
            use_emoji = False
            break
        else:
            print("Nhập yes hoặc no hợp lệ.")

    while True:
        rep = input(f"{Fore.CYAN}Số tin muốn refresh cookie : {Style.RESET_ALL}").strip()
        if not rep:
            repeat_per_recipient = 1
            break
        try:
            repeat_per_recipient = int(rep)
            break
        except:
            print("Nhập số nguyên hợp lệ.")

    return cookies, recipient_ids, message, delay, repeat_per_recipient, use_emoji

# ================= BANNER =================
def print_banner_live(total_cookies, messengers):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╔═══════════════════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║  ⚙️ 𝑵𝒐𝒗𝒂𝑿 Spam Tool | Zalo Group Premium               ║")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╠═══════════════════════════════════════════════════════╣")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 👑 Admin     : Tiến Đạt (Real)")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}📅 Khởi chạy : {now}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}⚡ Phiên bản : Premium V5.0")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}🌈 Developer : NovaX Team")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╚═══════════════════════════════════════════════════════╝\n")
    if messengers:
        print(f"{Fore.CYAN}Danh sách cookie hợp lệ:{Style.RESET_ALL}")
        for i, m in enumerate(messengers, 1):
            print(f"  {Fore.GREEN}Cookie{Fore.RED}{i}{Style.RESET_ALL} | UID: {Fore.CYAN}{m.user_id}{Style.RESET_ALL}")

# ================= MAIN =================
def main():
    # 1. Nhập tất cả thông tin trước
    cookies, recipient_ids, message, delay, repeat_per_recipient, use_emoji = interactive_setup()

    # 2. Clear màn hình sau khi nhập xong
    os.system('cls' if os.name == 'nt' else 'clear')

    # 3. Khởi tạo Messenger
    messengers = []
    for i, c in enumerate(cookies, 1):
        try:
            messengers.append(Messenger(c, global_counter))
        except Exception as e:
            print(f"{Fore.RED}Cookie {i} lỗi: {e}{Style.RESET_ALL}")

    if not messengers:
        print(f"{Fore.RED}Không có cookie hợp lệ!{Style.RESET_ALL}")
        return

    # 4. In banner
    print_banner_live(len(messengers), messengers)

    # 5. Bắt đầu gửi tin nhắn
    while True:
        for messenger in list(messengers):
            for recipient_id in recipient_ids:
                for _ in range(repeat_per_recipient):
                    messenger.send_message(recipient_id, message, use_emoji)
                    time.sleep(delay)
                messenger.refresh_fb_dtsg()

# ================= GLOBAL COUNTER =================
global_counter = {"sent": 0, "fail": 0, "lock": threading.Lock()}

if __name__=="__main__":
    main()