# -*- mode: python ; coding: utf-8 -*-
import sys

# 실행 파일 아이콘: Windows는 .ico, macOS는 .icns, Linux는 지정하지 않음(미지원)
if sys.platform == 'win32':
    exe_icon = ['latexcolorpalette.ico']
elif sys.platform == 'darwin':
    exe_icon = ['latexcolorpalette.icns']
else:
    exe_icon = None

a = Analysis(
    ['latexcolorpalette.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('latexcolors.sty', '.'),
        ('latexcolorsnames.txt', '.'),
        ('svgnam.def', '.'),
        ('x11nam.def', '.'),
        ('dvipsnam.def', '.'),
        ('xkcd_popular.txt', '.'),
        ('xkcdcolors.sty', '.'),
        # 런타임 창 아이콘 (Windows: .ico, 그 외: .png)
        ('latexcolorpalette.ico', '.'),
        ('latexcolorpalette.png', '.'),
    ],
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
    name='latexcolorpalette',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=exe_icon,
)

# macOS: .app 번들 생성
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='LaTeX Color Palette.app',
        icon='latexcolorpalette.icns',
        bundle_identifier=None,
    )
