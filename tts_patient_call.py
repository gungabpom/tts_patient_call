import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
from playsound import playsound
import pymysql
import os
import json
import subprocess

CONFIG_FILE = "config.json"
VERSION_FILE = "version.txt"
CURRENT_VERSION = "v1.0.13"
GITHUB_URL = "https://github.com/gungabpom/tts_patient_call"

# -------------------------------
# โหลดการตั้งค่าจากไฟล์เดียว
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
# บันทึก config ลงไฟล์
# -------------------------------
def save_config_file():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# -------------------------------
# ฟังก์ชันทดสอบการเชื่อมต่อ
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
# บันทึกค่าฐานข้อมูล
# -------------------------------
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

# -------------------------------
# หน้าต่างตั้งค่าฐานข้อมูล
# -------------------------------
def open_db_settings():
    global host_entry, user_entry, pass_entry, db_entry, settings_window
    settings_window = tk.Toplevel(root)
    settings_window.title("ตั้งค่าฐานข้อมูล")
    settings_window.geometry("300x250")

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

# -------------------------------
# ตั้งค่าข้อความก่อน/หลังชื่อ + คำนำหน้า
# -------------------------------
def save_text_settings():
    global text_config
    text_config["prefix"] = prefix_entry.get()
    text_config["suffix"] = suffix_entry.get()
    text_config["show_prefix_name"] = show_prefix_var.get()
    config["text_config"] = text_config
    save_config_file()
    text_window.destroy()
    messagebox.showinfo("บันทึกแล้ว", "บันทึกการตั้งค่าข้อความเรียบร้อย")

def open_text_settings():
    global prefix_entry, suffix_entry, show_prefix_var, text_window
    text_window = tk.Toplevel(root)
    text_window.title("ตั้งค่าข้อความ")
    text_window.geometry("350x220")

    tk.Label(text_window, text="ข้อความก่อนชื่อ:").grid(row=0, column=0, padx=5, pady=10, sticky="e")
    prefix_entry = tk.Entry(text_window, width=30)
    prefix_entry.insert(0, text_config["prefix"])
    prefix_entry.grid(row=0, column=1)

    tk.Label(text_window, text="ข้อความหลังชื่อ:").grid(row=1, column=0, padx=5, pady=10, sticky="e")
    suffix_entry = tk.Entry(text_window, width=30)
    suffix_entry.insert(0, text_config["suffix"])
    suffix_entry.grid(row=1, column=1)

    show_prefix_var = tk.BooleanVar(value=text_config.get("show_prefix_name", True))
    tk.Checkbutton(text_window, text="แสดงคำนำหน้าชื่อ (เช่น นาย/นาง)", variable=show_prefix_var).grid(row=2, column=0, columnspan=2)

    tk.Button(text_window, text="บันทึก", command=save_text_settings, bg="#5cb85c").grid(row=3, column=0, columnspan=2, pady=15)

# -------------------------------
# ดึงข้อมูลผู้ป่วยจาก HN (ไม่ต้องใส่ 0 นำหน้า)
# -------------------------------
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
        cursor.execute("SELECT pname, fname, lname, hn FROM patient WHERE hn = LPAD(%s, 9, '0')", (hn,))
        patient = cursor.fetchone()
        conn.close()
        return patient
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", str(e))
        return None

# -------------------------------
# แปลงข้อความเป็นเสียงและเล่นทันที (ไม่เคลียร์ HN)
# -------------------------------
def call_patient():
    hn = hn_entry.get().strip()
    if hn == "":
        messagebox.showwarning("เตือน", "กรุณากรอก HN")
        return

    patient = get_patient_name(hn)
    if not patient:
        messagebox.showerror("ไม่พบข้อมูล", f"ไม่พบผู้ป่วย HN {hn}")
        return

    prefix_name = patient['pname'] if text_config.get("show_prefix_name", True) else ""
    text = f"{text_config['prefix']} {prefix_name}{patient['fname']} {patient['lname']} {text_config['suffix']}"
    try:
        tts = gTTS(text=text, lang='th')
        filename = f"call_{hn}.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", str(e))

# -------------------------------
# ตรวจสอบเวอร์ชันและอัปเดต
# -------------------------------
def check_for_update():
    try:
        subprocess.Popen(["python", "updater.py"])
    except Exception as e:
        messagebox.showerror("อัปเดตล้มเหลว", str(e))

# -------------------------------
# GUI หลัก
# -------------------------------
root = tk.Tk()
root.title(f"ระบบเรียกชื่อผู้ป่วย (Text-to-Speech)  {CURRENT_VERSION}")
root.geometry("420x330")
root.attributes("-topmost", True)

tk.Label(root, text="HN ผู้ป่วย:", font=("TH Sarabun New", 14)).pack(pady=10)
hn_entry = tk.Entry(root, font=("TH Sarabun New", 14))
hn_entry.pack()
hn_entry.focus_set()

def on_enter(event):
    call_patient()
hn_entry.bind("<Return>", on_enter)

tk.Button(root, text="เรียกชื่อ", command=call_patient, font=("TH Sarabun New", 14), bg="lightgreen").pack(pady=10)
tk.Button(root, text="ตั้งค่าฐานข้อมูล", command=open_db_settings, font=("TH Sarabun New", 12), bg="lightblue").pack(pady=5)
tk.Button(root, text="ตั้งค่าข้อความ", command=open_text_settings, font=("TH Sarabun New", 12), bg="lightyellow").pack(pady=5)
tk.Button(root, text="ตรวจสอบอัปเดต", command=check_for_update, font=("TH Sarabun New", 12), bg="#f0ad4e").pack(pady=5)

root.mainloop()
