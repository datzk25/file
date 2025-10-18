# tool_messenger.py
# -*- coding: utf-8 -*-
import requests, time, re, os, threading, random, shutil, socket
from datetime import datetime

# ================ CONFIG / UTIL ================
def rgb(r,g,b,t):
    return f"\033[38;2;{r};{g};{b}m{t}\033[0m"

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
def theme(): return random.choice(PALETTES)

def neon_border(w,c1,c2): return grad("—"*w,c1,c2)

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
        print(f"| {inner.ljust(w)} ")
    print(f"+{b}+")

def logo(c1,c2):
    art=[
        "███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ██╗  ██╗",
        "████╗  ██║██╔═══██╗██║   ██║██╔══██╗╚██╗██╔╝",
        "██╔██╗ ██║██║   ██║██║   ██║███████║ ╚███╔╝ ",
        "██║╚██╗██║██║   ██║██║   ██║██╔══██║ ██╔██╗ ",
        "██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██╔╝ ██╗",
        "╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝",
    ]
    for l in art: print(grad(l,c1,c2))
    print(grad("⚡ NOVAX SPAM TOOL | MESSENGER PREMIUM ⚡",(255,255,120),c2))

# ================ GLOBAL COUNTER ================
global_counter = {"sent":0,"fail":0,"lock":threading.Lock()}

# ================ EMOJIS ================
EMOJIS = [
"😂","😍","👍","🔥","💯","🥰","😎","😉","😜","🤩",
"😅","🤔","😇","😁","🙌","🥳","😱","😏","🤪","😋",
"🤗","😌","😛","😝","😤","🤤","😴","🤫","🤭","😐",
"😶","😕","🙃","🫣","😬","🥺","😪","🤮","🤧","🥵"
]

# ================ MESSENGER CLASS ================
class Messenger:
    FB_URLS = [
        "https://www.facebook.com",
        "https://mbasic.facebook.com",
        "https://m.facebook.com",
        "https://free.facebook.com",
        "https://touch.facebook.com"
    ]
    def __init__(self, cookie, counter_ref):
        self.cookie = cookie.strip()
        self.user_id = self.get_user_id()
        self.fb_dtsg = None
        self.counter_ref = counter_ref
        self.init_params()

    def get_user_id(self):
        m = re.search(r"c_user=(\d+)", self.cookie)
        if not m:
            raise Exception("Cookie không hợp lệ (không tìm thấy c_user)")
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
                        print(grad(f"🔄 Refresh fb_dtsg thành công UID {self.user_id}", (120,255,200),(0,200,255)))
                    return True
            if not initial:
                print(grad(f"❌ Refresh fb_dtsg thất bại UID {self.user_id}", (255,80,80),(255,150,150)))
            return False
        except Exception as e:
            if not initial:
                print(grad(f"❌ Refresh fb_dtsg lỗi UID {self.user_id} | Err: {e}", (255,80,80),(255,150,150)))
            return False

    def send_message(self, recipient_id, message, use_emoji=True):
        msg_to_send = message + (" " + random.choice(EMOJIS) if use_emoji else "")
        if not self.fb_dtsg:
            if not self.refresh_fb_dtsg():
                with self.counter_ref["lock"]:
                    self.counter_ref["fail"] += 1
                sent = self.counter_ref["sent"]; fail = self.counter_ref["fail"]
                print(grad(f"❌ Fail | Box: {recipient_id} | Sent: {sent} | Fail: {fail}", (255,80,80),(255,150,150)))
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
            sent = self.counter_ref["sent"]; fail = self.counter_ref["fail"]
            if r.status_code == 200:
                print(grad(f"✅ Thành công | Box: {recipient_id} | Sent: {sent} | Fail: {fail}", (100,255,180),(50,200,255)))
                return True
            else:
                print(grad(f"❌ Thất bại | Box: {recipient_id} | Sent: {sent} | Fail: {fail} | HTTP:{r.status_code}", (255,100,100),(255,180,180)))
                return False
        except Exception as exc:
            with self.counter_ref["lock"]:
                self.counter_ref["fail"] += 1
            sent = self.counter_ref["sent"]; fail = self.counter_ref["fail"]
            print(grad(f"❌ Exception | Box: {recipient_id} | Sent: {sent} | Fail: {fail} | Err: {exc}", (255,80,80),(255,150,150)))
            return False

# ================ BANNER / UI ================
def banner_live(messengers=None,c1=(255,0,255),c2=(0,255,255)):
    clear()
    logo(c1,c2)
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
    except:
        try: ip = socket.gethostbyname(socket.gethostname())
        except: ip = "Không xác định"
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    neon_box("THÔNG TIN TOOL MESSENGER", [
        "👑 Admin     : Tiến Đạt (Real)",
        f"📅 Khởi chạy : {now}",
        "⚡ Phiên bản : Premium V5.0",
        "🌈 Developer : NovaX Team",
        f"🌐 IP Thiết bị : {ip}"
    ], c1, c2)
    if messengers:
        print(grad("\nDanh sách cookie hợp lệ:", c1, c2))
        for i,m in enumerate(messengers,1):
            print(grad(f"  Cookie{i} | UID: {m.user_id}", (180,255,180),(100,255,255)))
    print()

