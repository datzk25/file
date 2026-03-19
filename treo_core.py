#!/usr/bin/env python3
# treo_core.py - Core Functions for TREO BOT
import sys
import os
import json
import time
import hashlib
import random
import string
import requests
import paho.mqtt.client as mqtt
import ssl
import re
import threading
from urllib.parse import urlparse
from collections import defaultdict
from typing import Dict, List, Optional
from datetime import datetime
import pytz

# Timezone VN
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Global variables - QUAN TRỌNG: Phải khởi tạo đúng cách
treo_cookie_attempts = defaultdict(lambda: {
    'count': 0, 
    'last_reset': time.time(), 
    'banned_until': 0, 
    'permanent_ban': False
})

# Các biến global dùng chung
treo_active_threads = {}
stop_flags = {}
running_tasks = {}  # Dict lưu trạng thái task đang chạy
task_counter = 0    # Biến đếm task ID
task_start_times = {}  # Lưu thời gian bắt đầu task
task_info = {}      # Lưu thông tin chi tiết task

# Lock để tránh xung đột khi ghi dữ liệu
task_lock = threading.Lock()


def treo_handle_failed_connection(cookie_hash):
    """Xử lý khi kết nối thất bại và quản lý ban cookie"""
    global treo_cookie_attempts
    
    with task_lock:
        current_time = time.time()
        
        # Reset counter sau 12 giờ
        if current_time - treo_cookie_attempts[cookie_hash]['last_reset'] > 43200:
            treo_cookie_attempts[cookie_hash]['count'] = 0
            treo_cookie_attempts[cookie_hash]['last_reset'] = current_time
            treo_cookie_attempts[cookie_hash]['banned_until'] = 0
        
        # Xử lý ban tạm thời/vĩnh viễn
        if treo_cookie_attempts[cookie_hash]['banned_until'] > 0:
            ban_count = treo_cookie_attempts[cookie_hash].get('ban_count', 0) + 1
            treo_cookie_attempts[cookie_hash]['ban_count'] = ban_count
            
            if ban_count >= 5:
                treo_cookie_attempts[cookie_hash]['permanent_ban'] = True
                print(f"\n⚠️  Cookie {cookie_hash[:10]}... đã bị ban vĩnh viễn!")
                
                # Dừng tất cả thread đang chạy với cookie này
                for key in list(treo_active_threads.keys()):
                    if key.startswith(cookie_hash):
                        if hasattr(treo_active_threads[key], 'stop'):
                            treo_active_threads[key].stop()
                        del treo_active_threads[key]


def treo_generate_offline_threading_id() -> str:
    """Tạo ID cho tin nhắn offline"""
    ret = int(time.time() * 1000)
    value = random.randint(0, 4294967295)
    binary_str = format(value, "022b")[-22:]
    msgs = bin(ret)[2:] + binary_str
    return str(int(msgs, 2))


def treo_json_minimal(data):
    """Chuyển đổi JSON với format tối giản"""
    return json.dumps(data, separators=(",", ":"))


class TreoFacebookAuth:
    """Class xác thực Facebook từ cookie"""
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.fb_dtsg = None
        self.jazoest = None
        self.rev = None
        self.init_params()

    def id_user(self):
        """Lấy User ID từ cookie"""
        try:
            match = re.search(r"c_user=(\d+)", self.cookie)
            if not match:
                raise Exception("Cookie không hợp lệ - không tìm thấy c_user")
            return match.group(1)
        except Exception as e:
            raise Exception(f"Lỗi khi lấy user_id: {str(e)}")

    def init_params(self):
        """Lấy các tham số xác thực từ Facebook"""
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        urls = [
            'https://www.facebook.com',
            'https://mbasic.facebook.com',
            'https://m.facebook.com'
        ]

        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code != 200:
                    continue

                fb_dtsg_patterns = [
                    r'"token":"(.*?)"',
                    r'name="fb_dtsg" value="(.*?)"',
                    r'"fb_dtsg":"(.*?)"',
                    r'fb_dtsg=([^&"]+)'
                ]
                jazoest_pattern = r'name="jazoest" value="(\d+)"'
                rev_pattern = r'"__rev":"(\d+)"'

                fb_dtsg = None
                for pattern in fb_dtsg_patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        fb_dtsg = match.group(1)
                        break

                jazoest_match = re.search(jazoest_pattern, response.text)
                rev_match = re.search(rev_pattern, response.text)

                if fb_dtsg:
                    self.fb_dtsg = fb_dtsg
                    self.jazoest = jazoest_match.group(1) if jazoest_match else "22036"
                    self.rev = rev_match.group(1) if rev_match else "1015919737"
                    return

            except Exception as e:
                time.sleep(2)

        raise Exception("Không thể lấy fb_dtsg từ bất kỳ URL nào")


