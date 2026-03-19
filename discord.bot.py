#!/usr/bin/env python3
# discord_bot.py - TREO BOT PRO MAX EDITION
import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import time
import random
import string
import hashlib
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pytz

# Import từ treo_core
from treo_core import (
    treo_send_messages_task, load_messages_from_file,
    running_tasks, stop_flags, task_counter, task_info, task_start_times,
    format_uptime, TreoFacebookAuth, treo_handle_failed_connection
)

# ==================== CẤU HÌNH ====================
TOKEN = "MTQ4MjIxNTkzNzEzMzUxNDc2Mg.GbIEw6.2Bueo6tOMlFUDCFA2Lue9PU0g-fzGJflcsIstk"  # Thay token của bạn
ADMIN_IDS = [1153524502630760498]  # Thay ID Discord admin

# Timezone Việt Nam
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# File lưu trữ
KEYS_FILE = "keys.json"
USER_SESSIONS_FILE = "user_sessions.json"

# Banner
BANNER_URL = "https://raw.githubusercontent.com/datzk25/file/refs/heads/main/D%E1%BB%B1%20%C3%A1n%20m%E1%BB%9Bi%2066%20Copy%202%20Copy%20Copy%20%5BBE98E2E%5D.png"
QR_URL = "https://raw.githubusercontent.com/datzk25/file/refs/heads/main/D%E1%BB%B1%20%C3%A1n%20m%E1%BB%9Bi%2066%20Copy%202%20Copy%20Copy%20%5BBE98E2E%5D.png"# Thay link QR

# Màu sắc
COLORS = {
    "primary": 0x5865F2,
    "success": 0x57F287,
    "warning": 0xFEE75C,
    "danger": 0xED4245,
    "vip": 0x9B59B6,
    "info": 0x3498DB,
    "gold": 0xF1C40F
}

