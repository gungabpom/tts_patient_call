import os
import requests
import zipfile
import subprocess
import sys

GITHUB_ZIP_URL = "https://github.com/gungabpom/tts_patient_call/archive/refs/heads/main.zip"
VERSION_FILE = "version.txt"

def get_local_version():
    if not os.path.exists(VERSION_FILE):
        return "v0.0.0"
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_remote_version():
    url = "https://raw.githubusercontent.com/gungabpom/tts_patient_call/main/version.txt"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return None

def update_app():
    print("ดาวน์โหลดเวอร์ชันใหม่จาก GitHub ...")
    r = requests.get(GITHUB_ZIP_URL)
    with open("update.zip", "wb") as f:
        f.write(r.content)

    with zipfile.ZipFile("update.zip", "r") as zip_ref:
        zip_ref.extractall(".")
    os.remove("update.zip")

    src_dir = "tts_patient_call-main"
    for file in os.listdir(src_dir):
        src_path = os.path.join(src_dir, file)
        dst_path = os.path.join(".", file)
        if os.path.isdir(src_path):
            continue
        os.replace(src_path, dst_path)

    subprocess.Popen(["python", "tts_patient_call.py"])
    sys.exit(0)

if __name__ == "__main__":
    local_v = get_local_version()
    remote_v = get_remote_version()
    print(f"Local: {local_v} | Remote: {remote_v}")
    if remote_v and remote_v != local_v:
        update_app()
    else:
        print("ไม่มีเวอร์ชันใหม่")
