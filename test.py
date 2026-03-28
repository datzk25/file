import os
import sys
import time
import random
import multiprocessing
from datetime import datetime
import threading
import base64
from pathlib import Path
import urllib.request

try:
    import requests
    from zlapi import ZaloAPI, ThreadType, Message, Mention, MultiMsgStyle, MessageStyle
except Exception:
    ZaloAPI = None
    ThreadType = None
    Message = None
    Mention = None
    MultiMsgStyle = None
    MessageStyle = None

# ================= DANH SÁCH MÀU =================
COLORS = [
    "#FF6B6B",  # Đỏ nhạt
    "#4ECDC4",  # Xanh ngọc
    "#45B7D1",  # Xanh dương
    "#96CEB4",  # Xanh lá nhạt
    "#FFEAA7",  # Vàng kem
    "#DDA0DD",  # Tím nhạt
    "#F7B05E",  # Cam
    "#B83B5E",  # Hồng đậm
    "#2C3A47",  # Xám đen
    "#FDA7DF",  # Hồng phấn
    "#9980FA",  # Tím
    "#E67E22",  # Cam đậm
    "#1ABC9C",  # Xanh ngọc bích
    "#E74C3C",  # Đỏ
    "#3498DB",  # Xanh dương đậm
    "#9B59B6",  # Tím
    "#F1C40F",  # Vàng
    "#2ECC71",  # Xanh lá
    "#E84393",  # Hồng
    "#00CEC9",  # Xanh biển
]

