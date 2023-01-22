import subprocess
import time
import os
import json
import random
from utils.blivex import Bilibili
bili = Bilibili()
bili.login_with_cookie('./data/cookie.json')
video_file = './data/videos.json'
mtime = os.stat(video_file).st_mtime
with open(video_file, 'r') as v_f:
    live_list = json.load(v_f)
    
file_list = []
for p in live_list['path']:
    f_li = [x for x in os.listdir(p) if (os.path.splitext(x)[1] == '.mp4')]
    file_list.extend( p+x for x in f_li)

i = 0
retry = 0
high = len(file_list) - 1

while not bili.info["live_status"]:
    bili.start_live()
    time.sleep(1)
    bili.get_user_info()

rtmp_addr = bili.get_rtmp()

while True:
    if mtime != os.stat(video_file).st_mtime:
        log_file = open('./data/live.log', 'a')
        e_start = time.time()
        log_content = (f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]  change:\"{video_file}\",refresh")
        log_file.write(log_content + "\n")
        log_file.close()
        mtime = os.stat(video_file).st_mtime
        with open(video_file, 'r') as v_f:
            live_list = json.load(v_f)
        file_list = []
        for p in live_list['path']:
            f_li = [x for x in os.listdir(p) if (os.path.splitext(x)[1] == '.mp4')]
            file_list.extend( p+x for x in f_li)
        i = 0
        retry = 0
        high = len(file_list) - 1

    if retry > 4:
        log_file = open('./data/live.log', 'a')
        e_start = time.time()
        log_content = (f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]  retry:{retry},break")
        log_file.write(log_content + "\n")
        log_file.close()
        break

    if retry > 2:
        bili = Bilibili()
        bili.login_with_cookie('./data/cookie.json')
        bili.stop_live()
        time.sleep(1)
        bili.start_live()
        time.sleep(1)
        rtmp_addr = bili.get_rtmp()
        bili.send_dm("BOT:尝试重新连接成功，直播继续")
        log_file = open('./data/live.log', 'a')
        e_start = time.time()
        log_content = (f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]  retry:{retry},net_work,retry_login_live,retry_get_rtmp:{rtmp_addr}")
        log_file.write(log_content + "\n")
        log_file.close()

    i = random.randint(0, high)
    log_file = open('./data/live.log', 'a')
    e_start = time.time()
    log_content = (f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]  push:{file_list[i]}")
    log_file.write(log_content + "\n")
    log_file.close()
    returncode = subprocess.Popen(f'ffmpeg -re -i {file_list[i]} -threads 8 -preset ultrafast -c copy -flvflags no_duration_filesize -f flv \"{rtmp_addr}\"', shell=True).wait()
    if returncode:
        retry += 1
        ping = 1
        log_file = open('./data/live.log', 'a')
        e_start = time.time()
        log_content = (f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]  push_error,try_ping")
        log_file.write(log_content + "\n")
        log_file.close()
        while ping:
            ping = subprocess.Popen(f'ping live-push.bilivideo.com -c 1', shell=True).wait()
            time.sleep(1)
        rtmp_addr = bili.get_rtmp()
        log_file = open('./data/live.log', 'a')
        e_start = time.time()
        log_content = (f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]  retry:{retry},net_work,retry_get_rtmp:{rtmp_addr}")
        log_file.write(log_content + "\n")
        log_file.close()
        
    else:
        retry = 0