# ================ INTERACTIVE SETUP ================
def interactive_setup(c1,c2):
    banner_live(None,c1,c2)

    # --- FILE COOKIE ---
    print(grad("Nhập File Cookie: ( ví dụ yes/no )",(255,80,80),(255,150,150)))
    use_file="" 
    while use_file.lower() not in ("yes","no","y","n"):
        use_file = input(grad("Nhập : ",c1,c2)).strip().lower()
    cookies=[]
    if use_file in ("yes","y"):
        print(grad("Nhập File Cookie",(255,80,80),(255,150,150)))
        fname=input(grad("Nhập : ",c1,c2)).strip()
        if not fname:
            print(grad("Tên file không hợp lệ.",(255,80,80),(255,150,150)))
            return None,None,None,None,None,None
        if not os.path.exists(fname):
            with open(fname,"w",encoding="utf-8") as f:
                f.write("# Mỗi dòng 1 cookie (bỏ # nếu là cookie thật)\n# ví dụ: c_user=12345; xs=...; fr=...\n")
            print(grad(f"File '{fname}' không tồn tại. Đã tạo file mẫu.",(255,180,80),(255,220,180)))
            input(grad("Nhấn Enter để thoát...",c1,c2))
            return None,None,None,None,None,None
        with open(fname,"r",encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith("#"): continue
                cookies.append(line)
        if not cookies:
            print(grad(f"File '{fname}' rỗng hoặc chỉ comment.",(255,80,80),(255,150,150)))
            input(grad("Nhấn Enter để thoát...",c1,c2))
            return None,None,None,None,None,None
        neon_box("DANH SÁCH COOKIE ĐÃ ĐỌC", [f"{i+1}. {c[:50]}..." for i,c in enumerate(cookies)], c1,c2)
    else:
        neon_box("Nhập cookie ( done để kết thúc)",["Nhập từng cookie 1 dòng"], c1,c2)
        while True:
            c = input(grad("Cookie: ",c1,c2)).strip()
            if not c: continue
            if c.lower()=="done": break
            cookies.append(c)

    # --- RECIPIENT ---
    neon_box("Nhập Idbox Treo", ["(Gõ 'done' để kết thúc)"], c1, c2)
    recipient_ids = []
    while True:
        rid = input(grad("Nhập : ", c1, c2)).strip()
        if not rid: continue
        if rid.lower() == "done": break
        recipient_ids.append(rid)

    # --- MESSAGE ---
    print(grad("Nhập file ngôn",(255,80,80),(255,150,150)))
    msg_file = input(grad("Nhập : ", c1, c2)).strip() or "ngon.txt"
    if not os.path.exists(msg_file):
        with open(msg_file, 'w', encoding='utf-8') as f:
            f.write("Ank Là NovaX.")
        print(grad(f"Đã tạo file mẫu {msg_file}", (255, 255, 100), (200, 255, 255)))
    with open(msg_file, 'r', encoding='utf-8') as f:
        message = f.read().rstrip("\n") or "Nội dung mẫu"

    # --- DELAY ---
    print(grad("Nhập tốc độ treo",(255,80,80),(255,150,150)))
    try:
        delay = float(input(grad("Nhập : ",c1,c2)).strip() or 5)
    except:
        delay = 5.0

    # --- EMOJI ---
    print(grad("Random emoji (yes/no)",(255,80,80),(255,150,150)))
    use_emoji = input(grad("Nhập : ",c1,c2)).strip().lower() != "no"

    # --- REPEAT ---
    print(grad("Số tin để refresh cookie",(255,80,80),(255,150,150)))
    try:
        repeat_per_recipient = int(input(grad("Nhập : ",c1,c2)).strip() or 1)
    except:
        repeat_per_recipient = 1

    return cookies, recipient_ids, message, delay, repeat_per_recipient, use_emoji

# ================ MAIN ================
def main():
    c1,c2 = theme()
    while True:
        setup = interactive_setup(c1,c2)
        if setup == (None,)*6:
            return
        cookies, recipient_ids, message, delay, repeat_per_recipient, use_emoji = setup

        messengers=[]
        for i,c in enumerate(cookies,1):
            try:
                messengers.append(Messenger(c, global_counter))
            except Exception as e:
                print(grad(f"Cookie {i} lỗi: {e}", (255,80,80),(255,150,150)))
        if not messengers:
            print(grad("❌ Không có cookie hợp lệ! Kiểm tra lại.", (255,80,80),(255,150,150)))
            input(grad("Nhấn Enter để quay lại menu...", c1, c2))
            continue

        banner_live(messengers,c1,c2)
        print(grad("Bắt đầu gửi... Nhấn Ctrl+C để dừng.", (180,255,180),(100,255,255)))

        try:
            while True:
                banner_live(messengers,c1,c2)
                for messenger in list(messengers):
                    for recipient_id in recipient_ids:
                        for _ in range(repeat_per_recipient):
                            messenger.send_message(recipient_id, message, use_emoji)
                            time.sleep(delay)
                        messenger.refresh_fb_dtsg()
        except KeyboardInterrupt:
            print("\n" + grad("⏸️  Đã dừng bởi người dùng. Quay về menu.", (255,200,100),(255,160,200)))
            time.sleep(1)

if __name__ == "__main__":
    main()