# ================= UI & COLOR =================
def rgb(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def grad(text, c1=(180,0,255), c2=(0,220,200)):
    if not text:
        return ""
    out = ""
    L = len(text)
    r1,g1,b1 = c1
    r2,g2,b2 = c2
    for i,ch in enumerate(text):
        t = i / max(1, L-1)
        r = int(r1 + (r2-r1)*t)
        g = int(g1 + (g2-g1)*t)
        b = int(b1 + (b2-b1)*t)
        out += rgb(r,g,b,ch)
    return out

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def theme_palette():
    palettes = [
        ((180,0,255),(0,220,200)),
        ((255,100,180),(100,200,255)),
        ((200,0,255),(0,255,150)),
        ((255,150,50),(255,80,200))
    ]
    return random.choice(palettes)

def print_banner(c1,c2):
    clear()
    logo = [
        "╔════════════════════════════════════════════════════════════╗",
        "║                                                            ║",
        "║        ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ██╗  ██╗        ║",
        "║        ████╗  ██║██╔═══██╗██║   ██║██╔══██╗╚██╗██╔╝        ║",
        "║        ██╔██╗ ██║██║   ██║██║   ██║███████║ ╚███╔╝         ║",
        "║        ██║╚██╗██║██║   ██║██║   ██║██╔══██║ ██╔██╗         ║",
        "║        ██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██╔╝ ██╗        ║",
        "║        ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝        ║",
        "║                                                            ║",
        "║              ✦ MESSENGER LIMITED SUITE  V7.5 ✦             ║",
        "║                                                            ║",
        "╚════════════════════════════════════════════════════════════╝",
    ]
    for l in logo:
        print(grad(l, c1, c2))
    print(grad("🌟 NOVAX ZALO TREO NGÔN + ẢNH | NHÂY SIÊU VIP 2026 🌟", c1, c2))
    now = datetime.now().strftime('%H:%M:%S %d/%m/%Y')
    neon_lines = [
        f"👑 Admin: Nguyễn Tiến Đạt",
        f"📱 Liên hệ: facebook.com/NovaX",
        f"📞 Zalo: 0395988143",
        f"🔄 Updated: 20/01/2026",
        f"🕓 Time: {now}",
    ]
    width = max(len(x) for x in neon_lines) + 6
    border = grad("—"*width, c1, c2)
    print(f"+{border}+")
    for t in neon_lines:
        inner = grad(" " + t + " ", c1, c2)
        print(f"|{inner.center(width)}")
    print(f"+{border}+")
    print()

# ================= XỬ LÝ ẢNH =================
def download_image_from_url(url):
    """Tải ảnh từ URL và chuyển sang base64"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        return None
    except Exception as e:
        print(rgb(255,100,100, f"❌ Lỗi tải ảnh từ URL: {e}"))
        return None

def load_image_base64(image_path):
    """Đọc file ảnh và chuyển sang base64"""
    try:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        else:
            return None
    except Exception as e:
        print(rgb(255,100,100, f"❌ Lỗi đọc ảnh: {e}"))
        return None

def load_image_messages(image_dir='images'):
    """Đọc danh sách ảnh từ thư mục"""
    messages = []
    try:
        if os.path.exists(image_dir):
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            image_files = []
            
            for file in os.listdir(image_dir):
                file_path = os.path.join(image_dir, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in image_extensions:
                        image_files.append(file_path)
            
            for img_path in sorted(image_files):
                base_name = os.path.splitext(img_path)[0]
                caption_file = base_name + '.txt'
                caption = ""
                
                if os.path.exists(caption_file):
                    with open(caption_file, 'r', encoding='utf-8') as f:
                        caption = f.read().strip()
                
                image_base64 = load_image_base64(img_path)
                if image_base64:
                    messages.append({
                        'type': 'image',
                        'path': img_path,
                        'name': os.path.basename(img_path),
                        'data': image_base64,
                        'caption': caption
                    })
            
            if messages:
                print(grad(f"✅ Đã đọc {len(messages)} ảnh từ thư mục {image_dir}", (0,255,0), (100,255,100)))
        else:
            os.makedirs(image_dir, exist_ok=True)
            print(grad(f"✅ Đã tạo thư mục {image_dir}. Hãy thêm ảnh vào để gửi!", (0,255,0), (100,255,100)))
    except Exception as e:
        print(rgb(255,100,100, f"❌ Lỗi đọc ảnh: {e}"))
    return messages

def load_messages_from_file(file_path='nhay.txt', is_image_mode=False):
    """Đọc danh sách tin nhắn từ file (hỗ trợ cả text và link ảnh)"""
    messages = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Kiểm tra nếu là link ảnh
                        if is_image_mode and (line.startswith('http://') or line.startswith('https://')):
                            # Tách link ảnh và caption (format: link|caption)
                            if '|' in line:
                                img_url, caption = line.split('|', 1)
                                img_url = img_url.strip()
                                caption = caption.strip()
                            else:
                                img_url = line
                                caption = ""
                            
                            print(grad(f"📥 Đang tải ảnh từ: {img_url[:50]}...", (100,200,255), (100,255,200)))
                            img_data = download_image_from_url(img_url)
                            if img_data:
                                messages.append({
                                    'type': 'image',
                                    'url': img_url,
                                    'data': img_data,
                                    'caption': caption
                                })
                                print(grad(f"   ✅ Đã tải xong ảnh {len(messages)}", (0,255,0), (100,255,100)))
                            else:
                                print(rgb(255,100,100, f"   ❌ Không tải được ảnh từ: {img_url}"))
                        else:
                            # Tin nhắn text
                            messages.append({
                                'type': 'text',
                                'text': line
                            })
            
            if messages:
                print(grad(f"✅ Đã đọc {len(messages)} nội dung từ {file_path}", (0,255,0), (100,255,100)))
            else:
                print(rgb(255,100,100, f"⚠️ File {file_path} không có nội dung hợp lệ!"))
        else:
            print(rgb(255,100,100, f"⚠️ Không tìm thấy file {file_path}!"))
            # Tạo file mẫu
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# File nội dung - mỗi dòng là 1 tin nhắn\n")
                f.write("# Đối với ảnh: nhập link ảnh, có thể thêm caption sau dấu |\n")
                f.write("# Ví dụ: https://example.com/image.jpg|Caption cho ảnh\n")
                f.write("Chào cậu! 💕\n")
                f.write("Cậu đang làm gì thế? 🌸\n")
                f.write("Nhớ cậu quá! 😘\n")
            print(grad(f"✅ Đã tạo file {file_path} mẫu!", (0,255,0), (100,255,100)))
            messages = [{'type': 'text', 'text': 'Chào cậu! 💕'}, 
                       {'type': 'text', 'text': 'Cậu đang làm gì thế? 🌸'},
                       {'type': 'text', 'text': 'Nhớ cậu quá! 😘'}]
    except Exception as e:
        print(rgb(255,100,100, f"❌ Lỗi đọc file: {e}"))
    return messages

# ================= Bot =================
class Bot(ZaloAPI if ZaloAPI is not None else object):
    def __init__(self, api_key, secret_key, imei, session_cookies, delay_min=0, 
                 message_text="", ttl=None, use_multi_color=False, mode="ngon", 
                 media_messages=None, color_mode="random"):
        if ZaloAPI is not None:
            super().__init__(api_key, secret_key, imei, session_cookies)
        self.delay_min = delay_min
        self.message_text = message_text
        self.ttl = ttl
        self.use_multi_color = use_multi_color
        self.color_mode = color_mode  # 'random', 'gradient', 'sequential'
        self.mode = mode  # 'ngon', 'nhay', 'anh'
        self.media_messages = media_messages if media_messages else []
        self.running_flags = {}
        self.processes = {}
        self.sent_count = 0
        self.start_time = datetime.now()
        self.message_index = 0
        self.current_color_index = 0

    def get_message_style(self, text):
        """Tạo style màu cho tin nhắn"""
        if not self.use_multi_color or MultiMsgStyle is None:
            return None
        
        styles = []
        
        if self.color_mode == "random":
            # Màu ngẫu nhiên cho mỗi tin nhắn
            color = random.choice(COLORS)
            styles.append(MessageStyle(offset=0, length=len(text), style="color", color=color, auto_format=False))
            
        elif self.color_mode == "sequential":
            # Tuần tự các màu
            color = COLORS[self.current_color_index % len(COLORS)]
            styles.append(MessageStyle(offset=0, length=len(text), style="color", color=color, auto_format=False))
            self.current_color_index += 1
            
        elif self.color_mode == "gradient":
            # Gradient màu cho tin nhắn
            segment_len = len(text) // 5
            for i in range(5):
                start = i * segment_len
                end = start + segment_len if i < 4 else len(text)
                if start < len(text):
                    color = COLORS[i % len(COLORS)]
                    styles.append(MessageStyle(offset=start, length=end-start, style="color", color=color, auto_format=False))
        
        # Thêm style font
        styles.append(MessageStyle(offset=0, length=len(text), style="font", size="15", auto_format=False))
        
        return MultiMsgStyle(styles) if styles else None

    def send_image_message(self, thread_id, thread_type, image_data, caption="", ttl=None):
        """Gửi tin nhắn kèm ảnh"""
        try:
            if hasattr(self, 'sendImage'):
                if ttl is not None:
                    self.sendImage(image_data, thread_id, thread_type, ttl=ttl)
                else:
                    self.sendImage(image_data, thread_id, thread_type)
            elif hasattr(self, 'sendFile'):
                if ttl is not None:
                    self.sendFile(image_data, thread_id, thread_type, ttl=ttl)
                else:
                    self.sendFile(image_data, thread_id, thread_type)
            else:
                print(rgb(255,100,100, "⚠️ API không hỗ trợ gửi ảnh!"))
                return False
            
            # Gửi caption nếu có
            if caption:
                time.sleep(1)
                if Message is not None:
                    style = self.get_message_style(caption)
                    if ttl is not None:
                        self.send(Message(text=caption, style=style), thread_id, thread_type, ttl=ttl)
                    else:
                        self.send(Message(text=caption, style=style), thread_id, thread_type)
            return True
        except Exception as e:
            print(rgb(255,100,100, f"❌ Lỗi gửi ảnh: {e}"))
            return False

    def start_spam(self, thread_id, thread_type, ttl=None):
        if self.mode == 'anh' and not self.media_messages:
            print(rgb(255,80,80, "❌ Không có ảnh để gửi!"))
            return
        if self.mode == 'ngon' and not self.message_text:
            print(rgb(255,80,80, "❌ Nội dung spam rỗng!"))
            return
        if self.mode == 'nhay' and not self.media_messages:
            print(rgb(255,80,80, "❌ Không có tin nhắn để nhây!"))
            return
            
        if thread_id not in self.running_flags:
            self.running_flags[thread_id] = multiprocessing.Value('b', False)
        if thread_id not in self.processes:
            self.processes[thread_id] = None
        if not self.running_flags[thread_id].value:
            try:
                if Message is not None:
                    self.send(Message(text="🚀 BẮT ĐẦU TREO NGÔN/ẢNH/NHÂY 🚀"), thread_id, thread_type, ttl=ttl if ttl is not None else None)
            except Exception:
                pass
            self.running_flags[thread_id].value = True
            self.processes[thread_id] = multiprocessing.Process(
                target=self.spam_messages,
                args=(thread_id, thread_type, self.running_flags[thread_id], ttl)
            )
            self.processes[thread_id].start()

    def spam_messages(self, thread_id, thread_type, running_flag, ttl=None):
        while running_flag.value:
            try:
                if hasattr(self, "setTyping"):
                    try: self.setTyping(thread_id, thread_type)
                    except: pass
                time.sleep(4)
                
                # Xử lý theo từng chế độ
                if self.mode == 'anh':
                    # Chế độ gửi ảnh
                    current = self.media_messages[self.message_index]
                    image_data = current.get('data')
                    caption = current.get('caption', '')
                    
                    if image_data:
                        self.send_image_message(thread_id, thread_type, image_data, caption, ttl)
                        display_msg = f"📸 Ảnh {self.message_index + 1}"
                        if caption:
                            display_msg += f" - {caption[:20]}..."
                    else:
                        display_msg = "❌ Lỗi ảnh"
                        
                elif self.mode == 'nhay':
                    # Chế độ nhây (có thể là text hoặc ảnh)
                    current = self.media_messages[self.message_index]
                    
                    if current.get('type') == 'image':
                        # Gửi ảnh
                        image_data = current.get('data')
                        caption = current.get('caption', '')
                        if image_data:
                            self.send_image_message(thread_id, thread_type, image_data, caption, ttl)
                            display_msg = f"📸 Ảnh {self.message_index + 1}"
                            if caption:
                                display_msg += f" - {caption[:20]}..."
                        else:
                            display_msg = "❌ Lỗi ảnh"
                    else:
                        # Gửi text
                        msg_text = current.get('text', '')
                        mention = None
                        if Mention is not None:
                            try:
                                mention = Mention("-1", length=len(msg_text), offset=0)
                            except:
                                mention = None
                        
                        style = self.get_message_style(msg_text) if self.use_multi_color else None
                        
                        if Message is not None:
                            if ttl is not None:
                                self.send(Message(text=msg_text, mention=mention, style=style), thread_id, thread_type, ttl=ttl)
                            else:
                                self.send(Message(text=msg_text, mention=mention, style=style), thread_id, thread_type)
                        
                        display_msg = msg_text[:20] + "..." if len(msg_text) > 23 else msg_text
                    
                else:  # ngon mode
                    # Chế độ ngôn (spam 1 tin nhắn)
                    if len(self.message_text) > 5:
                        display_msg = self.message_text[:5] + "***" + str(self.sent_count + 1)
                    else:
                        display_msg = self.message_text + "***" + str(self.sent_count + 1)
                    
                    mention = None
                    if Mention is not None:
                        try:
                            mention = Mention("-1", length=len(self.message_text), offset=0)
                        except:
                            mention = None
                    
                    style = self.get_message_style(self.message_text) if self.use_multi_color else None
                    
                    if Message is not None:
                        if ttl is not None:
                            self.send(Message(text=self.message_text, mention=mention, style=style), thread_id, thread_type, ttl=ttl)
                        else:
                            self.send(Message(text=self.message_text, mention=mention, style=style), thread_id, thread_type)
                
                self.sent_count += 1
                
                # Chuyển sang tin nhắn tiếp theo (vòng tròn)
                if self.media_messages:
                    self.message_index = (self.message_index + 1) % len(self.media_messages)
                
                # Hiển thị log realtime
                self.show_realtime_log(thread_id, display_msg)
                
            except Exception as e:
                print(rgb(255,100,100, f"❌ Lỗi gửi tin nhắn: {e}"))
            time.sleep(max(1, self.delay_min))

    def show_realtime_log(self, thread_id, current_msg=""):
        clear()
        now = datetime.now()
        current_date = now.strftime('%d/%m/%Y')
        current_time = now.strftime('%H:%M:%S')
        
        uptime = now - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        mode_names = {
            'ngon': '💬 NGÔN TREO MÁY 💬',
            'nhay': '🐍 NHÂY SIÊU VIP 2026 🐍',
            'anh': '📸 TREO ẢNH SIÊU VIP 📸'
        }
        mode_text = mode_names.get(self.mode, '💬 MODE UNKNOWN 💬')
        
        # Hiển thị banner
        logo_lines = [
            "╔════════════════════════════════════════════════════════════╗",
            "║                                                            ║",
            "║        ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ██╗  ██╗        ║",
            "║        ████╗  ██║██╔═══██╗██║   ██║██╔══██╗╚██╗██╔╝        ║",
            "║        ██╔██╗ ██║██║   ██║██║   ██║███████║ ╚███╔╝         ║",
            "║        ██║╚██╗██║██║   ██║██║   ██║██╔══██║ ██╔██╗         ║",
            "║        ██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██╔╝ ██╗        ║",
            "║        ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝        ║",
            "║                                                            ║",
            "║              ✦ MESSENGER LIMITED SUITE  V7.5 ✦             ║",
            "║                                                            ║",
            "╚════════════════════════════════════════════════════════════╝",
        ]
        
        for line in logo_lines:
            print(grad(line, (180,0,255), (0,220,200)))
        
        print(grad(f"[ NovaX ] {current_date} {current_time}", (255,255,100), (255,100,255)))
        print(grad("─" * 60, (255,100,100), (100,255,255)))
        print()
        
        print(grad(f"📊 {mode_text}", (200,0,255), (0,220,200)))
        print()
        
        print(grad(f"  🆔 Thread ID: {thread_id[:15]}...", (255,100,100), (255,200,100)))
        print(grad(f"     💬 Nội dung: {current_msg}", (100,255,100), (100,255,200)))
        print(grad(f"     📤 Đã gửi: {self.sent_count} tin", (255,200,100), (255,100,200)))
        print(grad(f"     ⏱️  Uptime: {uptime_str}", (100,200,255), (200,100,255)))
        
        if self.media_messages:
            total = len(self.media_messages)
            current = self.message_index
            print(grad(f"     🔄 Vòng lặp: {current}/{total}", (255,150,100), (255,100,150)))
        
        if self.use_multi_color:
            color_mode_names = {'random': '🌈 Random', 'sequential': '🎨 Tuần tự', 'gradient': '✨ Gradient'}
            print(grad(f"     🎨 Màu sắc: {color_mode_names.get(self.color_mode, 'Random')}", (100,255,200), (255,100,200)))
        
        print(grad("     " + "─" * 45, (100,100,255), (200,100,255)))
        print()

    def onMessage(self, *args, **kwargs): pass
    def onEvent(self, *args, **kwargs): pass
    def onAdminMessage(self, *args, **kwargs): pass

    def fetch_groups(self):
        try:
            if not hasattr(self, "fetchAllGroups"):
                raise AttributeError("fetchAllGroups không tồn tại trong ZaloAPI")
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id, _ in all_groups.gridVerMap.items():
                group_info = self.fetchGroupInfo(group_id)
                group_name = group_info.gridInfoMap[group_id]["name"]
                group_list.append({'id': group_id, 'name': group_name})
            return type('GroupObj', (), {'groups': [type('GroupItem', (), {'grid': g['id'], 'name': g['name']})() for g in group_list]})()
        except Exception as e:
            print(rgb(255,100,100, f"❌ Lỗi khi lấy danh sách nhóm: {e}"))
            return None

# ================= TASK MANAGEMENT =================
TASKS = []
TASK_LOCK = multiprocessing.Lock()

def add_task_entry(t_type, box_name, nick_name, proc):
    with TASK_LOCK:
        TASKS.append({
            'id': len(TASKS)+1,
            'type': t_type,
            'box': box_name,
            'nick': nick_name,
            'proc': proc,
            'ts': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            'sent_count': 0,
            'start_time': datetime.now()
        })

# ================= Process target =================
def process_target(api_key, secret_key, imei, session_cookies, message, delay, 
                   group_id, ttl, use_multi_color, mode, media_messages=None, color_mode="random"):
    try:
        bot = Bot(api_key, secret_key, imei, session_cookies, delay_min=delay, 
                  message_text=message, ttl=ttl, use_multi_color=use_multi_color, 
                  mode=mode, media_messages=media_messages, color_mode=color_mode)
    except Exception as e:
        print(rgb(255,100,100, f"[PID:{os.getpid()}] Khởi tạo Bot lỗi: {e}"))
        return

    try:
        bot.start_spam(group_id, ThreadType.GROUP, ttl=ttl)
    except Exception as e:
        print(rgb(255,100,100, f"[PID:{os.getpid()}] start_spam lỗi: {e}"))

# ================= Helpers chọn nhóm =================
def select_groups_interactive(imei, cookie, api_key='api_key', secret_key='secret_key'):
    try:
        bot_tmp = Bot(api_key, secret_key, imei, cookie)
    except Exception as e:
        print(rgb(255,100,100, f"❌ Không thể khởi tạo Bot tạm: {e}"))
        time.sleep(1)
        return None
    groups = bot_tmp.fetch_groups()
    if not groups or not getattr(groups, 'groups', None):
        print(rgb(255,100,100, "❌ Không lấy được nhóm nào!"))
        time.sleep(1)
        return None
    print()
    print(grad("📚 DANH SÁCH NHÓM (CHỌN SỐ):", (200,0,255), (0,220,200)))
    for idx, g in enumerate(groups.groups, start=1):
        print(grad(f" [{idx}] {g.name} (ID: {g.grid})", (160,0,255), (0,220,200)))
    print()
    raw = input(rgb(255,255,200, "🔸 Nhập số nhóm muốn chạy (VD: 1,3) hoặc 0 để quay lại: ")).strip()
    if raw == '0':
        return None
    try:
        nums = [int(i.strip()) for i in raw.split(',') if i.strip() != '']
    except:
        print(rgb(255,100,100, "❌ Định dạng không hợp lệ!")); time.sleep(1); return None
    selected = [n for n in nums if 1 <= n <= len(groups.groups)]
    if not selected:
        print(rgb(255,100,100, "❌ Không có nhóm hợp lệ!")); time.sleep(1); return None
    ids = [groups.groups[i-1].grid for i in selected]
    names = [groups.groups[i-1].name for i in selected]
    return ids, names

# ================= Menu =================
def main_menu():
    c1,c2 = theme_palette()
    while True:
        print_banner(c1,c2)
        print(grad("1️⃣  Ngôn (Spam 1 tin nhắn)", c1,c2))
        print(grad("2️⃣  Nhây (Đọc từ file nhay.txt - hỗ trợ cả text và link ảnh)", c1,c2))
        print(grad("3️⃣  Treo Ảnh (Gửi ảnh từ thư mục images)", c1,c2))
        print(grad("0️⃣  Thoát chương trình", c1,c2))
        choice = input(rgb(255,255,200,"🔹 Chọn chức năng: ")).strip()
        if choice == '0':
            print(rgb(0,255,0, "✅ Đang thoát... Task đang chạy vẫn giữ nguyên."))
            break
        elif choice == '1':
            try:
                flow_create_ngon(c1,c2)
            except Exception as e:
                print(rgb(255,100,100, f"❌ Lỗi Task Ngôn: {e}")); time.sleep(1)
        elif choice == '2':
            try:
                flow_create_nhay(c1,c2)
            except Exception as e:
                print(rgb(255,100,100, f"❌ Lỗi Task Nhây: {e}")); time.sleep(1)
        elif choice == '3':
            try:
                flow_create_anh(c1,c2)
            except Exception as e:
                print(rgb(255,100,100, f"❌ Lỗi Task Ảnh: {e}")); time.sleep(1)
        else:
            print(rgb(255,100,100, "❌ Lựa chọn không hợp lệ!")); time.sleep(1)

# ================= Flow tạo task ngôn =================
def flow_create_ngon(c1,c2):
    print(grad("\n" + "="*60, c1, c2))
    print(grad("📝 NHẬP THÔNG TIN TASK NGÔN", c1, c2))
    print(grad("="*60, c1, c2))
    
    print(rgb(255,255,100, "\n[1/5] NHẬP IMEI:"))
    imei = input(grad("➡️  IMEI (0 để quay lại): ", c1, c2)).strip()
    if imei == '0': return
    
    print(rgb(255,255,100, "\n[2/5] NHẬP COOKIE:"))
    print(grad("💡 Cookie phải là định dạng dict, ví dụ: {'key':'value'}", (100,200,255), (150,150,255)))
    cookie_str = input(grad("➡️  Cookie (0 để quay lại): ", c1, c2)).strip()
    if cookie_str == '0': return
    try:
        session_cookies = eval(cookie_str)
        if not isinstance(session_cookies, dict):
            print(rgb(255,100,100, "❌ Cookie phải là dict!")); time.sleep(1); return
    except:
        print(rgb(255,100,100, "❌ Cookie không hợp lệ!")); time.sleep(1); return

    sel = select_groups_interactive(imei, session_cookies)
    if not sel: return
    group_ids, group_names = sel

    print(rgb(255,255,100, "\n[3/5] NHẬP NỘI DUNG TIN NHẮN:"))
    print(grad("💡 Nội dung tin nhắn sẽ được spam liên tục", (100,200,255), (150,150,255)))
    message_text = input(grad("➡️  Nội dung: ", c1, c2)).strip()
    
    if not message_text:
        print(rgb(255,100,100, "❌ Nội dung tin nhắn không được để trống!")); time.sleep(1); return

    print(rgb(255,255,100, "\n[4/5] CÀI ĐẶT DELAY:"))
    try:
        delay = float(input(grad("➡️  Delay giữa các tin nhắn (giây): ", c1, c2)).strip())
        if delay < 0: raise ValueError
    except:
        print(rgb(255,100,100, "❌ Delay không hợp lệ!")); time.sleep(1); return

    print(rgb(255,255,100, "\n[5/5] CÀI ĐẶT MÀU SẮC:"))
    print(grad("  1. Không màu", (150,150,150), (200,200,200)))
    print(grad("  2. Màu ngẫu nhiên (20+ màu)", (200,100,255), (255,100,200)))
    print(grad("  3. Màu tuần tự", (100,200,255), (150,150,255)))
    print(grad("  4. Gradient (5 màu trong 1 tin)", (255,200,100), (255,150,100)))
    color_choice = input(grad("➡️  Chọn kiểu màu (1-4): ", c1, c2)).strip()
    
    use_multi_color = color_choice != '1'
    color_mode = "random"
    if color_choice == '2':
        color_mode = "random"
    elif color_choice == '3':
        color_mode = "sequential"
    elif color_choice == '4':
        color_mode = "gradient"

    ttl = None
    ttl_choice = input(grad("\n⏰ Bật TTL? (Y/N): ", c1, c2)).strip().lower()
    if ttl_choice == 'y':
        try:
            ttl_sec = float(input(grad("⏰ TTL (giây): ", c1, c2)).strip())
            if ttl_sec > 0: ttl = int(ttl_sec*1000)
        except:
            ttl = None

    print(grad("\n🔥 ĐANG KHỞI TẠO TASK NGÔN...", (255,100,100), (255,200,100)))
    
    for gid, gname in zip(group_ids, group_names):
        p = multiprocessing.Process(
            target=process_target,
            args=('api_key','secret_key',imei,session_cookies,message_text,delay,gid,ttl,use_multi_color,"ngon",None,color_mode)
        )
        p.start()
        add_task_entry("Ngôn", gname, "NovaX", p)

    print(rgb(0,255,0,f"✅ Task Ngôn đã tạo cho {len(group_ids)} nhóm!"))
    time.sleep(2)

# ================= Flow tạo task nhây =================
def flow_create_nhay(c1,c2):
    print(grad("\n" + "="*60, c1, c2))
    print(grad("🐍 NHẬP THÔNG TIN TASK NHÂY", c1, c2))
    print(grad("="*60, c1, c2))
    
    print(rgb(255,255,100, "\n[1/6] NHẬP IMEI:"))
    imei = input(grad("➡️  IMEI (0 để quay lại): ", c1, c2)).strip()
    if imei == '0': return
    
    print(rgb(255,255,100, "\n[2/6] NHẬP COOKIE:"))
    print(grad("💡 Cookie phải là định dạng dict, ví dụ: {'key':'value'}", (100,200,255), (150,150,255)))
    cookie_str = input(grad("➡️  Cookie (0 để quay lại): ", c1, c2)).strip()
    if cookie_str == '0': return
    try:
        session_cookies = eval(cookie_str)
        if not isinstance(session_cookies, dict):
            print(rgb(255,100,100, "❌ Cookie phải là dict!")); time.sleep(1); return
    except:
        print(rgb(255,100,100, "❌ Cookie không hợp lệ!")); time.sleep(1); return

    sel = select_groups_interactive(imei, session_cookies)
    if not sel: return
    group_ids, group_names = sel

    print(rgb(255,255,100, "\n[3/6] CHỌN NGUỒN NỘI DUNG:"))
    print(grad("  1. Đọc từ file nhay.txt (text + link ảnh)", (100,200,255), (150,150,255)))
    print(grad("  2. Chỉ đọc text từ file nhay.txt", (100,200,255), (150,150,255)))
    source_choice = input(grad("➡️  Chọn (1-2): ", c1, c2)).strip()
    
    is_image_mode = source_choice == '1'
    media_messages = load_messages_from_file('nhay.txt', is_image_mode)
    
    if not media_messages:
        print(rgb(255,100,100, "❌ Không có nội dung để nhây!"))
        time.sleep(2)
        return
    
    print(grad(f"\n📊 ĐÃ ĐỌC {len(media_messages)} NỘI DUNG:", (100,255,100), (100,255,200)))
    for i, msg in enumerate(media_messages[:5], 1):
        if msg.get('type') == 'image':
            print(grad(f"   {i}. 📸 ẢNH: {msg.get('caption', 'Không caption')[:30]}...", (150,150,255), (100,200,255)))
        else:
            preview = msg.get('text', '')[:40] + "..." if len(msg.get('text', '')) > 43 else msg.get('text', '')
            print(grad(f"   {i}. 💬 {preview}", (150,150,255), (100,200,255)))
    if len(media_messages) > 5:
        print(grad(f"   ... và {len(media_messages)-5} nội dung khác", (150,150,255), (100,200,255)))

    print(rgb(255,255,100, "\n[4/6] CÀI ĐẶT DELAY:"))
    try:
        delay = float(input(grad("➡️  Delay giữa các tin nhắn (giây): ", c1, c2)).strip())
        if delay < 0: raise ValueError
    except:
        print(rgb(255,100,100, "❌ Delay không hợp lệ!")); time.sleep(1); return

    print(rgb(255,255,100, "\n[5/6] CÀI ĐẶT MÀU SẮC:"))
    print(grad("  1. Không màu", (150,150,150), (200,200,200)))
    print(grad("  2. Màu ngẫu nhiên (20+ màu)", (200,100,255), (255,100,200)))
    print(grad("  3. Màu tuần tự", (100,200,255), (150,150,255)))
    print(grad("  4. Gradient (5 màu trong 1 tin)", (255,200,100), (255,150,100)))
    color_choice = input(grad("➡️  Chọn kiểu màu (1-4): ", c1, c2)).strip()
    
    use_multi_color = color_choice != '1'
    color_mode = "random"
    if color_choice == '2':
        color_mode = "random"
    elif color_choice == '3':
        color_mode = "sequential"
    elif color_choice == '4':
        color_mode = "gradient"

    ttl = None
    print(rgb(255,255,100, "\n[6/6] TTL:"))
    ttl_choice = input(grad("⏰ Bật TTL? (Y/N): ", c1, c2)).strip().lower()
    if ttl_choice == 'y':
        try:
            ttl_sec = float(input(grad("⏰ TTL (giây): ", c1, c2)).strip())
            if ttl_sec > 0: ttl = int(ttl_sec*1000)
        except:
            ttl = None

    print(grad("\n🔥 ĐANG KHỞI TẠO TASK NHÂY SIÊU VIP...", (255,100,100), (255,200,100)))
    
    for gid, gname in zip(group_ids, group_names):
        p = multiprocessing.Process(
            target=process_target,
            args=('api_key','secret_key',imei,session_cookies,"",delay,gid,ttl,use_multi_color,"nhay",media_messages,color_mode)
        )
        p.start()
        add_task_entry("Nhây", gname, "NovaX", p)

    print(rgb(0,255,0,f"✅ Task Nhây đã tạo cho {len(group_ids)} nhóm!"))
    print(grad("🐍 CHÚC BẠN NHÂY VUI VẺ! 🐍", (255,100,100), (255,200,100)))
    time.sleep(2)

# ================= Flow tạo task ảnh =================
def flow_create_anh(c1,c2):
    print(grad("\n" + "="*60, c1, c2))
    print(grad("📸 NHẬP THÔNG TIN TREO ẢNH", c1, c2))
    print(grad("="*60, c1, c2))
    
    print(rgb(255,255,100, "\n[1/5] NHẬP IMEI:"))
    imei = input(grad("➡️  IMEI (0 để quay lại): ", c1, c2)).strip()
    if imei == '0': return
    
    print(rgb(255,255,100, "\n[2/5] NHẬP COOKIE:"))
    print(grad("💡 Cookie phải là định dạng dict, ví dụ: {'key':'value'}", (100,200,255), (150,150,255)))
    cookie_str = input(grad("➡️  Cookie (0 để quay lại): ", c1, c2)).strip()
    if cookie_str == '0': return
    try:
        session_cookies = eval(cookie_str)
        if not isinstance(session_cookies, dict):
            print(rgb(255,100,100, "❌ Cookie phải là dict!")); time.sleep(1); return
    except:
        print(rgb(255,100,100, "❌ Cookie không hợp lệ!")); time.sleep(1); return

    sel = select_groups_interactive(imei, session_cookies)
    if not sel: return
    group_ids, group_names = sel

    print(rgb(255,255,100, "\n[3/5] CHỌN NGUỒN ẢNH:"))
    print(grad("  1. Đọc ảnh từ thư mục images/", (100,200,255), (150,150,255)))
    print(grad("  2. Đọc link ảnh từ file nhay.txt", (100,200,255), (150,150,255)))
    source_choice = input(grad("➡️  Chọn (1-2): ", c1, c2)).strip()
    
    if source_choice == '1':
        media_messages = load_image_messages('images')
    else:
        media_messages = load_messages_from_file('nhay.txt', is_image_mode=True)
        # Lọc chỉ lấy ảnh
        media_messages = [m for m in media_messages if m.get('type') == 'image']
    
    if not media_messages:
        print(rgb(255,100,100, "❌ Không có ảnh để gửi!"))
        time.sleep(2)
        return
    
    print(grad(f"\n📊 ĐÃ ĐỌC {len(media_messages)} ẢNH:", (100,255,100), (100,255,200)))
    for i, msg in enumerate(media_messages[:5], 1):
        print(grad(f"   {i}. 📸 {msg.get('name', 'Ảnh')} - {msg.get('caption', 'Không caption')[:30]}...", (150,150,255), (100,200,255)))
    if len(media_messages) > 5:
        print(grad(f"   ... và {len(media_messages)-5} ảnh khác", (150,150,255), (100,200,255)))

    print(rgb(255,255,100, "\n[4/5] CÀI ĐẶT DELAY:"))
    try:
        delay = float(input(grad("➡️  Delay giữa các ảnh (giây): ", c1, c2)).strip())
        if delay < 0: raise ValueError
    except:
        print(rgb(255,100,100, "❌ Delay không hợp lệ!")); time.sleep(1); return

    ttl = None
    print(rgb(255,255,100, "\n[5/5] TTL:"))
    ttl_choice = input(grad("⏰ Bật TTL? (Y/N): ", c1, c2)).strip().lower()
    if ttl_choice == 'y':
        try:
            ttl_sec = float(input(grad("⏰ TTL (giây): ", c1, c2)).strip())
            if ttl_sec > 0: ttl = int(ttl_sec*1000)
        except:
            ttl = None

    print(grad("\n🔥 ĐANG KHỞI TẠO TREO ẢNH...", (255,100,100), (255,200,100)))
    
    for gid, gname in zip(group_ids, group_names):
        p = multiprocessing.Process(
            target=process_target,
            args=('api_key','secret_key',imei,session_cookies,"",delay,gid,ttl,False,"anh",media_messages,"random")
        )
        p.start()
        add_task_entry("Treo Ảnh", gname, "NovaX", p)

    print(rgb(0,255,0,f"✅ Treo Ảnh đã tạo cho {len(group_ids)} nhóm!"))
    print(grad("📸 CHÚC BẠN TREO ẢNH VUI VẺ! 📸", (255,100,100), (255,200,100)))
    time.sleep(2)

# ================= Run =================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(rgb(0,255,0,"\n✅ Thoát bằng Ctrl+C. Task đang chạy vẫn giữ nguyên."))