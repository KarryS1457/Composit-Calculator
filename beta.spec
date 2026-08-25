# -*- mode: python ; coding: utf-8 -*-
# Бета-сборка: тот же код, что и в main.spec, с двумя отличиями —
#   1) внутрь кладется файл-маркер beta.marker (по нему программа понимает,
#      что она бета: баннер в меню, отдельный журнал, своя версия);
#   2) exe называется cscalc-beta, чтобы он мог лежать рядом с рабочим
#      cscalc.exe и не подменял его при копировании.
# Сборка:  python -m PyInstaller --noconfirm --clean beta.spec
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
           ('icon.ico', '.'), ('beta.marker', '.'),
           ('изменения.txt', '.')],
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
    name='cscalc-beta',
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
