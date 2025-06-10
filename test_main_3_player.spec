# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['test_main_3_player.py'],
    pathex=[],
    binaries=[('C:\\\\Users\\\\justin.pham\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python311\\\\Lib\\\\site-packages\\\\py_mini_racer\\\\mini_racer.dll', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='test_main_3_player',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
