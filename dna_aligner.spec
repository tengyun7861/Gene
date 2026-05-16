# dna_aligner.spec
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# 获取项目根目录（使用当前工作目录）
project_root = os.getcwd()

# 使用 collect_all 获取所有 torch 相关文件（包括 CUDA DLL）
torch_all = collect_all('torch')
torch_datas = torch_all[0]  # 数据文件
torch_binaries = torch_all[1]  # 二进制文件（DLL）
torch_modules = torch_all[2]  # 模块

# 收集PyQt5相关文件
qt_datas = collect_data_files('PyQt5')

# 额外需要包含的文件
extra_files = [
    (os.path.join(project_root, 'history.db'), '.'),  # 数据库文件
]

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=torch_binaries,  # 添加 CUDA DLL 文件
    datas=torch_datas + qt_datas + extra_files,
    hiddenimports=torch_modules + [
        'numpy',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'dna_aligner.core',
        'dna_aligner.gui',
        'dna_aligner.models',
        'dna_aligner.utils',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DNA序列比对工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 关闭控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dna.ico'  # 可选：添加图标
)