import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
from playsound import playsound
import pymysql
import os
import json
import subprocess
import sys
import requests

CONFIG_FILE = "config.json"
VERSION_FILE = "version.txt"
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/gungabpom/tts_patient_call/main/version.txt"
UPDATER_FILE = "updater.py"
APP_NAME = "tts_patient_call.exe"

# -------------------------------
# โหลดการตั้งค่า
# -------------------------------
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except:
    config = {
        "db_config": {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "hospital"
        },
        "text_config": {
            "prefix": "ขอเชิญ",
            "suffix": "ที่ช่องบริการ 2 ค่ะ",
            "show_prefix_name": True
        }
    }

db_config = config["db_config"]
text_config = config["text_config"]

# -------------------------------
# โหลดเวอร์ชัน
# -------------------------------
def get_local_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0.0.0"

def get_remote_version():
    try:
        r = requests.get(REMOTE_VERSION_URL, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except:
        return None

# -------------------------------
# อัปเดตเวอร์ชัน (เรียก updater.py)
# -------------------------------
def update_app():
    app_path = sys.argv[0]
    if not os.path.exists(UPDATER_FILE):
        messagebox.showerror("ไม่พบ updater.py", "กรุณาแน่ใจว่าไฟล์ updater.py อยู่ในโฟลเดอร์เดียวกับโปรแกรม")
        return
    messagebox.showinfo("อัปเดต", "กำลังอัปเดตและรีสตาร์ทโปรแกรม...")
    subprocess.Popen(["python", UPDATER_FILE, app_path])
    root.destroy()

# -------------------------------
# ตรวจสอบเวอร์ชัน
# -------------------------------
def check_for_update():
    remote_ver = get_remote_version()
    local_ver = get_local_version()
    if remote_ver and remote_ver != local_ver:
        if messagebox.askyesno("พบเวอร์ชันใหม่", f"เวอร์ชันใหม่ {remote_ver} พร้อมให้ติดตั้ง\n\nต้องการอัปเดตตอนนี้หรือไม่?"):
            update_app()

# -------------------------------
# ฟังก์ชันพื้นฐาน
# -------------------------------
def save_config_file():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def test_connection():
    try:
        conn = pymysql.connect(
            host=host_entry.get(),
            user=user_entry.get(),
            password=pass_entry.get(),
            database=db_entry.get(),
            charset='utf8mb4'
        )
        conn.close()
        messagebox.showinfo("สำเร็จ ✅", "เชื่อมต่อฐานข้อมูลสำเร็จ")
    except Exception as e:
        messagebox.showerror("เชื่อมต่อล้มเหลว ❌", str(e))

def save_db_settings():
    global db_config
    db_config["host"] = host_entry.get()
    db_config["user"] = user_entry.get()
    db_config["password"] = pass_entry.get()
    db_config["database"] = db_entry.get()
    config["db_config"] = db_config
    save_config_file()
    settings_window.destroy()
    messagebox.showinfo("บันทึกแล้ว", "บันทึกการตั้งค่าฐานข้อมูลเรียบร้อย")

def open_db_settings():
    global host_entry, user_entry, pass_entry, db_entry, settings_window
    settings_window = tk.Toplevel(root)
    settings_window.title("ตั้งค่าฐานข้อมูล")
    settings_window.geometry("300x230")

    tk.Label(settings_window, text="Host:").grid(row=0, column=0, padx=5, pady=5)
    host_entry = tk.Entry(settings_window)
    host_entry.insert(0, db_config["host"])
    host_entry.grid(row=0, column=1)

    tk.Label(settings_window, text="User:").grid(row=1, column=0, padx=5, pady=5)
    user_entry = tk.Entry(settings_window)
    user_entry.insert(0, db_config["user"])
    user_entry.grid(row=1, column=1)

    tk.Label(settings_window, text="Password:").grid(row=2, column=0, padx=5, pady=5)
    pass_entry = tk.Entry(settings_window, show="*")
    pass_entry.insert(0, db_config["password"])
    pass_entry.grid(row=2, column=1)

    tk.Label(settings_window, text="Database:").grid(row=3, column=0, padx=5, pady=5)
    db_entry = tk.Entry(settings_window)
    db_entry.insert(0, db_config["database"])
    db_entry.grid(row=3, column=1)

    tk.Button(settings_window, text="ทดสอบการเชื่อมต่อ", command=test_connection, bg="#f0ad4e").grid(row=4, column=0, columnspan=2, pady=5)
    tk.Button(settings_window, text="บันทึก", command=save_db_settings, bg="#5cb85c").grid(row=5, column=0, columnspan=2, pady=5)

def save_text_settings():
    global text_config
    text_config["prefix"] = prefix_entry.get()
    text_config["suffix"] = suffix_entry.get()
    text_config["show_prefix_name"] = prefix_var.get()
    config["text_config"] = text_config
    save_config_file()
    text_window.destroy()
    messagebox.showinfo("บันทึกแล้ว", "บันทึกการตั้งค่าข้อความเรียบร้อย")

def open_text_settings():
    global prefix_entry, suffix_entry, prefix_var, text_window
    text_window = tk.Toplevel(root)
    text_window.title("ตั้งค่าข้อความ")
    text_window.geometry("350x230")

    tk.Label(text_window, text="ข้อความก่อนชื่อ:").grid(row=0, column=0, padx=5, pady=10, sticky="e")
    prefix_entry = tk.Entry(text_window, width=30)
    prefix_entry.insert(0, text_config["prefix"])
    prefix_entry.grid(row=0, column=1)

    tk.Label(text_window, text="ข้อความหลังชื่อ:").grid(row=1, column=0, padx=5, pady=10, sticky="e")
    suffix_entry = tk.Entry(text_window, width=30)
    suffix_entry.insert(0, text_config["suffix"])
    suffix_entry.grid(row=1, column=1)

    prefix_var = tk.BooleanVar(value=text_config.get("show_prefix_name", True))
    tk.Checkbutton(text_window, text="แสดงคำนำหน้า (เช่น นาย/นาง/เด็กชาย)", variable=prefix_var).grid(row=2, column=0, columnspan=2)

    tk.Button(text_window, text="บันทึก", command=save_text_settings, bg="#5cb85c").grid(row=3, column=0, columnspan=2, pady=15)

def get_patient_name(hn):
    try:
        conn = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            charset='utf8mb4'
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT pname, fname, lname FROM patient WHERE LPAD(hn, 9, '0') = LPAD(%s, 9, '0')", (hn,))
        patient = cursor.fetchone()
        conn.close()
        return patient
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", str(e))
        return None

def call_patient():
    hn = hn_entry.get().strip()
    if hn == "":
        messagebox.showwarning("เตือน", "กรุณากรอก HN")
        return

    patient = get_patient_name(hn)
    if not patient:
        messagebox.showerror("ไม่พบข้อมูล", f"ไม่พบผู้ป่วย HN {hn}")
        return

    name_part = f"{patient['pname']}{patient['fname']} {patient['lname']}" if text_config.get("show_prefix_name", True) else f"{patient['fname']} {patient['lname']}"
    text = f"{text_config['prefix']} {name_part} {text_config['suffix']}"

    try:
        tts = gTTS(text=text, lang='th')
        filename = f"call_{hn}.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
        hn_entry.focus_set()
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", str(e))

# -------------------------------
# GUI
# -------------------------------
root = tk.Tk()
root.title(f"ระบบเรียกชื่อผู้ป่วย (Text-to-Speech) v{get_local_version()}")
root.geometry("400x330")
root.attributes("-topmost", True)

tk.Label(root, text="HN ผู้ป่วย:", font=("Tahoma", 14)).pack(pady=10)
hn_entry = tk.Entry(root, font=("Tahoma", 14))
hn_entry.pack()
hn_entry.focus_set()

hn_entry.bind("<Return>", lambda e: call_patient())

tk.Button(root, text="เรียกชื่อ", command=call_patient, font=("Tahoma", 14), bg="lightgreen").pack(pady=10)
tk.Button(root, text="ตั้งค่าฐานข้อมูล", command=open_db_settings, font=("Tahoma", 12), bg="lightblue").pack(pady=5)
tk.Button(root, text="ตั้งค่าข้อความ", command=open_text_settings, font=("Tahoma", 12), bg="lightyellow").pack(pady=5)
tk.Button(root, text="อัปเดตโปรแกรม", command=check_for_update, font=("Tahoma", 12), bg="#f0ad4e").pack(pady=5)

root.after(2000, check_for_update)
root.mainloop()
