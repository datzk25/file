import requests
import time
import re
import os
from datetime import datetime
from colorama import Fore, Style, init
import threading
import random
import traceback

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

# ================= GLOBAL COUNTER =================
global_counter = {"sent": 0, "fail": 0, "lock": threading.Lock()}

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
        except Exception as exc:
            if not initial:
                print(f"{Fore.RED}❌ Refresh fb_dtsg lỗi UID {self.user_id} | Err: {exc}{Style.RESET_ALL}")
                traceback.print_exc()
            return False
    
    def send_message(self, recipient_id, message, use_emoji=True):
        msg_to_send = message
        if use_emoji:
            msg_to_send += " " + random.choice(EMOJIS)

        if not self.fb_dtsg:
            if not self.refresh_fb_dtsg():
                with self.counter_ref["lock"]:
                    self.counter_ref["fail"] += 1
                print(f"{Fore.RED}❌ Cookie UID {self.user_id} die, bỏ qua{Style.RESET_ALL}")
                return False, False  # Fail, cookie die

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
                if r.status_code == 200 and "error" not in r.text.lower():
                    self.counter_ref["sent"] += 1
                else:
                    self.counter_ref["fail"] += 1
                sent = self.counter_ref["sent"]
                fail = self.counter_ref["fail"]

            if r.status_code == 200 and "error" not in r.text.lower():
                print(f"{Fore.GREEN}✅ Thành công | Box: {recipient_id} | Tổng gửi: {sent} | Fail: {fail}{Style.RESET_ALL}")
                return True, True
            else:
                print(f"{Fore.RED}❌ Thất bại | Box: {recipient_id} | Tổng gửi: {sent} | Fail: {fail} | HTTP:{r.status_code}{Style.RESET_ALL}")
                return False, True

        except Exception as exc:
            with self.counter_ref["lock"]:
                self.counter_ref["fail"] += 1
                sent = self.counter_ref["sent"]
                fail = self.counter_ref["fail"]
            print(f"{Fore.RED}❌ Exception | Box: {recipient_id} | Tổng gửi: {sent} | Fail: {fail} | Err: {exc}{Style.RESET_ALL}")
            return False, False

# ================= COUNTDOWN =================
def countdown(delay):
    for remaining in range(int(delay), 0, -1):
        print(f"\r {Fore.MAGENTA}⏱ Thời Gian Chờ :{Style.RESET_ALL} {remaining}s ", end="", flush=True)
        time.sleep(1)
    print("\r", end="")

# ================= BANNER =================
def print_banner_live(total_cookies, messengers, show_list=True):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╔═══════════════════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║  ⚙️ 𝑵𝒐𝒗𝒂𝑿 Spam Tool | Mess Group Premium               ║")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╠═══════════════════════════════════════════════════════╣")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 👑 Admin     : Tiến Đạt (Real)")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}📅 Khởi chạy : {now}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}⚡ Phiên bản : Premium V5.0")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}🌈 Developer : NovaX Team")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╚═══════════════════════════════════════════════════════╝")
    
    if show_list and messengers:
        print(f"{Fore.CYAN}Danh sách cookie hợp lệ:{Style.RESET_ALL}")
        for i, m in enumerate(messengers, 1):
            print(f"  {Fore.GREEN}Cookie {Fore.RED}{i}{Style.RESET_ALL} | UID: {Fore.CYAN}{m.user_id}{Style.RESET_ALL}")

# ================= INTERACTIVE SETUP =================
def interactive_setup():
    print(f"{Fore.MAGENTA}Thêm Cookie (nhập 'done' để kết thúc){Style.RESET_ALL}")
    cookies = []
    while True:
        c = input(">").strip()
        if not c:
            continue
        if c.lower() == "done":
            break
        cookies.append(c)

    print(f"{Fore.MAGENTA}Thêm Idbox (nhập 'done' để kết thúc){Style.RESET_ALL}")
    recipient_ids = []
    while True:
        rid = input(">").strip()
        if not rid:
            continue
        if rid.lower() == "done":
            break
        recipient_ids.append(rid)

    print(f"{Fore.MAGENTA}File Ngôn (Enter để dùng ngon.txt){Style.RESET_ALL}")
    msg_file = input(f"{Fore.MAGENTA}>{Style.RESET_ALL}").strip()
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

    # Delay
    while True:
        print(f"{Fore.MAGENTA}Nhập Delay{Style.RESET_ALL}")
        d = input(f"{Fore.MAGENTA}>{Style.RESET_ALL}").strip()
        if not d:
            delay = 5.0
            break
        try:
            delay = float(d)
            break
        except:
            print("Nhập số hợp lệ.")

    # Random emoji
    while True:
        print(f"{Fore.MAGENTA}Random Icon (Yes/no){Style.RESET_ALL}")
        use_emoji_input = input(f"{Fore.MAGENTA}>{Style.RESET_ALL}").strip().lower()
        if not use_emoji_input or use_emoji_input == "yes":
            use_emoji = True
            break
        elif use_emoji_input == "no":
            use_emoji = False
            break
        else:
            print("Nhập yes hoặc no hợp lệ.")

    # Repeat per recipient
    while True:
        print(f"{Fore.MAGENTA}Số Tin Reload Cookie{Style.RESET_ALL}")
        rep = input(f"{Fore.MAGENTA}>{Style.RESET_ALL}").strip()
        if not rep:
            repeat_per_recipient = 1
            break
        try:
            repeat_per_recipient = int(rep)
            break
        except:
            print("Nhập số nguyên hợp lệ.")

    return cookies, recipient_ids, message, delay, repeat_per_recipient, use_emoji

# ================= MAIN =================
def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    # Banner trước khi nhập cookie
    print_banner_live(total_cookies=0, messengers=[], show_list=False)

    # Nhập thông tin
    cookies, recipient_ids, message, delay, repeat_per_recipient, use_emoji = interactive_setup()

    # Clear màn hình sau khi nhập xong
    os.system('cls' if os.name == 'nt' else 'clear')

    # Tạo messenger hợp lệ
    messengers = []
    for i, c in enumerate(cookies, 1):
        try:
            messengers.append(Messenger(c, global_counter))
        except Exception as e:
            print(f"{Fore.RED}Cookie {i} lỗi: {e}{Style.RESET_ALL}")

    if not messengers:
        print(f"{Fore.RED}Không có cookie hợp lệ!{Style.RESET_ALL}")
        return

    # Banner với danh sách cookie hợp lệ
    print_banner_live(len(messengers), messengers, show_list=True)

    # Vòng gửi tin nhắn liên tục
    while True:
        for messenger in list(messengers):
            for recipient_id in recipient_ids:
                for _ in range(repeat_per_recipient):
                    success, alive = messenger.send_message(recipient_id, message, use_emoji)
                    countdown(delay)  # Thời gian chờ đếm ngược đẹp
                    if not alive:
                        print(f"{Fore.RED}❌ Cookie UID {messenger.user_id} die, bỏ qua{Style.RESET_ALL}")
                        break
                messenger.refresh_fb_dtsg()

if __name__=="__main__":
    main()