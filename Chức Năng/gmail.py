#!/usr/bin/env python3
# nova_gmail_rotating_accounts_full.py
# -*- coding: utf-8 -*-
"""
Developer Tool By ✿｡🌸 𝑵𝒐𝒗𝒂𝑿 🌸｡✿
Facebook admin : Tiến Đạt (Real)
"""

import os, time, ssl, smtplib, shutil, random, socket
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ================= COLOR / GRADIENT =================
def rgb(r,g,b,t): return f"\033[38;2;{r};{g};{b}m{t}\033[0m"
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
    b = neon_border(w,c1,c2)
    print(f"+{b}+")
    if title:
        t = grad(f" {title} ", c1,c2)
        print(f"|{t.center(w)}|")
        print(f"+{b}+")
    for line in lines or []:
        inner = grad(line.strip(), (240,240,255),(200,255,255))
        print(f"| {inner:<{w-2}}|")
    print(f"+{b}+")

# ================= BANNER / LOGO ===================
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
    print(grad("⚡ NOVAX SAFE GMAIL SENDER ⚡",(255,255,120),c2))

def banner_live():
    c1,c2 = theme()
    clear()
    logo(c1,c2)
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    try: ip = socket.gethostbyname(socket.gethostname())
    except: ip = "Không xác định"
    neon_box("THÔNG TIN TOOL", [
        "👑 Admin     : Tiến Đạt (Real)",
        f"📅 Khởi chạy : {now}",
        "⚡ Phiên bản : Premium V5.0",
        "🌈 Developer : NovaX Team",
        f"🌐 IP Thiết bị : {ip}"
    ], c1,c2)
    return c1,c2

# ================= SMTP HELPERS ===================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def test_smtp(gmail,password):
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.login(gmail,password)
        return True,"Kết nối SMTP thành công ✅"
    except smtplib.SMTPAuthenticationError:
        return False,"Authentication failed — kiểm tra App Password."
    except Exception as e:
        return False,f"Lỗi kết nối SMTP: {e}"

def make_message(gmail,to_email,subject,body):
    msg = MIMEMultipart()
    msg["From"] = gmail
    msg["To"] = to_email
    msg["Subject"] = subject or "(no subject)"
    msg.attach(MIMEText(body or "","plain"))
    return msg

def send_mail(gmail,password,to_email,subject,body):
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls(context=ctx)
        server.login(gmail,password)
        msg = make_message(gmail,to_email,subject,body)
        server.sendmail(gmail,[to_email],msg.as_string())

# ================= SENDER LOOP =====================
def infinite_rotating_send(accounts,to_email,subjects,body,delay):
    counter = 0
    idx = 0
    if isinstance(subjects,str): subjects_list = [subjects]
    else: subjects_list = subjects
    try:
        c1,c2 = theme()
        print(grad(f"Đang gửi VÔ HẠN → {to_email} (Ctrl+C để dừng).",c1,c2))
        while True:
            account = accounts[idx % len(accounts)]
            gmail,password = account
            subj = subjects_list[idx % len(subjects_list)]
            counter += 1
            try:
                send_mail(gmail,password,to_email,subj,body)
                print(grad(f"[{counter}] ✓ Sent | {gmail} → {to_email} | {subj}",(180,255,180),(100,255,255)))
            except Exception as e:
                print(grad(f"[{counter}] ✗ Failed | {gmail} → {to_email} | Err: {e}",(255,80,80),(255,150,150)))
            idx += 1
            try: time.sleep(max(0.5,float(delay)))
            except: time.sleep(1)
    except KeyboardInterrupt:
        print("\n"+grad("⏹️ Đã dừng bởi user (Ctrl+C).",(255,255,120),(255,180,180)))

# ================= MAIN ==========================
def main():
    c1,c2 = banner_live()
    accounts = []
    print(grad("Nhập tài khoản Gmail | AppPassword, nhập 'done' để kết thúc:",c1,c2))
    while True:
        line = input(grad("> ",c1,c2)).strip()
        if line.lower() == "done": break
        if "|" not in line:
            print(grad("❌ Sai định dạng, phải email|app_password",(255,80,80),(255,150,150)))
            continue
        email,apppw = [x.strip() for x in line.split("|",1)]
        accounts.append((email,apppw))
    if not accounts:
        print(grad("❌ Chưa nhập tài khoản nào, thoát.",(255,80,80),(255,150,150)))
        return

    print(grad("Gmail người nhận: ",c1,c2))
    to_email = input(grad(">",c1,c2)).strip()
    if not to_email:
        print(grad("❌ Phải nhập Gmail người nhận. Hủy.",(255,80,80),(255,150,150)))
        return

    print(grad("Nhập tiêu đề thủ công? (y/n) [y]: ",c1,c2))
    use_manual = input(grad(">",c1,c2)).strip().lower() or "y"
    if use_manual == "y":
        print(grad("Tiêu Đề Gmail:",c1,c2))
        subject = input(grad(">",c1,c2)).strip() or "NovaX Mail"
        subjects = subject
    else:
        path = "nhay.txt"
        if not os.path.isfile(path):
            print(grad(f"❌ Không tìm thấy file '{path}', chọn nhập thủ công.",(255,80,80),(255,150,150)))
            return
        with open(path,"r",encoding="utf-8") as f:
            subjects_list = [line.strip() for line in f if line.strip()]
        if not subjects_list:
            print(grad(f"❌ File '{path}' rỗng, chọn nhập thủ công.",(255,80,80),(255,150,150)))
            return
        subjects = subjects_list
        print(grad(f"Đã load {len(subjects_list)} tiêu đề từ '{path}'.",(180,255,180),(100,255,255)))

    print(grad("Tin Nhắn:",c1,c2))
    body = input(grad(">",c1,c2)).strip() or "NovaX Mail Test"
    try:
        print(grad("Tốc Độ (giây):",c1,c2))
        delay = float(input(grad(">",c1,c2)).strip() or "5")
    except:
        delay = 5.0

    # Test lần lượt các tài khoản
    for g,p in accounts:
        ok,msg = test_smtp(g,p)
        print(grad(f"{g}: {msg}",(180,255,180),(100,255,255)) if ok else grad(f"{g}: {msg}",(255,80,80),(255,150,150)))

    infinite_rotating_send(accounts,to_email,subjects,body,delay)

if __name__=="__main__":
    main()