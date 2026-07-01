# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

# Экраны turningotp подгружаются динамически (importlib) — PyInstaller не
# видит такие импорты сам, поэтому перечисляем их явно, иначе в собранном
# exe вкладки "ТОКАРНАЯ ОБРАБОТКА ОТПиР" не открываются. turning добавляем
# заодно для надежности (он импортируется статически, но пусть будет).
hiddenimports = collect_submodules('turningotp') + collect_submodules('turning')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('pics', 'pics'), ('core', 'core'), ('ui', 'ui'),
           ('turning', 'turning'), ('turningotp', 'turningotp'),
           ('icon.ico', '.')],
    hiddenimports=hiddenimports,
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
    name='cscalc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
