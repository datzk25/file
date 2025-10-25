
import requests, time, re, os, threading, random, shutil, socket
from datetime import datetime

# ================ UTILS & UI ================
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

# ================ GLOBALS ================
global_counter = {"sent":0,"fail":0,"lock":threading.Lock()}
TASKS = []   # list of Task instances
TASK_LOCK = threading.Lock()
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
                    return True
            return False
        except:
            return False

    def send_message(self, recipient_id, message, use_emoji=True):
        msg_to_send = message + (" " + random.choice(EMOJIS) if use_emoji else "")
        if not self.fb_dtsg:
            if not self.refresh_fb_dtsg():
                with self.counter_ref["lock"]:
                    self.counter_ref["fail"] += 1
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
            return r.status_code == 200
        except:
            with self.counter_ref["lock"]:
                self.counter_ref["fail"] += 1
            return False

# ================ TASK CLASS ================
class Task:
    def __init__(self, kind, cookie, recipient_ids, message_source, delay, use_emoji, refresh_after, c1, c2, intro_message=None):
        self.kind = kind
        self.cookie = cookie
        self.recipient_ids = recipient_ids
        self.message_source = message_source
        self.delay = float(delay)
        self.use_emoji = use_emoji
        self.refresh_after = int(refresh_after) if refresh_after else 1
        self.c1 = c1; self.c2 = c2
        self.intro_message = intro_message

        self.messenger = Messenger(self.cookie, global_counter)
        self.thread = None
        self.stop_event = threading.Event()
        self.start_time = None
        self.sent_count = 0

    def start(self):
        self.start_time = datetime.now()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        try:
            if self.intro_message:
                for rid in self.recipient_ids:
                    if self.stop_event.is_set(): break
                    self.messenger.send_message(rid, self.intro_message, use_emoji=False)
                    time.sleep(self.delay)

            if self.kind == "Nhây":
                msgs = list(self.message_source)
                idx = 0; local_count = 0
                while not self.stop_event.is_set():
                    msg = msgs[idx % len(msgs)].strip()
                    for rid in self.recipient_ids:
                        if self.stop_event.is_set(): break
                        self.messenger.send_message(rid, msg, use_emoji=self.use_emoji)
                        self.sent_count += 1
                        local_count += 1
                        time.sleep(self.delay)
                        if local_count >= self.refresh_after:
                            local_count = 0
                            self.messenger.refresh_fb_dtsg()
                    idx += 1
            else:
                content = str(self.message_source)
                local_count = 0
                while not self.stop_event.is_set():
                    for rid in self.recipient_ids:
                        if self.stop_event.is_set(): break
                        self.messenger.send_message(rid, content, use_emoji=self.use_emoji)
                        self.sent_count += 1
                        local_count += 1
                        time.sleep(self.delay)
                        if local_count >= self.refresh_after:
                            local_count = 0
                            self.messenger.refresh_fb_dtsg()
        except:
            pass

    def stop(self, wait=3):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=wait)

    def uptime_str(self):
        if not self.start_time: return "00:00:00"
        delta = datetime.now() - self.start_time
        h, rem = divmod(int(delta.total_seconds()), 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def status(self):
        try: ok = self.messenger.fb_dtsg is not None
        except: ok = False
        return "Online" if ok else "Offline"

# ================ BANNER / LIVE ================
def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        try: return socket.gethostbyname(socket.gethostname())
        except: return "Không xác định"

def banner_live(messengers=None,c1=(255,0,255),c2=(0,255,255)):
    clear()
    logo(c1,c2)
    ip = get_public_ip()
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    neon_box("THÔNG TIN TOOL MESSENGER", [
        "👑 Admin     : Tiến Đạt (Real)",
        f"📅 Khởi chạy : {now}",
        "⚡ Phiên bản : Premium V5.0",
        "🌈 Developer : NovaX Team",
        f"🌐 Thiết bị : {ip}"
    ], c1, c2)
    if messengers:
        print(grad("\nDanh sách cookie hợp lệ:", c1, c2))
        for i,m in enumerate(messengers,1):
            try:
                print(grad(f"  Cookie{i} | UID: {m.user_id}", (180,255,180),(100,255,255)))
            except: pass
    print()

# ================ INTERACTIVE HELPERS ================
def input_nonempty(prompt, c1, c2, default=None):
    while True:
        print(grad(prompt,c1,c2))
        v = input(grad("> ",c1,c2)).strip()
        if v: return v
        if default is not None: return default

def parse_recipient_input(raw):
    parts = [p.strip() for p in raw.replace(";",",").split(",") if p.strip()]
    return parts

# ================ MENU ACTIONS ================
def action_nhay(c1,c2):
    print(grad("Nhập cookie",c1,c2))
    cookie = input(grad("Cookie: ",c1,c2)).strip()
    if not cookie:
        print(grad("❌ Cookie không hợp lệ. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    print(grad("Nhập ID Box",c1,c2))
    raw_ids = input(grad("ID Box: ",c1,c2)).strip()
    recipient_ids = parse_recipient_input(raw_ids)
    if not recipient_ids:
        print(grad("❌ ID Box không hợp lệ. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    print(grad("Tốc độ (3.2)",c1,c2))
    try:
        delay = float(input(grad("Delay: ",c1,c2)).strip() or 5)
    except:
        delay = 5.0

    print(grad("Random emoji? (yes/no)",c1,c2))
    use_emoji = input(grad("Emoji: ",c1,c2)).strip().lower() not in ("no","n","0")

    print(grad("Số tin làm mới cookie",c1,c2))
    try:
        refresh_after = int(input(grad("Refresh after: ",c1,c2)).strip() or 1)
    except:
        refresh_after = 1

    intro_msg = "𝐀𝐧𝐤 𝐋𝐚 𝐍𝐨𝐯𝐚𝐗 🔥"

    nhay_file = "nhay.txt"
    if not os.path.exists(nhay_file):
        with open(nhay_file,"w",encoding="utf-8") as f:
            f.write("Ank Là NovaX.\nXin chào.\nTest nhây.")
        print(grad(f"Đã tạo file mẫu {nhay_file}", (255,255,100),(200,255,255)))
    with open(nhay_file,"r",encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]
    if not lines:
        print(grad(f"File {nhay_file} rỗng. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    try:
        task = Task("Nhây", cookie, recipient_ids, lines, delay, use_emoji, refresh_after, c1, c2, intro_message=intro_msg)
    except Exception as e:
        print(grad(f"❌ Tạo Task thất bại: {e}. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    with TASK_LOCK:
        TASKS.append(task)
    task.start()
    print(grad("✅ Task Nhây đã được tạo và đang chạy (quay lại menu).", (100,255,180),(50,200,255)))
    time.sleep(1)

# ------------------ action_ngon ------------------
def action_ngon(c1,c2):
    print(grad("Nhập cookie",c1,c2))
    cookie = input(grad("Cookie: ",c1,c2)).strip()
    if not cookie:
        print(grad("❌ Cookie không hợp lệ. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    print(grad("Nhập ID Box",c1,c2))
    raw_ids = input(grad("ID Box: ",c1,c2)).strip()
    recipient_ids = parse_recipient_input(raw_ids)
    if not recipient_ids:
        print(grad("❌ ID Box không hợp lệ. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    print(grad("Nhập tên file",c1,c2))
    fname = input(grad("File: ",c1,c2)).strip() or "ngon.txt"
    if not os.path.exists(fname):
        with open(fname,"w",encoding="utf-8") as f:
            f.write("𝐀𝐧𝐤 𝐋𝐚 𝐍𝐨𝐯𝐚𝐗 🔥")
        print(grad(f"Đã tạo file mẫu {fname}", (255,255,100),(200,255,255)))
    with open(fname,"r",encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        print(grad(f"File {fname} rỗng. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    print(grad("Tốc độ (3.2)",c1,c2))
    try:
        delay = float(input(grad("Delay: ",c1,c2)).strip() or 5)
    except:
        delay = 5.0

    print(grad("Random emoji? (yes/no)",c1,c2))
    use_emoji = input(grad("Emoji: ",c1,c2)).strip().lower() not in ("no","n","0")

    print(grad("số tin làm mới cookie",c1,c2))
    try:
        refresh_after = int(input(grad("Refresh after: ",c1,c2)).strip() or 1)
    except:
        refresh_after = 1

    intro_msg = "𝐀𝐧𝐤 𝐋𝐚 𝐍𝐨𝐯𝐚𝐗 🔥"
    try:
        task = Task("Ngôn", cookie, recipient_ids, content, delay, use_emoji, refresh_after, c1, c2, intro_message=intro_msg)
    except Exception as e:
        print(grad(f"❌ Tạo Task thất bại: {e}. Quay lại menu...", (255,80,80),(255,150,150)))
        time.sleep(1)
        return

    with TASK_LOCK:
        TASKS.append(task)
    task.start()
    print(grad("✅ Task Ngôn đã được tạo và đang chạy (quay lại menu).", (100,255,180),(50,200,255)))
    time.sleep(1)

# ================ TASK LIST / STOP ================
def action_task_list(c1,c2):
    while True:
        banner_live(None,c1,c2)
        print(grad("DANH SÁCH TASK", c1, c2))
        with TASK_LOCK:
            if not TASKS:
                print(grad("Chưa có task nào.", (255,200,100),(255,160,200)))
            else:
                for idx, t in enumerate(TASKS, start=1):
                    ids = ",".join(t.recipient_ids)
                    print(grad(f"[{idx:02d}] {t.kind} | UID: {t.messenger.user_id} | ID Box: {ids} | Uptime: {t.uptime_str()} | {t.status()} | Sent: {t.sent_count}", (180,255,180),(100,255,255)))
        print()
        print(grad("Nhập số Task để dừng\nNhập 0 Menu", c1, c2))
        choice = input(grad("Chọn: ", c1, c2)).strip()
        if not choice:
            continue
        if choice == "0":
            return
        if not choice.isdigit():
            continue
        idx = int(choice)
        with TASK_LOCK:
            if 1 <= idx <= len(TASKS):
                t = TASKS[idx-1]
                print(grad(f"⏳ Đang dừng Task [{idx:02d}]...", (255,200,100),(255,160,200)))
                t.stop()
                TASKS.pop(idx-1)
                print(grad(f"✅ Task [{idx:02d}] đã dừng và xóa.", (100,255,180),(50,200,255)))
                time.sleep(1)
            else:
                print(grad("❌ Số task không hợp lệ. Quay lại menu...", (255,80,80),(255,150,150)))
                time.sleep(1)

# ================ MAIN MENU ================
def main():
    c1,c2 = theme()
    while True:
        try:
            banner_live(None,c1,c2)
            neon_box("MENU CHÍNH", [
                "[ 1 ] Nhây",
                "[ 2 ] Ngôn",
                "[ 3 ] Task",
                "[ 0 ] Thoát"
            ], c1, c2)
            choice = input(grad("Chọn chức năng: ", c1, c2)).strip()
            if choice == "1":
                action_nhay(c1,c2)
            elif choice == "2":
                action_ngon(c1,c2)
            elif choice == "3":
                action_task_list(c1,c2)
            elif choice == "0":
                print(grad("⏳ Dừng toàn bộ task...", (255,200,100),(255,160,200)))
                with TASK_LOCK:
                    for t in TASKS:
                        t.stop()
                    TASKS.clear()
                print(grad("✅ Đã dừng tất cả. Thoát chương trình.", (100,255,180),(50,200,255)))
                break
            else:
                continue
        except KeyboardInterrupt:
            print("\n" + grad("⏸️  Đã dừng bởi người dùng. Quay về menu.", (255,200,100),(255,160,200)))
            time.sleep(1)
            continue

if __name__ == "__main__":
    main()