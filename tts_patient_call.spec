# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tts_patient_call.py'],
    pathex=[],
    binaries=[],
    datas=[('version.txt', '.'), ('config.json', '.'), ('updater.py', '.')],
    hiddenimports=['pymysql', 'gtts', 'playsound', 'requests'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tts_patient_call',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True,
    name='tts_patient_call'
)
