from urllib.parse import quote
from secrets import compare_digest
import datetime
import os
import ssl
from urllib.parse import urlencode
from http import cookiejar
from urllib3.exceptions import InsecureRequestWarning
import hashlib
import random
try:
    import base64
    from requests.exceptions import RequestException
    import requests
    import pystyle
    from concurrent.futures import ThreadPoolExecutor
    from faker import Faker
    from requests import session
    import concurrent.futures
    
except ImportError:
    import os
    os.system("pip install faker")
    os.system("pip install colorama")
    os.system("pip install requests")
    os.system("pip install pystyle")
    os.system("pip install concurrent.futures")
    os.system("pip install base64")
import requests,os,time,re,json,uuid,random,sys
from concurrent.futures import ThreadPoolExecutor
import datetime
from datetime import datetime
import requests,json
import uuid
import requests
from time import sleep
from random import choice, randint, shuffle
from pystyle import Add, Center, Anime, Colors, Colorate, Write, System
from os.path import isfile
from pystyle import Colors, Colorate, Write, Center, Add, Box
from time import sleep,strftime
import socket
from pystyle import *
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def runbanner(text, delay=0.001):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


trang = "\033[1;37m\033[1m"
xanh_la = "\033[1;32m\033[1m"
xanh_duong = "\033[1;34m\033[1m"
xanhnhat = '\033[1m\033[38;5;51m'
do = "\033[1;31m\033[1m\033[1m"
xam='\033[1;30m\033[1m'
vang = "\033[1;33m\033[1m"
tim = "\033[1;35m\033[1m"
hongnhat = "#FFC0CB"
kt_code = "</>"
dac_biet = "\033[32;5;245m\033[1m\033[38;5;39m"
colors = [
    "\033[1;37m\033[1m",  # Trắng
    "\033[1;32m\033[1m",  # Xanh lá
    "\033[1;34m\033[1m",  # Xanh dương
    "\033[1m\033[38;5;51m",  # Xanh nhạt
    "\033[1;31m\033[1m\033[1m",  # Đỏ
    "\033[1;30m\033[1m",  # Xám
    "\033[1;33m\033[1m",  # Vàng
    "\033[1;35m\033[1m",  # Tím
    "\033[32;5;245m\033[1m\033[38;5;39m",  # Màu đặc biệt
]
random_color = random.choice(colors)
def idelay(o):
    while(o>0):
        o=o-1
        print(f"{trang}[{xanhnhat}tiendat{trang}] \033[1;33mV\033[1;34mu\033[1;35mi \033[1;32mL\033[1;33mò\033[1;34mn\033[1;35mg \033[1;36mC\033[1;33mh\033[1;34mờ {trang}[\033[1;35m.....""]""["+str(o)+"]""    ",end='\r')
        time.sleep(1/6)
        print(f"{trang}[{xanhnhat}tiendat{trang}] \033[1;31mV\033[1;32mu\033[1;33mi \033[1;34mL\033[1;35mò\033[1;31mn\033[1;32mg \033[1;33mC\033[1;32mh\033[1;35mờ {trang}[\033[1;33m•{trang}....""]"f"{trang}[{xanhnhat}"+str(o)+f"{trang}]""     ",end='\r')
        time.sleep(1/6)
        print(f"{trang}[{xanhnhat}tiendat{trang}] \033[1;32mV\033[1;33mu\033[1;34mi \033[1;35mL\033[1;36mò\033[1;33mn\033[1;34mg \033[1;35mC\033[1;31mh\033[1;32mờ {trang}[\033[1;35m••{trang}...""]"f"{trang}[{xanh_la}"+str(o)+f"{trang}]""     ",end='\r')
        time.sleep(1/6)
        print(f"{trang}[{xanhnhat}tiendat{trang}] \033[1;31mV\033[1;33mu\033[1;35mi \033[1;33mL\033[1;31mò\033[1;32mn\033[1;34mg \033[1;36mC\033[1;35mh\033[1;31mờ {trang}[\033[1;32m•••{trang}..""]"f"{trang}[{do}"+str(o)+f"{trang}]""     ",end='\r')
        time.sleep(1/6)
        print(f"{trang}[{xanhnhat}tiendat{trang}] \033[1;32mV\033[1;34mu\033[1;36mi \033[1;32mL\033[1;34mò\033[1;31mn\033[1;35mg \033[1;33mC\033[1;36mh\033[1;35mờ {trang}[\033[1;38m••••{trang}.""]"f"{trang}[{tim}"+str(o)+f"{trang}]""     ",end='\r')
        time.sleep(1/6)
        print(f"{trang}[{xanhnhat}tiendat{trang}] \033[1;31mV\033[1;34mu\033[1;36mi \033[1;32mL\033[1;34mò\033[1;32mn\033[1;35mg \033[1;36mC\033[1;34mh\033[1;32mờ {trang}[\033[1;33m•••••{trang}""]"f"{trang}[{vang}"+str(o)+f"{trang}]""     ",end='\r')
        time.sleep(0.1)
        print(f"{trang}[{xanhnhat}Nguyễn Tiến Đạt{trang}] \033[1;31mV\033[1;34mu\033[1;36mi \033[1;32mL\033[1;34mò\033[1;32mn\033[1;35mg \033[1;36mC\033[1;34mh\033[1;32mờ {trang}[\033[1;33m•••••{trang}""]"f"{trang}[{xanh_la}"+str(o)+f"{trang}]""     ",end='\r')