class TreoMQTTSender:
    """Class gửi tin nhắn qua MQTT"""
    def __init__(self, dataFB):
        self.dataFB = dataFB
        self.mqtt = None
        self.ws_req_number = 0
        self.syncToken = None
        self.lastSeqID = dataFB.get("lastSeqID", "0")
        self.req_callbacks = {}
        self.cookie_hash = hashlib.md5(dataFB['cookieFacebook'].encode()).hexdigest()
        self.last_cleanup = time.time()
        self.success_count = 0
        self.message_count = 0
        self.connected = False
        self.task_id = None

    def cleanup_memory(self):
        """Dọn dẹp bộ nhớ định kỳ"""
        current_time = time.time()
        if current_time - self.last_cleanup > 3600:
            self.req_callbacks.clear()
            self.last_cleanup = current_time

    def on_disconnect(self, client, userdata, rc):
        """Xử lý khi bị ngắt kết nối"""
        global treo_cookie_attempts
        self.connected = False
        
        if rc != 0:
            treo_cookie_attempts[self.cookie_hash]['count'] += 1
            current_time = time.time()
            
            # Reset counter sau 12 giờ
            if current_time - treo_cookie_attempts[self.cookie_hash]['last_reset'] > 43200:
                treo_cookie_attempts[self.cookie_hash]['count'] = 1
                treo_cookie_attempts[self.cookie_hash]['last_reset'] = current_time
            
            # Nếu thất bại 20 lần, ban 12 giờ
            if treo_cookie_attempts[self.cookie_hash]['count'] >= 20:
                treo_cookie_attempts[self.cookie_hash]['banned_until'] = current_time + 43200

    def _messenger_queue_publish(self, client, userdata, flags, rc):
        """Khởi tạo queue messenger"""
        if rc != 0:
            return

        self.connected = True
        
        # Subscribe topics
        topics = [("/t_ms", 0)]
        client.subscribe(topics)

        # Tạo queue
        queue = {
            "sync_api_version": 10,
            "max_deltas_able_to_process": 1000,
            "delta_batch_size": 500,
            "encoding": "JSON",
            "entity_fbid": self.dataFB['FacebookID']
        }

        if self.syncToken is None:
            topic = "/messenger_sync_create_queue"
            queue["initial_titan_sequence_id"] = self.lastSeqID
            queue["device_params"] = None
        else:
            topic = "/messenger_sync_get_diffs"
            queue["last_seq_id"] = self.lastSeqID
            queue["sync_token"] = self.syncToken

        client.publish(
            topic,
            treo_json_minimal(queue),
            qos=1,
            retain=False,
        )

    def treo_mqtt_connect(self) -> bool:
        """Kết nối đến MQTT server"""
        global treo_cookie_attempts
        
        # Kiểm tra ban
        if treo_cookie_attempts[self.cookie_hash].get('permanent_ban', False):
            return False
            
        current_time = time.time()
        if current_time < treo_cookie_attempts[self.cookie_hash].get('banned_until', 0):
            return False

        # Tạo session
        session_id = random.randint(1, 2 ** 53)
        user = {
            "u": self.dataFB["FacebookID"],
            "s": session_id,
            "chat_on": treo_json_minimal(True),
            "fg": False,
            "d": ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '-' +
                 ''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + '-' +
                 ''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + '-' +
                 ''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + '-' +
                 ''.join(random.choices(string.ascii_lowercase + string.digits, k=12)),
            "ct": "websocket",
            "aid": 219994525426954,
            "mqtt_sid": "",
            "cp": 3,
            "ecp": 10,
            "st": ["/t_ms", "/messenger_sync_get_diffs", "/messenger_sync_create_queue"],
            "pm": [],
            "dc": "",
            "no_auto_fg": True,
            "gas": None,
            "pack": [],
        }

        host = f"wss://edge-chat.messenger.com/chat?region=eag&sid={session_id}"
        options = {
            "client_id": "mqttwsclient",
            "username": treo_json_minimal(user),
            "clean": True,
            "ws_options": {
                "headers": {
                    "Cookie": self.dataFB['cookieFacebook'],
                    "Origin": "https://www.messenger.com",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G973U Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
                    "Referer": "https://www.messenger.com/",
                    "Host": "edge-chat.messenger.com",
                },
            },
            "keepalive": 10,
        }

        # Tạo MQTT client
        self.mqtt = mqtt.Client(
            client_id="mqttwsclient",
            clean_session=True,
            protocol=mqtt.MQTTv31,
            transport="websockets",
        )

        # Cấu hình TLS
        self.mqtt.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.mqtt.on_connect = self._messenger_queue_publish
        self.mqtt.on_disconnect = self.on_disconnect
        self.mqtt.username_pw_set(username=options["username"])

        # Cấu hình WebSocket
        parsed_host = urlparse(host)
        self.mqtt.ws_set_options(
            path=f"{parsed_host.path}?{parsed_host.query}",
            headers=options["ws_options"]["headers"],
        )

        # Kết nối
        try:
            self.mqtt.connect(
                host=options["ws_options"]["headers"]["Host"],
                port=443,
                keepalive=options["keepalive"],
            )

            self.mqtt.loop_start()
            time.sleep(2)
            return True
        except Exception as e:
            treo_cookie_attempts[self.cookie_hash]['count'] = treo_cookie_attempts[self.cookie_hash].get('count', 0) + 1
            return False

    def stop(self):
        """Dừng kết nối"""
        if self.mqtt:
            try:
                self.mqtt.disconnect()
                self.mqtt.loop_stop()
            except:
                pass
        self.cleanup_memory()

    def treo_mqtt_send_message(self, message=None, thread_id=None) -> bool:
        """Gửi tin nhắn qua MQTT"""
        if self.mqtt is None or not self.connected:
            return False

        if not all([message, thread_id]):
            return False

        self.cleanup_memory()
        self.ws_req_number += 1

        # Tạo payload tin nhắn
        task_payload = {
            "thread_id": thread_id,
            "otid": treo_generate_offline_threading_id(),
            "source": 0,
            "send_type": 1,
            "text": message,
            "initiating_source": 1
        }
        
        content = {
            "app_id": "2220391788200892",
            "payload": {
                "tasks": [{
                    "label": 46,
                    "payload": json.dumps(task_payload, separators=(",", ":")),
                    "queue_name": "send_message",
                    "task_id": self.ws_req_number,
                    "failure_count": None,
                }],
                "epoch_id": treo_generate_offline_threading_id(),
                "version_id": "7214102258676893",
            },
            "request_id": self.ws_req_number,
            "type": 3
        }

        content["payload"] = json.dumps(content["payload"], separators=(",", ":"))

        try:
            self.mqtt.publish(
                topic="/ls_req",
                payload=json.dumps(content, separators=(",", ":")),
                qos=1,
                retain=False,
            )
            self.success_count += 1
            self.message_count += 1
            return True
        except Exception:
            return False


