import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
from playsound import playsound
import pymysql
import os
import json
import requests
import threading
import subprocess

# -------------------------------
# ค่าพื้นฐาน
# -------------------------------
CONFIG_FILE = "config.json"
VERSION_FILE = "version.txt"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/gungabpom/tts_patient_call/main/version.txt"

# อ่านเวอร์ชันปัจจุบัน
try:
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        LOCAL_VERSION = f.read().strip()
except:
    LOCAL_VERSION = "1.0.0"

# -------------------------------
# โหลด config จากไฟล์
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
            "suffix": "ที่ช่องบริการ 2 ค่ะ"
        },
        "show_prefix_name": True
    }

db_config = config["db_config"]
text_config = config["text_config"]

# -------------------------------
# ฟังก์ชันบันทึก config
# -------------------------------
def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# -------------------------------
# ทดสอบการเชื่อมต่อฐานข้อมูล
# -------------------------------
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

# -------------------------------
# หน้าต่างตั้งค่าฐานข้อมูล
# -------------------------------
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
    tk.Button(settings_window, text="บันทึก", command=lambda: save_db_settings(settings_window), bg="#5cb85c").grid(row=5, column=0, columnspan=2, pady=5)

def save_db_settings(win):
    db_config["host"] = host_entry.get()
    db_config["user"] = user_entry.get()
    db_config["password"] = pass_entry.get()
    db_config["database"] = db_entry.get()
    config["db_config"] = db_config
    save_config()
    win.destroy()
    messagebox.showinfo("บันทึกแล้ว", "บันทึกการตั้งค่าฐานข้อมูลเรียบร้อย")

# -------------------------------
# ตั้งค่าข้อความ
# -------------------------------
def open_text_settings():
    global prefix_entry, suffix_entry, prefix_checkbox, text_window
    text_window = tk.Toplevel(root)
    text_window.title("ตั้งค่าข้อความ")
    text_window.geometry("350x200")

    tk.Label(text_window, text="ข้อความก่อนชื่อ:").grid(row=0, column=0, padx=5, pady=10)
    prefix_entry = tk.Entry(text_window, width=30)
    prefix_entry.insert(0, text_config["prefix"])
    prefix_entry.grid(row=0, column=1)

    tk.Label(text_window, text="ข้อความหลังชื่อ:").grid(row=1, column=0, padx=5, pady=10)
    suffix_entry = tk.Entry(text_window, width=30)
    suffix_entry.insert(0, text_config["suffix"])
    suffix_entry.grid(row=1, column=1)

    prefix_var = tk.BooleanVar(value=config.get("show_prefix_name", True))
    prefix_checkbox = tk.Checkbutton(text_window, text="แสดงคำนำหน้า (นาย/นาง/น.ส.)", variable=prefix_var)
    prefix_checkbox.grid(row=2, column=0, columnspan=2, pady=5)

    tk.Button(text_window, text="บันทึก", command=lambda: save_text_settings(text_window, prefix_var), bg="#5cb85c").grid(row=3, column=0, columnspan=2, pady=10)

def save_text_settings(win, prefix_var):
    text_config["prefix"] = prefix_entry.get()
    text_config["suffix"] = suffix_entry.get()
    config["text_config"] = text_config
    config["show_prefix_name"] = prefix_var.get()
    save_config()
    win.destroy()
    messagebox.showinfo("บันทึกแล้ว", "บันทึกการตั้งค่าข้อความเรียบร้อย")

# -------------------------------
# ดึงข้อมูลผู้ป่วยจาก HN (รองรับเลขไม่มีศูนย์)
# -------------------------------
def get_patient_name(hn):
    try:
        conn = pymysql.connect(**db_config, charset='utf8mb4')
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT pname, fname, lname, hn FROM patient")
        patients = cursor.fetchall()
        conn.close()

        for p in patients:
            if str(int(p['hn'])) == str(int(hn)):
                return p
        return None
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", str(e))
        return None

# -------------------------------
# เรียกชื่อผู้ป่วย
# -------------------------------
def call_patient():
    hn = hn_entry.get().strip()
    if not hn:
        messagebox.showwarning("เตือน", "กรุณากรอก HN")
        return

    patient = get_patient_name(hn)
    if not patient:
        messagebox.showerror("ไม่พบข้อมูล", f"ไม่พบผู้ป่วย HN {hn}")
        return

    name_part = f"{patient['pname']}" if config.get("show_prefix_name", True) else ""
    text = f"{text_config['prefix']} {name_part}{patient['fname']} {patient['lname']} {text_config['suffix']}"
    try:
        tts = gTTS(text=text, lang='th')
        filename = f"call_{hn}.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", str(e))

# -------------------------------
# ตรวจสอบเวอร์ชันจาก GitHub
# -------------------------------
def check_new_version():
    def run_check():
        try:
            r = requests.get(GITHUB_VERSION_URL, timeout=5)
            latest_version = r.text.strip()
            if latest_version != LOCAL_VERSION:
                root.title(f"ระบบเรียกชื่อผู้ป่วย — v{LOCAL_VERSION} (มีเวอร์ชันใหม่: v{latest_version})")
                if messagebox.askyesno("อัปเดตเวอร์ชันใหม่", f"มีเวอร์ชันใหม่ {latest_version}\nต้องการอัปเดตตอนนี้ไหม?"):
                    update_program()
            else:
                root.title(f"ระบบเรียกชื่อผู้ป่วย — v{LOCAL_VERSION} (ล่าสุด)")
        except:
            root.title(f"ระบบเรียกชื่อผู้ป่วย — v{LOCAL_VERSION} (ตรวจสอบเวอร์ชันล้มเหลว)")
    threading.Thread(target=run_check).start()

def update_program():
    try:
        subprocess.Popen(["git", "pull"])
        messagebox.showinfo("อัปเดตแล้ว", "อัปเดตโปรแกรมเรียบร้อย กรุณาเปิดใหม่อีกครั้ง")
    except Exception as e:
        messagebox.showerror("อัปเดตล้มเหลว", str(e))

# -------------------------------
# GUI หลัก
# -------------------------------
root = tk.Tk()
root.geometry("400x320")
root.title(f"ระบบเรียกชื่อผู้ป่วย — v{LOCAL_VERSION}")

root.attributes("-topmost", True)

tk.Label(root, text="HN ผู้ป่วย:", font=("TH Sarabun New", 14)).pack(pady=10)
hn_entry = tk.Entry(root, font=("TH Sarabun New", 14))
hn_entry.pack()

tk.Button(root, text="เรียกชื่อ", command=call_patient, bg="#98FB98", font=("TH Sarabun New", 14)).pack(pady=10)
tk.Button(root, text="ตั้งค่าฐานข้อมูล", command=open_db_settings, bg="#87CEFA", font=("TH Sarabun New", 12)).pack(pady=5)
tk.Button(root, text="ตั้งค่าข้อความ", command=open_text_settings, bg="#FFF68F", font=("TH Sarabun New", 12)).pack(pady=5)
tk.Button(root, text="ตรวจสอบเวอร์ชัน", command=check_new_version, bg="#FFD580", font=("TH Sarabun New", 12)).pack(pady=5)

check_new_version()
root.mainloop()