# ==================== CLASS QUẢN LÝ SESSION ====================
class SessionManager:
    def __init__(self):
        self.sessions = self.load_sessions()
        self.active_keys = {}
    
    def load_sessions(self):
        try:
            if os.path.exists(USER_SESSIONS_FILE):
                with open(USER_SESSIONS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            return {}
        return {}
    
    def save_sessions(self):
        try:
            with open(USER_SESSIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def login(self, user_id: str, key: str, key_data: dict):
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        
        self.sessions[user_id] = {
            "key": key,
            "key_data": key_data,
            "login_time": datetime.now(VIETNAM_TZ).isoformat(),
            "last_used": datetime.now(VIETNAM_TZ).isoformat()
        }
        
        self.active_keys[key] = user_id
        self.save_sessions()
    
    def logout(self, user_id: str):
        if user_id in self.sessions:
            key = self.sessions[user_id].get("key")
            if key and key in self.active_keys:
                del self.active_keys[key]
            del self.sessions[user_id]
            self.save_sessions()
            return True
        return False
    
    def get_session(self, user_id: str):
        return self.sessions.get(user_id)
    
    def is_logged_in(self, user_id: str):
        return user_id in self.sessions
    
    def get_user_by_key(self, key: str):
        return self.active_keys.get(key)
    
    def force_logout_by_key(self, key: str):
        """Đăng xuất user đang dùng key"""
        user_id = self.active_keys.get(key)
        if user_id:
            return self.logout(user_id)
        return False

# ==================== CLASS QUẢN LÝ KEY ====================
class KeyManager:
    def __init__(self):
        self.keys = self.load_keys()
    
    def load_keys(self):
        try:
            if os.path.exists(KEYS_FILE):
                with open(KEYS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            return {}
        return {}
    
    def save_keys(self):
        try:
            with open(KEYS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.keys, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def generate_key(self, days_valid=30, key_type="basic"):
        def random_segment(length=5):
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        type_map = {"basic": "BASIC", "pro": "PRO", "vip": "VIP", "unlimited": "ULTRA"}
        key_type_code = type_map.get(key_type, "BASIC")
        key = f"TREO-{key_type_code}-{random_segment()}-{random_segment()}-{random_segment()}"
        
        expiry_date = datetime.now(VIETNAM_TZ) + timedelta(days=days_valid)
        
        message_limits = {"basic": 2000, "pro": 5000, "vip": 10000, "unlimited": 50000}
        max_tasks = {"basic": 1, "pro": 3, "vip": 5, "unlimited": 999}
        prices = {"basic": "50k", "pro": "100k", "vip": "200k", "unlimited": "500k"}
        
        self.keys[key] = {
            "created": datetime.now(VIETNAM_TZ).isoformat(),
            "expiry": expiry_date.isoformat(),
            "used_by": None,
            "used_at": None,
            "banned": False,
            "banned_reason": None,
            "banned_at": None,
            "days_valid": days_valid,
            "type": key_type,
            "message_limit": message_limits.get(key_type, 2000),
            "max_tasks": max_tasks.get(key_type, 1),
            "price": prices.get(key_type, "50k")
        }
        self.save_keys()
        return key, expiry_date
    
    def validate_key(self, key, discord_id):
        if key not in self.keys:
            return False, "KEY_NOT_EXISTS", None
        
        data = self.keys[key]
        
        if data.get("banned"):
            return False, "KEY_BANNED", data
        
        try:
            expiry = datetime.fromisoformat(data["expiry"])
            if expiry.tzinfo is None:
                expiry = VIETNAM_TZ.localize(expiry)
            if expiry < datetime.now(VIETNAM_TZ):
                return False, "KEY_EXPIRED", data
        except:
            return False, "KEY_INVALID", data
        
        if data["used_by"] and data["used_by"] != str(discord_id):
            return False, "KEY_USED", data
        
        return True, "KEY_VALID", data
    
    def ban_key(self, key: str, reason: str = None):
        if key in self.keys:
            self.keys[key]["banned"] = True
            self.keys[key]["banned_reason"] = reason
            self.keys[key]["banned_at"] = datetime.now(VIETNAM_TZ).isoformat()
            self.save_keys()
            return True
        return False
    
    def unban_key(self, key: str):
        if key in self.keys:
            self.keys[key]["banned"] = False
            self.keys[key]["banned_reason"] = None
            self.keys[key]["banned_at"] = None
            self.save_keys()
            return True
        return False
    
    def delete_key(self, key: str):
        if key in self.keys:
            del self.keys[key]
            self.save_keys()
            return True
        return False
    
    def get_key_info(self, key: str):
        return self.keys.get(key)
    
    def list_keys(self, show_all=False):
        keys_list = []
        for key, data in self.keys.items():
            if not show_all and data.get("banned"):
                continue
            
            status = "✅" if not data.get("banned") else "❌"
            used_by = data.get("used_by", "Chưa sd")
            key_type = data.get('type', 'basic').upper()
            
            try:
                expiry = datetime.fromisoformat(data["expiry"])
                if expiry.tzinfo is None:
                    expiry = VIETNAM_TZ.localize(expiry)
                expiry_str = expiry.strftime("%d/%m/%Y")
                days_left = (expiry - datetime.now(VIETNAM_TZ)).days
            except:
                expiry_str = "N/A"
                days_left = 0
            
            keys_list.append({
                "key": key,
                "status": status,
                "type": key_type,
                "expiry": expiry_str,
                "days_left": days_left,
                "used_by": used_by,
                "banned": data.get("banned", False)
            })
        
        return keys_list

# Khởi tạo managers
key_manager = KeyManager()
session_manager = SessionManager()

# ==================== CLASS HIỂN THỊ ====================
class BeautifulEmbeds:
    @staticmethod
    def get_time():
        return datetime.now(VIETNAM_TZ).strftime("%H:%M • %d/%m/%Y")
    
    @staticmethod
    def success(title, description):
        embed = discord.Embed(
            title=f"✅ **{title}**",
            description=description,
            color=COLORS["success"],
            timestamp=datetime.now(VIETNAM_TZ)
        )
        embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
        return embed
    
    @staticmethod
    def error(title, description):
        embed = discord.Embed(
            title=f"❌ **{title}**",
            description=description,
            color=COLORS["danger"],
            timestamp=datetime.now(VIETNAM_TZ)
        )
        embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
        return embed
    
    @staticmethod
    def info(title, description):
        embed = discord.Embed(
            title=f"ℹ️ **{title}**",
            description=description,
            color=COLORS["info"],
            timestamp=datetime.now(VIETNAM_TZ)
        )
        embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
        return embed
    
    @staticmethod
    def warning(title, description):
        embed = discord.Embed(
            title=f"⚠️ **{title}**",
            description=description,
            color=COLORS["warning"],
            timestamp=datetime.now(VIETNAM_TZ)
        )
        embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
        return embed

# ==================== MODAL ĐĂNG NHẬP ====================
class LoginModal(discord.ui.Modal, title="🔐 ĐĂNG NHẬP TREO BOT"):
    def __init__(self):
        super().__init__()
        
        self.key_input = discord.ui.TextInput(
            label="🔑 KEY KÍCH HOẠT",
            placeholder="Nhập key của bạn)",
            style=discord.TextStyle.short,
            required=True,
            max_length=50
        )
        self.add_item(self.key_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        key = self.key_input.value.strip().upper()
        
        # Kiểm tra key
        valid, code, key_data = key_manager.validate_key(key, str(interaction.user.id))
        
        if not valid:
            if code == "KEY_NOT_EXISTS":
                embed = BeautifulEmbeds.error(
                    "KEY KHÔNG TỒN TẠI",
                    f"❌ Key `{key}` không có trong hệ thống!\n\n"
                    f"💡 **MUA KEY NGAY**\n"
                    f"```diff\n"
                    f"+ BASIC  (30 ngày): 50k  - 2000 từ/tin - 1 task\n"
                    f"+ PRO    (30 ngày): 100k - 5000 từ/tin - 3 tasks\n"
                    f"+ VIP    (30 ngày): 200k - 10000 từ/tin - 5 tasks\n"
                    f"+ ULTRA  (30 ngày): 500k - 50000 từ/tin - ∞ tasks\n"
                    f"```"
                )
            elif code == "KEY_EXPIRED":
                embed = BeautifulEmbeds.error(
                    "KEY HẾT HẠN",
                    f"❌ Key `{key}` đã hết hạn sử dụng!\n\n💡 Vui lòng gia hạn key."
                )
            elif code == "KEY_USED":
                user_id = key_data.get('used_by', 'N/A')
                embed = BeautifulEmbeds.error(
                    "KEY ĐÃ ĐƯỢC SỬ DỤNG",
                    f"❌ Key này đang được sử dụng bởi <@{user_id}>!\n\n"
                    f"💡 Mỗi key chỉ dùng cho 1 người duy nhất."
                )
            elif code == "KEY_BANNED":
                reason = key_data.get('banned_reason', 'Không rõ lý do')
                embed = BeautifulEmbeds.error(
                    "KEY ĐÃ BỊ BAN",
                    f"❌ Key `{key}` đã bị ban khỏi hệ thống!\n"
                    f"📝 Lý do: `{reason}`\n\n"
                    f"💡 Liên hệ admin để biết thêm chi tiết."
                )
            else:
                embed = BeautifulEmbeds.error("LỖI", "Key không hợp lệ!")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Đăng nhập thành công
        session_manager.login(str(interaction.user.id), key, key_data)
        
        # Tính thời gian còn lại
        expiry = datetime.fromisoformat(key_data["expiry"])
        if expiry.tzinfo is None:
            expiry = VIETNAM_TZ.localize(expiry)
        days_left = (expiry - datetime.now(VIETNAM_TZ)).days
        
        # Gửi banner
        banner_embed = discord.Embed(
            title="🎯 **TREO BOT PRO MAX**",
            description="```\nĐĂNG NHẬP THÀNH CÔNG\n```",
            color=COLORS["success"]
        )
        banner_embed.set_image(url=BANNER_URL)
        await interaction.followup.send(embed=banner_embed, ephemeral=True)
        
        # Gửi thông tin key
        embed = discord.Embed(
            title="🎉 **ĐĂNG NHẬP THÀNH CÔNG**",
            color=COLORS["success"],
            timestamp=datetime.now(VIETNAM_TZ)
        )
        
        embed.add_field(
            name="📋 **THÔNG TIN KEY**",
            value=f"```yaml\n"
                  f"Key: {key[:20]}...{key[-10:]}\n"
                  f"Loại: {key_data.get('type', 'basic').upper()}\n"
                  f"Hạn: {expiry.strftime('%d/%m/%Y')}\n"
                  f"Còn: {days_left} ngày\n"
                  f"Giới hạn: {key_data.get('message_limit')} từ/tin\n"
                  f"Max tasks: {key_data.get('max_tasks')}\n"
                  f"```",
            inline=False
        )
        
        embed.add_field(
            name="📌 **HƯỚNG DẪN**",
            value="• Dùng `/send` để gửi tin nhắn\n"
                  "• Dùng `/tab` để xem dashboard\n"
                  "• Dùng `/logout` để đăng xuất",
            inline=False
        )
        
        embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()} • User: {interaction.user.name}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

# ==================== MODAL GỬI TIN ====================
class SendModal(discord.ui.Modal, title="📨 GỬI TIN NHẮN"):
    def __init__(self, session):
        super().__init__()
        self.session = session
        key_data = session.get("key_data", {})
        
        self.cookie = discord.ui.TextInput(
            label="🍪 COOKIE FACEBOOK",
            placeholder="c_user=xxxx; xs=xxxx;...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )
        
        self.idbox = discord.ui.TextInput(
            label="📦 ID BOX / THREAD",
            placeholder="Nhập ID box cần gửi tin...",
            required=True,
            max_length=50
        )
        
        limit = key_data.get('message_limit', 2000)
        self.message = discord.ui.TextInput(
            label=f"💬 NỘI DUNG (Tối đa: {limit} ký tự)",
            placeholder="Nhập nội dung tin nhắn...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=limit
        )
        
        self.delay = discord.ui.TextInput(
            label="⏱️ DELAY (GIÂY)",
            placeholder="Khoảng cách giữa các lần gửi",
            required=False,
            default="5",
            max_length=3
        )
        
        self.add_item(self.cookie)
        self.add_item(self.idbox)
        self.add_item(self.message)
        self.add_item(self.delay)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        key_data = self.session.get("key_data", {})
        
        # Kiểm tra key còn hạn không
        try:
            expiry = datetime.fromisoformat(key_data.get("expiry", ""))
            if expiry.tzinfo is None:
                expiry = VIETNAM_TZ.localize(expiry)
            if expiry < datetime.now(VIETNAM_TZ):
                session_manager.logout(str(interaction.user.id))
                embed = BeautifulEmbeds.error(
                    "KEY HẾT HẠN",
                    "❌ Key của bạn đã hết hạn! Vui lòng đăng nhập lại với key mới."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            pass
        
        # Kiểm tra số lượng task
        user_tasks = [tid for tid in running_tasks 
                     if task_info.get(tid, {}).get('user') == str(interaction.user.id)]
        
        max_tasks = key_data.get('max_tasks', 1)
        if len(user_tasks) >= max_tasks:
            embed = BeautifulEmbeds.error(
                "GIỚI HẠN TASK",
                f"❌ Bạn chỉ được chạy tối đa **{max_tasks}** task cùng lúc!\n"
                f"📊 Hiện tại: **{len(user_tasks)}/{max_tasks}** task"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        try:
            delay = int(self.delay.value or "5")
            if delay < 1:
                delay = 5
        except:
            delay = 5
        
        # Kiểm tra cookie
        try:
            fb = TreoFacebookAuth(self.cookie.value)
            user_id = fb.user_id
        except Exception as e:
            embed = BeautifulEmbeds.error(
                "LỖI COOKIE",
                f"❌ Cookie không hợp lệ!\n📝 Lỗi: `{str(e)}`"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Tạo task
        global task_counter
        task_counter += 1
        task_id = task_counter
        
        task_info[task_id] = {
            'idbox': self.idbox.value,
            'iduser': user_id,
            'start_time': datetime.now(VIETNAM_TZ).strftime("%H:%M:%S %d/%m/%Y"),
            'user': str(interaction.user.id),
            'user_name': str(interaction.user),
            'key': self.session.get('key'),
            'key_type': key_data.get('type', 'basic'),
            'status': 'running'
        }
        
        # Chạy task
        thread = threading.Thread(
            target=treo_send_messages_task,
            args=(self.cookie.value, self.idbox.value, self.message.value, delay, task_id),
            daemon=True
        )
        thread.start()
        
        # Embed thành công
        embed = discord.Embed(
            title="🚀 **TASK ĐÃ KHỞI ĐỘNG**",
            color=COLORS["success"],
            timestamp=datetime.now(VIETNAM_TZ)
        )
        
        embed.add_field(name="🆔 TASK ID", value=f"`#{task_id}`", inline=True)
        embed.add_field(name="📦 ID BOX", value=f"`{self.idbox.value}`", inline=True)
        embed.add_field(name="👤 FB USER", value=f"`{user_id}`", inline=True)
        embed.add_field(name="⏱️ DELAY", value=f"`{delay}s`", inline=True)
        embed.add_field(name="🔑 KEY", value=f"`{key_data.get('type', 'basic').upper()}`", inline=True)
        
        embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
        
        await interaction.followup.send(embed=embed)

# ==================== BOT ====================
class TreoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Đã sync lệnh!")

bot = TreoBot()

# ==================== TASKS ====================
@tasks.loop(minutes=5)
async def cleanup_sessions():
    """Dọn dẹp sessions hết hạn mỗi 5 phút"""
    now = datetime.now(VIETNAM_TZ)
    expired = []
    
    for user_id, session in session_manager.sessions.items():
        key_data = session.get("key_data", {})
        try:
            expiry = datetime.fromisoformat(key_data.get("expiry", ""))
            if expiry.tzinfo is None:
                expiry = VIETNAM_TZ.localize(expiry)
            if expiry < now:
                expired.append(user_id)
        except:
            expired.append(user_id)
    
    for user_id in expired:
        session_manager.logout(user_id)

# ==================== DASHBOARD VIEW ====================
class DashboardView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id
    
    @discord.ui.button(label="🔄 REFRESH", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        await tab(interaction)
    
    @discord.ui.button(label="⏹️ STOP TASK", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        
        # Hiển thị modal chọn task để stop
        modal = StopTaskModal(self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ ĐÓNG", style=discord.ButtonStyle.secondary)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        await interaction.response.edit_message(content="✅ **ĐÃ ĐÓNG DASHBOARD**", embed=None, view=None)

class StopTaskModal(discord.ui.Modal, title="⏹️ DỪNG TASK"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        self.task_id = discord.ui.TextInput(
            label="🔢 TASK ID",
            placeholder="Nhập ID task cần dừng...",
            required=True,
            max_length=10
        )
        self.add_item(self.task_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            tid = int(self.task_id.value)
            
            if tid not in running_tasks:
                embed = BeautifulEmbeds.error("LỖI", f"❌ Task #{tid} không tồn tại!")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            info = task_info.get(tid, {})
            if str(interaction.user.id) != info.get('user') and interaction.user.id not in ADMIN_IDS:
                embed = BeautifulEmbeds.error("LỖI", "❌ Bạn không có quyền dừng task này!")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            stop_flags[tid] = True
            
            embed = BeautifulEmbeds.success(
                "ĐÃ GỬI TÍN HIỆU DỪNG",
                f"✅ **Task #{tid}** sẽ dừng sau vài giây..."
            )
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            embed = BeautifulEmbeds.error("LỖI", "❌ Task ID không hợp lệ!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

# ==================== COMMANDS USER ====================
@bot.tree.command(name="login", description="🔐 Đăng nhập với key")
async def login(interaction: discord.Interaction):
    """Đăng nhập để sử dụng bot"""
    
    if session_manager.is_logged_in(str(interaction.user.id)):
        embed = BeautifulEmbeds.warning(
            "ĐÃ ĐĂNG NHẬP",
            "⚠️ Bạn đã đăng nhập rồi!\n\n"
            "• Dùng `/logout` để đăng xuất\n"
            "• Dùng `/send` để gửi tin nhắn\n"
            "• Dùng `/tab` để xem dashboard"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.send_modal(LoginModal())

@bot.tree.command(name="logout", description="🚪 Đăng xuất")
async def logout(interaction: discord.Interaction):
    """Đăng xuất khỏi hệ thống"""
    
    if not session_manager.is_logged_in(str(interaction.user.id)):
        embed = BeautifulEmbeds.error(
            "CHƯA ĐĂNG NHẬP",
            "❌ Bạn chưa đăng nhập!\n\n💡 Dùng `/login` để đăng nhập."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Dừng tất cả task
    user_tasks = [tid for tid in running_tasks 
                 if task_info.get(tid, {}).get('user') == str(interaction.user.id)]
    
    for task_id in user_tasks:
        stop_flags[task_id] = True
    
    # Đăng xuất
    session_manager.logout(str(interaction.user.id))
    
    embed = BeautifulEmbeds.success(
        "ĐĂNG XUẤT THÀNH CÔNG",
        f"✅ Đã dừng **{len(user_tasks)}** task và đăng xuất."
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="send", description="📨 Gửi tin nhắn tự động")
async def send(interaction: discord.Interaction):
    """Gửi tin nhắn (cần đăng nhập)"""
    
    session = session_manager.get_session(str(interaction.user.id))
    if not session:
        embed = BeautifulEmbeds.error(
            "CHƯA ĐĂNG NHẬP",
            "❌ Bạn cần đăng nhập để sử dụng lệnh này!\n\n💡 Dùng `/login` để đăng nhập."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.send_modal(SendModal(session))

@bot.tree.command(name="tab", description="📊 Xem dashboard")
async def tab(interaction: discord.Interaction):
    """Xem dashboard cá nhân"""
    
    session = session_manager.get_session(str(interaction.user.id))
    
    # Lọc tasks của user
    user_tasks = []
    current_time = time.time()
    
    for tid in running_tasks:
        info = task_info.get(tid, {})
        if info.get('user') == str(interaction.user.id):
            uptime = current_time - task_start_times.get(tid, current_time)
            user_tasks.append((tid, info, uptime))
    
    # Tạo embed
    embed = discord.Embed(
        title=f"📊 **DASHBOARD • {interaction.user.name}**",
        description=f"```\n{'═'*40}\n```",
        color=COLORS["primary"] if session else COLORS["danger"],
        timestamp=datetime.now(VIETNAM_TZ)
    )
    
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_image(url=BANNER_URL)
    
    if session:
        key_data = session.get("key_data", {})
        key = session.get("key", "N/A")
        key_type = key_data.get('type', 'basic').upper()
        
        try:
            expiry = datetime.fromisoformat(key_data.get("expiry", ""))
            if expiry.tzinfo is None:
                expiry = VIETNAM_TZ.localize(expiry)
            days_left = (expiry - datetime.now(VIETNAM_TZ)).days
            expiry_str = expiry.strftime("%d/%m/%Y")
        except:
            days_left = 0
            expiry_str = "N/A"
        
        embed.add_field(
            name="🔑 **THÔNG TIN KEY**",
            value=f"```yaml\n"
                  f"Key: {key[:15]}...{key[-10:]}\n"
                  f"Loại: {key_type}\n"
                  f"HSD: {expiry_str}\n"
                  f"Còn: {days_left} ngày\n"
                  f"Giới hạn: {key_data.get('message_limit')} từ\n"
                  f"Max tasks: {key_data.get('max_tasks')}\n"
                  f"```",
            inline=False
        )
    else:
        embed.add_field(
            name="⚠️ **CHƯA ĐĂNG NHẬP**",
            value="💡 Dùng `/login` để đăng nhập",
            inline=False
        )
    
    if user_tasks:
        tasks_text = ""
        for i, (tid, info, uptime) in enumerate(user_tasks[:5], 1):
            tasks_text += f"**Task #{tid}**\n"
            tasks_text += f"┣ 📦 Box: `{info.get('idbox', 'N/A')}`\n"
            tasks_text += f"┣ ⏱️ Uptime: `{format_uptime(uptime)}`\n"
            tasks_text += f"┗ 🔑 Key: `{info.get('key_type', 'basic').upper()}`\n\n"
        
        embed.add_field(
            name=f"📋 **TASKS ĐANG CHẠY ({len(user_tasks)})**",
            value=tasks_text,
            inline=False
        )
    else:
        embed.add_field(
            name="📭 **KHÔNG CÓ TASK**",
            value="Hiện tại bạn chưa có task nào đang chạy.",
            inline=False
        )
    
    embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
    
    # View với buttons
    view = DashboardView(str(interaction.user.id))
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="shop", description="🛒 Xem bảng giá")
async def shop(interaction: discord.Interaction):
    """Xem bảng giá và mua key"""
    
    embed = discord.Embed(
        title="🛒 **TREO BOT SHOP**",
        description="```\nMUA KEY - THANH TOÁN QR\n```",
        color=COLORS["gold"],
        timestamp=datetime.now(VIETNAM_TZ)
    )
    
    embed.set_image(url=QR_URL)
    
    pricing = (
        "```diff\n"
        "+ BASIC  (30 ngày): 50,000đ\n"
        "  • 2000 ký tự/tin • 1 task\n"
        "+ PRO    (30 ngày): 100,000đ\n"
        "  • 5000 ký tự/tin • 3 tasks\n"
        "+ VIP    (30 ngày): 200,000đ\n"
        "  • 10000 ký tự/tin • 5 tasks\n"
        "+ ULTRA  (30 ngày): 500,000đ\n"
        "  • 50000 ký tự/tin • ∞ tasks\n"
        "```"
    )
    
    embed.add_field(name="💰 **BẢNG GIÁ**", value=pricing, inline=False)
    embed.add_field(
        name="📞 **LIÊN HỆ MUA KEY**",
        value=f"👑 Admin: <@{ADMIN_IDS[0] if ADMIN_IDS else 'ADMIN'}>\n"
              f"💬 Chat riêng để được hỗ trợ",
        inline=False
    )
    
    embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="📚 Hướng dẫn")
async def help(interaction: discord.Interaction):
    """Hướng dẫn sử dụng"""
    
    embed = discord.Embed(
        title="📚 **HƯỚNG DẪN SỬ DỤNG**",
        description=f"```\n{'═'*40}\n```",
        color=COLORS["info"],
        timestamp=datetime.now(VIETNAM_TZ)
    )
    
    embed.set_thumbnail(url="https://raw.githubusercontent.com/datzk25/file/refs/heads/main/discord_fake_avatar_decorations_1773912580803.gif")
    embed.set_image(url=BANNER_URL)
    
    user_commands = (
        "```css\n"
        "[🔐] /login   - Đăng nhập với key\n"
        "[📨] /send    - Gửi tin nhắn tự động\n"
        "[📊] /tab     - Xem dashboard cá nhân\n"
        "[🚪] /logout  - Đăng xuất\n"
        "[🛒] /shop    - Xem bảng giá\n"
        "[📚] /help    - Hướng dẫn này\n"
        "```"
    )
    
    embed.add_field(name="👤 **LỆNH CHO USER**", value=user_commands, inline=False)
    
    if interaction.user.id in ADMIN_IDS:
        admin_commands = (
            "```css\n"
            "[👑] /createkey [days] [type] - Tạo key mới\n"
            "[📋] /keys [show_all] - Danh sách keys\n"
            "[🔨] /bankey [key] [reason] - Ban key\n"
            "[🔓] /unbankey [key] - Bỏ ban key\n"
            "[❌] /deletekey [key] - Xóa key vĩnh viễn\n"
            "[🔍] /keyinfo [key] - Xem chi tiết key\n"
            "```"
        )
        embed.add_field(name="👑 **LỆNH ADMIN**", value=admin_commands, inline=False)
    
    embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
    
    await interaction.response.send_message(embed=embed)

# ==================== ADMIN COMMANDS ====================
@bot.tree.command(name="createkey", description="[ADMIN] Tạo key mới")
@app_commands.describe(days="Số ngày hiệu lực", key_type="Loại key (basic/pro/vip/unlimited)")
async def createkey(interaction: discord.Interaction, days: int = 30, key_type: str = "basic"):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌", ephemeral=True)
        return
    
    if key_type not in ["basic", "pro", "vip", "unlimited"]:
        key_type = "basic"
    
    key, expiry = key_manager.generate_key(days, key_type)
    
    embed = discord.Embed(
        title="🔑 **KEY MỚI ĐÃ ĐƯỢC TẠO**",
        color=COLORS["success"],
        timestamp=datetime.now(VIETNAM_TZ)
    )
    
    embed.add_field(name="**KEY**", value=f"`{key}`", inline=False)
    embed.add_field(name="**LOẠI**", value=f"`{key_type.upper()}`", inline=True)
    embed.add_field(name="**HẠN**", value=f"`{days} ngày`", inline=True)
    embed.add_field(name="**HẾT HẠN**", value=f"`{expiry.strftime('%d/%m/%Y')}`", inline=True)
    
    embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()} • Admin: {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="keys", description="[ADMIN] Danh sách keys")
@app_commands.describe(show_all="Hiển thị cả key đã ban?")
async def keys(interaction: discord.Interaction, show_all: bool = False):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌", ephemeral=True)
        return
    
    keys_list = key_manager.list_keys(show_all)
    
    if not keys_list:
        await interaction.response.send_message("📭 Chưa có key nào!", ephemeral=True)
        return
    
    # Tạo embed cho từng trang
    chunks = [keys_list[i:i+10] for i in range(0, len(keys_list), 10)]
    
    for i, chunk in enumerate(chunks):
        embed = discord.Embed(
            title=f"📋 **DANH SÁCH KEYS** (Trang {i+1}/{len(chunks)})",
            description="```\n" + "═"*40 + "\n```",
            color=COLORS["info"],
            timestamp=datetime.now(VIETNAM_TZ)
        )
        
        for key_info in chunk:
            status_emoji = key_info["status"]
            ban_status = " (BANNED)" if key_info["banned"] else ""
            embed.add_field(
                name=f"{status_emoji} **{key_info['type']}**{ban_status}",
                value=f"```yaml\n"
                      f"Key: {key_info['key']}\n"
                      f"HSD: {key_info['expiry']} (còn {key_info['days_left']} ngày)\n"
                      f"User: {key_info['used_by']}\n"
                      f"```",
                inline=False
            )
        
        embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()} • Tổng: {len(keys_list)} keys")
        
        if i == 0:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)

@bot.tree.command(name="bankey", description="[ADMIN] Ban key")
@app_commands.describe(key="Key cần ban", reason="Lý do ban")
async def bankey(interaction: discord.Interaction, key: str, reason: str = "Vi phạm điều khoản"):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌", ephemeral=True)
        return
    
    key_data = key_manager.get_key_info(key)
    if not key_data:
        await interaction.response.send_message("❌ Key không tồn tại!", ephemeral=True)
        return
    
    # Ban key
    key_manager.ban_key(key, reason)
    
    # Logout user đang dùng key
    user_id = session_manager.get_user_by_key(key)
    if user_id:
        session_manager.logout(user_id)
        
        # Dừng tasks của user
        for tid in list(running_tasks.keys()):
            if task_info.get(tid, {}).get('user') == user_id:
                stop_flags[tid] = True
    
    embed = BeautifulEmbeds.success(
        "ĐÃ BAN KEY",
        f"✅ **Key:** `{key}`\n"
        f"📝 **Lý do:** `{reason}`\n"
        f"👤 **User:** {f'<@{user_id}>' if user_id else 'Chưa sử dụng'}"
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unbankey", description="[ADMIN] Bỏ ban key")
@app_commands.describe(key="Key cần bỏ ban")
async def unbankey(interaction: discord.Interaction, key: str):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌", ephemeral=True)
        return
    
    if key_manager.unban_key(key):
        embed = BeautifulEmbeds.success(
            "ĐÃ BỎ BAN KEY",
            f"✅ Key `{key}` đã được bỏ ban thành công!"
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Key không tồn tại!", ephemeral=True)

@bot.tree.command(name="deletekey", description="[ADMIN] Xóa key vĩnh viễn")
@app_commands.describe(key="Key cần xóa")
async def deletekey(interaction: discord.Interaction, key: str):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌", ephemeral=True)
        return
    
    # Kiểm tra key có đang được sử dụng không
    user_id = session_manager.get_user_by_key(key)
    if user_id:
        session_manager.logout(user_id)
        
        # Dừng tasks
        for tid in list(running_tasks.keys()):
            if task_info.get(tid, {}).get('user') == user_id:
                stop_flags[tid] = True
    
    if key_manager.delete_key(key):
        embed = BeautifulEmbeds.success(
            "ĐÃ XÓA KEY",
            f"✅ Key `{key}` đã được xóa vĩnh viễn khỏi hệ thống!"
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Key không tồn tại!", ephemeral=True)

@bot.tree.command(name="keyinfo", description="[ADMIN] Xem chi tiết key")
@app_commands.describe(key="Key cần xem thông tin")
async def keyinfo(interaction: discord.Interaction, key: str):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌", ephemeral=True)
        return
    
    data = key_manager.get_key_info(key)
    if not data:
        await interaction.response.send_message("❌ Key không tồn tại!", ephemeral=True)
        return
    
    try:
        created = datetime.fromisoformat(data["created"])
        if created.tzinfo is None:
            created = VIETNAM_TZ.localize(created)
        
        expiry = datetime.fromisoformat(data["expiry"])
        if expiry.tzinfo is None:
            expiry = VIETNAM_TZ.localize(expiry)
        
        days_left = (expiry - datetime.now(VIETNAM_TZ)).days
        
        if data.get("banned_at"):
            banned_at = datetime.fromisoformat(data["banned_at"])
            if banned_at.tzinfo is None:
                banned_at = VIETNAM_TZ.localize(banned_at)
            banned_at_str = banned_at.strftime("%H:%M %d/%m/%Y")
        else:
            banned_at_str = "Chưa ban"
        
    except:
        created_str = "N/A"
        expiry_str = "N/A"
        days_left = 0
        banned_at_str = "N/A"
    
    embed = discord.Embed(
        title=f"🔍 **CHI TIẾT KEY**",
        color=COLORS["info"] if not data.get("banned") else COLORS["danger"],
        timestamp=datetime.now(VIETNAM_TZ)
    )
    
    status = "✅ ACTIVE" if not data.get("banned") else f"❌ BANNED ({data.get('banned_reason', 'N/A')})"
    
    embed.add_field(name="**KEY**", value=f"`{key}`", inline=False)
    embed.add_field(name="**TRẠNG THÁI**", value=status, inline=True)
    embed.add_field(name="**LOẠI**", value=data.get('type', 'basic').upper(), inline=True)
    embed.add_field(name="**HẠN**", value=f"{data.get('days_valid')} ngày", inline=True)
    embed.add_field(name="**NGÀY TẠO**", value=created.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="**HẾT HẠN**", value=expiry.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="**CÒN LẠI**", value=f"{days_left} ngày", inline=True)
    embed.add_field(name="**NGƯỜI DÙNG**", value=f"<@{data.get('used_by')}>" if data.get("used_by") else "Chưa sử dụng", inline=True)
    embed.add_field(name="**BANNED AT**", value=banned_at_str, inline=True)
    
    embed.set_footer(text=f"🕒 {BeautifulEmbeds.get_time()}")
    
    await interaction.response.send_message(embed=embed)

# ==================== ON_READY ====================
@bot.event
async def on_ready():
    print(f"""
    ╔════════════════════════════════════╗
    ║     TREO BOT PRO MAX EDITION       ║
    ╠════════════════════════════════════╣
    ║ Bot: {bot.user.name}
    ║ ID: {bot.user.id}
    ║ Time: {datetime.now(VIETNAM_TZ).strftime('%H:%M:%S %d/%m/%Y')}
    ║ Admin: {len(ADMIN_IDS)}
    ╚════════════════════════════════════╝
    """)
    cleanup_sessions.start()

# ==================== CHẠY BOT ====================
if __name__ == "__main__":
    if TOKEN == "YOUR_DISCORD_BOT_TOKEN":
        print("❌ Vui lòng thay TOKEN trong file!")
    else:
        bot.run(TOKEN)