def treo_send_messages_task(cookie, thread_id, content, delay, task_id):
    """Task gửi tin nhắn liên tục"""
    global stop_flags, running_tasks, treo_active_threads, treo_cookie_attempts, task_start_times, task_info, task_lock

    cookie_hash = hashlib.md5(cookie.encode()).hexdigest()
    
    print(f"\n🚀 Task #{task_id} đang khởi động...")
    
    # Lưu thông tin task ngay khi bắt đầu
    with task_lock:
        task_start_times[task_id] = time.time()
        running_tasks[task_id] = True
        
        try:
            fb = TreoFacebookAuth(cookie)
            user_id = fb.user_id
            # Cập nhật thông tin user_id nếu đã có trong task_info từ discord bot
            if task_id in task_info:
                task_info[task_id]['iduser'] = user_id
                task_info[task_id]['status'] = 'running'
            else:
                task_info[task_id] = {
                    'idbox': thread_id,
                    'iduser': user_id,
                    'start_time': datetime.now(VIETNAM_TZ).strftime("%H:%M:%S %d/%m/%Y"),
                    'status': 'running',
                    'message': content[:50] + '...' if len(content) > 50 else content
                }
            print(f"✅ Task #{task_id} - Xác thực thành công: {user_id}")
        except Exception as e:
            if task_id in task_info:
                task_info[task_id]['status'] = 'error'
                task_info[task_id]['error'] = str(e)
            else:
                task_info[task_id] = {
                    'idbox': thread_id,
                    'iduser': 'Lỗi xác thực',
                    'start_time': datetime.now(VIETNAM_TZ).strftime("%H:%M:%S %d/%m/%Y"),
                    'error': str(e),
                    'status': 'error'
                }
            print(f"❌ Task #{task_id} - Lỗi xác thực: {e}")
            running_tasks[task_id] = False
            return False

    # Kiểm tra ban
    if treo_cookie_attempts[cookie_hash].get('permanent_ban', False):
        with task_lock:
            task_info[task_id]['status'] = 'banned'
            running_tasks[task_id] = False
        return False

    current_time = time.time()
    if current_time < treo_cookie_attempts[cookie_hash].get('banned_until', 0):
        with task_lock:
            task_info[task_id]['status'] = 'temp_banned'
            running_tasks[task_id] = False
        return False

    try:
        # Xác thực Facebook
        fb = TreoFacebookAuth(cookie)

        # Tạo sender
        sender = TreoMQTTSender({
            "FacebookID": fb.user_id,
            "fb_dtsg": fb.fb_dtsg,
            "clientRevision": fb.rev,
            "jazoest": fb.jazoest,
            "cookieFacebook": cookie,
            "lastSeqID": "0"
        })
        sender.task_id = task_id

        # Kết nối MQTT
        print(f"🔄 Task #{task_id} - Đang kết nối MQTT...")
        if not sender.treo_mqtt_connect():
            treo_handle_failed_connection(cookie_hash)
            with task_lock:
                task_info[task_id]['status'] = 'connection_failed'
                running_tasks[task_id] = False
            return False

        # Lưu sender vào active threads
        key = f"{cookie_hash}_{thread_id}_{task_id}"
        treo_active_threads[key] = sender
        
        print(f"✅ Task #{task_id} - Đã kết nối và bắt đầu gửi tin...")
        print(f"📝 Nội dung: {content[:100]}...")
        print(f"⏱️ Delay: {delay}s")

        # Gửi tin nhắn liên tục
        message_count = 0
        last_status_update = time.time()
        
        while True:
            # Kiểm tra stop flag
            if stop_flags.get(task_id, False):
                print(f"⏹️ Task #{task_id} nhận tín hiệu dừng")
                break
                
            # Kiểm tra xem task còn trong running_tasks không
            with task_lock:
                if task_id not in running_tasks or not running_tasks[task_id]:
                    print(f"⚠️ Task #{task_id} không còn trong running_tasks")
                    break
            
            # Gửi tin nhắn
            if sender.treo_mqtt_send_message(content, thread_id):
                message_count += 1
                
                # Cập nhật status mỗi 30 giây
                current_time = time.time()
                if current_time - last_status_update > 30:
                    with task_lock:
                        if task_id in task_info:
                            task_info[task_id]['message_count'] = message_count
                            task_info[task_id]['last_message'] = datetime.now(VIETNAM_TZ).strftime("%H:%M:%S")
                    last_status_update = current_time
                    
                if message_count % 10 == 0:
                    print(f"📨 Task #{task_id} đã gửi {message_count} tin")

            # Delay
            for i in range(delay):
                if stop_flags.get(task_id, False):
                    break
                time.sleep(1)

        with task_lock:
            if task_id in task_info:
                task_info[task_id]['status'] = 'stopped'
                task_info[task_id]['message_count'] = message_count
                task_info[task_id]['stop_time'] = datetime.now(VIETNAM_TZ).strftime("%H:%M:%S %d/%m/%Y")

    except Exception as e:
        print(f"❌ Lỗi task {task_id}: {e}")
        with task_lock:
            if task_id in task_info:
                task_info[task_id]['status'] = 'error'
                task_info[task_id]['error'] = str(e)
        treo_handle_failed_connection(cookie_hash)
    
    finally:
        # Dọn dẹp
        print(f"✅ Task #{task_id} kết thúc - Đã gửi {message_count if 'message_count' in locals() else 0} tin")
        if 'sender' in locals():
            sender.stop()
        if key in treo_active_threads:
            del treo_active_threads[key]
        
        with task_lock:
            if task_id in running_tasks:
                del running_tasks[task_id]
            stop_flags.pop(task_id, None)

    return True


def load_messages_from_file(filename):
    """Đọc tin nhắn từ file - tất cả các dòng gộp thành MỘT tin nhắn"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Lọc bỏ dòng trống và comment
            valid_lines = []
            for line in lines:
                line = line.rstrip('\n\r')
                if line and not line.startswith('#'):
                    valid_lines.append(line)
            
            if not valid_lines:
                print("❌ File không có nội dung hợp lệ")
                return []
            
            # Gộp tất cả thành một tin
            content = '\n'.join(valid_lines)
            return [content]
            
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {filename}")
        return []
    except Exception as e:
        print(f"❌ Lỗi đọc file: {e}")
        return []


def format_uptime(seconds):
    """Định dạng thời gian uptime"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"