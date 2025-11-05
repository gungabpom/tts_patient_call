import os
import sys
import time
import shutil
import requests
import subprocess

GITHUB_RAW_EXE = "https://raw.githubusercontent.com/gungabpom/tts_patient_call/main/tts_patient_call.exe"
VERSION_URL = "https://raw.githubusercontent.com/gungabpom/tts_patient_call/main/version.txt"

def update_and_restart(app_path):
    new_file = app_path + ".new"
    backup_file = app_path + ".bak"

    try:
        print("🔄 กำลังดาวน์โหลดเวอร์ชันใหม่...")
        response = requests.get(GITHUB_RAW_EXE, stream=True)
        with open(new_file, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        if os.path.exists(backup_file):
            os.remove(backup_file)
        shutil.move(app_path, backup_file)
        shutil.move(new_file, app_path)

        print("✅ อัปเดตสำเร็จ กำลังรีสตาร์ท...")
        time.sleep(1)
        subprocess.Popen([app_path], shell=True)
        sys.exit(0)

    except Exception as e:
        print(f"❌ อัปเดตล้มเหลว: {e}")
        if os.path.exists(new_file):
            os.remove(new_file)
        time.sleep(3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ใช้คำสั่ง: updater.py <path_to_exe>")
        sys.exit(1)
    update_and_restart(sys.argv[1])
