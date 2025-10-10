#!/usr/bin/env python3
# nova_gmail_sender_infinite_color_v3.py
"""
Developer Tool By ✿｡🌸 𝑵𝒐𝒗𝒂𝑿 🌸｡✿
Facebook admin : Tiến Đạt ( Real )
"""

import smtplib
import ssl
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Colorama init
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except Exception:
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = WHITE = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╔═══════════════════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║  ⚙️ 𝑵𝒐𝒗𝒂𝑿 Spam Tool | Gmail Group Premium               ║")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╠═══════════════════════════════════════════════════════╣")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.CYAN}{Style.BRIGHT} 👑 Admin     : Tiến Đạt (Real)")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}📅 Khởi chạy : {now}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}⚡ Phiên bản : Premium V5.0")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}║ {Fore.CYAN}{Style.BRIGHT}🌈 Developer : NovaX Team")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╚═══════════════════════════════════════════════════════╝\n")

def test_smtp(gmail, password):
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ctx, timeout=15) as s:
            s.login(gmail, password)
        return True, "Kết nối SMTP thành công ✅"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed — kiểm tra App Password (myaccount.google.com)."
    except Exception as e:
        return False, f"Lỗi kết nối SMTP: {e}"

def send_mail(gmail, password, to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = gmail
    msg["To"] = to_email
    msg["Subject"] = subject or "(no subject)"
    msg.attach(MIMEText(body or "", "plain"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ctx, timeout=30) as server:
        server.login(gmail, password)
        server.sendmail(gmail, [to_email], msg.as_string())

def infinite_send_colored(gmail, password, to_email, subjects, body, delay):
    """
    Gửi vô hạn ngay lập tức
    - subjects: str (1 subject) hoặc list (nhiều dòng từ nhay.txt)
    - Chỉ in status ✓ Sent / ✗ Failed | To: email
    """
    counter = 0
    if isinstance(subjects, str):
        subjects_list = [subjects]
    else:
        subjects_list = subjects
    idx = 0
    try:
        print(Fore.GREEN + f"Đang gửi VÔ HẠN → {Fore.CYAN}{to_email} (Ctrl+C để dừng).")
        while True:
            subj = subjects_list[idx % len(subjects_list)]
            counter += 1
            try:
                send_mail(gmail, password, to_email, subj, body)
                print(f"[{counter}] {Fore.GREEN}✓ Sent | To: {Fore.CYAN}{to_email}")
            except:
                print(f"[{counter}] {Fore.RED}✗ Failed | To: {Fore.CYAN}{to_email}")
            idx += 1
            try:
                time.sleep(max(0, float(delay)))
            except:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Đã dừng bởi user (Ctrl+C).")

def main():
    clear_screen()
    print_banner()
    try:
        gmail_in = input(Fore.YELLOW + "Tk Gmail : ").strip()
        if "|" in gmail_in and gmail_in.count("|") == 1:
            gmail, app_password = [x.strip() for x in gmail_in.split("|", 1)]
            print(Fore.CYAN + "(Phát hiện App Password kèm input.)")
        else:
            gmail = gmail_in
            app_password = input(Fore.YELLOW + "Mk Gmail (App Password) : ").strip()

        # === Chọn Y/N nhập thủ công hay lấy từ file nhay.txt ===
        use_manual = input(Fore.YELLOW + "Nhập tiêu đề thủ công? (y/n) [y] : ").strip().lower() or "y"
        if use_manual == "y":
            subject = input(Fore.YELLOW + "Tiêu đề mail: ").strip() or "NovaX Infinite Mail"
            subjects = subject
        else:
            path = "nhay.txt"
            if not os.path.isfile(path):
                print(Fore.RED + f"Không tìm thấy file '{path}'. Hãy tạo file hoặc chọn nhập thủ công.")
                return
            with open(path, "r", encoding="utf-8") as f:
                subjects_list = [line.strip() for line in f if line.strip()]
            if not subjects_list:
                print(Fore.RED + f"File '{path}' rỗng. Hãy nhập tiêu đề thủ công.")
                return
            subjects = subjects_list
            print(Fore.GREEN + f"Đã load {len(subjects_list)} chủ đề từ '{path}', gửi tuần tự từng dòng.")

        body = input(Fore.YELLOW + "Tin nhắn (Body): ").strip() or "NovaX Mailer Test"
        try:
            delay = float(input(Fore.YELLOW + "Delay giữa mỗi mail (giây) [5]: ").strip() or "5")
        except Exception:
            delay = 5.0

        to_email = input(Fore.YELLOW + "Gmail người nhận: ").strip()
        if not to_email:
            print(Fore.RED + "Phải nhập Gmail người nhận. Hủy.")
            return

        ok, msg = test_smtp(gmail, app_password)
        print((Fore.GREEN + msg) if ok else (Fore.YELLOW + msg))

        # Gửi vô hạn ngay lập tức
        infinite_send_colored(gmail, app_password, to_email, subjects, body, delay)

    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Đã dừng bởi user.")
    except Exception as e:
        print(Fore.RED + f"Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()