chontool = """
  \033[1;33m\033[1m _____________________________
 \033[32;5;245m\033[1m\033[38;5;39m Lưu ý để delay 8-12 để hạn chế bị mõm sớm
 \033[32;5;245m\033[1m\033[38;5;39m Nguyễn Tiến Đạt
 \033[32;5;245m\033[1m\033[38;5;39m tiendat deptrai vaicaloz
 \033[1;31m\033[1m\033[1m Facebook: https://www.facebook.com/datzk28
"""

clear()
runbanner(chontool)
idcanspam=input(f'\033[1;97m[\033[1;31m⁂\033[1;97m] {xanhnhat}Nhập Id  : {vang} ')
file_list = []
while True:
    ck=input(f'\033[1;97m[\033[1;31m⁂\033[1;97m] {xanhnhat}Mời Nhập Cookie :{vang} ')
    try:
        get=requests.get(f'https://www.facebook.com/messages/t/{idcanspam}&ret_cancel&source=profile',headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5','cookie': ck,'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','sec-fetch-dest': 'document','sec-fetch-mode': 'navigate','sec-fetch-site': 'same-origin','sec-fetch-user': '?1','upgrade-insecure-requests': '1'}).text
        fb_dtsg=get.split('<input type="hidden" name="fb_dtsg" value="')[1].split('" autocomplete="off" />')[0]
        jazoest=get.split('<input type="hidden" name="jazoest" value="')[1].split('" autocomplete="off" />')[0]
        clear()
        break
    except:
        print(f'{do}Cookie sai !')   
runbanner(chontool)
lol = input(f"{xanhnhat}Bạn Có Muốn Treo Nhiều Ngôn Không {trang}({tim}y{vang}/{tim}n{trang}): {vang}")
if lol.lower() == "y":
      stt = 0
      loz = int(input(f"{xanhnhat} Bạn Muốn Spam Bao Nhiêu Ngôn : "))
      while True:
        stt += 1
        name_files=input(f'\033[1;97m[\033[1;31m⁂\033[1;97m] {xanhnhat}Nhập File Chứa Nội Dung Thứ {stt} của bạn (ex: Form.txt) :{vang} ')
        file_list.append(name_files)
        if stt == loz:
          break
elif lol.lower() == "n":
      name_file=input(f'\033[1;97m[\033[1;31m⁂\033[1;97m] {xanhnhat}Nhập File Chứa Ngôn ( Ví Dụ : Form.txt ) :{vang} ') 
      file_list.append(name_file)
data_list = []
yn=str(input(f'\033[1;97m[\033[1;31m⁂\033[1;97m] {xanhnhat}Bạn Muốn Treo Mãi Mãi Không> {trang}({vang}y{trang}/{vang}n{trang}) :{vang} '))
params = {
    "icm": '1',
}
    
headers = {
                'Cookie': self.cookie,
                'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.facebook.com',
                'Referer': f'https://www.facebook.com/messages/t/{recipient_id}',
                'Host': 'www.facebook.com',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty'
}
if yn.lower() == 'y':
      delay=int(input(f'\033[1;97m[\033[1;31m</>\033[1;97m] {xanhnhat}Nhập Delay( 10 > 20 ) :{vang} '))
      while True:
        try:
          ping = requests.get("https://www.google.com")
          if ping.status_code == 200:
            for selected_file in file_list:
              with open(selected_file, "rb") as file:
                  nds = file.read()
                  #data_list.append(ndss.decode('utf-8'))
            #for ndss in data_list:
              data = f"fb_dtsg={fb_dtsg}&jazoest={jazoest}&body={nds.decode('utf-8')}&send=Send&tids=cid.g.{idcanspam}&wwwupp=C3&platform_xmd=&referrer=&ctype=&cver=legacy&csid=366a74a7-2d30-45dd-94c2-ad47d662dcfb"
              response = requests.post("https://www.facebook.com/messaging/send/", params=params, headers=headers, data=data.encode('utf-8'))
              print(f"\033[1;31m[\033[1;33m{i}\033[1;31m] \033[1;31m| \033[1;33mID Box \033[1;97m: {idcanspam} \033[1;31m| \033[1;31m| \033[1;35mTài Khoản : \033[1;97m: {xanh_la} Online")
              idelay(delay)
        except Exception as e:
          print(f"\033[1;31m[\033[1;33m{i}\033[1;31m] \033[1;31m| \033[1;33mID Box \033[1;97m: {idcanspam} \033[1;31m| \033[1;31m| \033[1;35mTài Khoản : \033[1;97m: {do} Offline")
          time.sleep(10)

elif yn.lower() == 'n':
      soluong = int(input(f'\033[1;97m[\033[1;31m</>\033[1;97m] {xanhnhat}Số Lần Spam :{vang} '))
      delay=int(input(f'\033[1;97m[\033[1;31m</>\033[1;97m] {xanhnhat}Nhập Delay ( 10 > 20 ) :{vang} '))
      for i in range(soluong):
        try:
          ping = requests.get("https://www.google.com")
          if ping.status_code == 200:
            for name_file in file_list:
              with open(name_file , "rb") as file:
                nds = file.read()
                data = f"fb_dtsg={fb_dtsg}&jazoest={jazoest}&body={nds.decode('utf-8')}&send=Send&tids=cid.g.{idcanspam}&wwwupp=C3&platform_xmd=&referrer=&ctype=&cver=legacy&csid=366a74a7-2d30-45dd-94c2-ad47d662dcfb"
              response = requests.post("https://www.facebook.com/messaging/send/", params=params, headers=headers, data=data.encode('utf-8'))
              i = i + 1
              print(f"\033[1;31m[\033[1;33m{i}\033[1;31m] \033[1;31m| \033[1;33mID Box \033[1;97m: {idcanspam} \033[1;31m| \033[1;31m| \033[1;35mTài Khoản : \033[1;97m: {xanh_la} Online")
              idelay(delay) 
        except Exception as e:
          print(f"\033[1;31m[\033[1;33m{i}\033[1;31m] \033[1;31m| \033[1;33mID Box \033[1;97m: {idcanspam} \033[1;31m| \033[1;31m| \033[1;35mTài Khoản : \033[1;97m: {do} Offline")
          time.sleep(10)
else:
    print(f"{do}Điền đúng")
