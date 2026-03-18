@echo off
chcp 65001 >nul
title 编译 ImageManagerApp

REM 清理之前的编译输出
if exist build_output rmdir /s /q build_output
if exist ImageManagerApp.dist rmdir /s /q ImageManagerApp.dist
if exist ImageManagerApp.build rmdir /s /q ImageManagerApp.build

nuitka --standalone ^
    --enable-plugin=pyside6 ^
    --enable-plugin=multiprocessing ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=icon.ico ^
    --include-data-files=icon.ico=icon.ico ^
    --include-package=sqlite3 ^
    --include-module=hashlib ^
    --include-module=threading ^
    --include-module=datetime ^
    --include-module=shutil ^
    --include-module=queue ^
    --nofollow-import-to=tkinter ^
    --nofollow-import-to=matplotlib ^
    --nofollow-import-to=numpy ^
    --nofollow-import-to=pytest ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=doctest ^
    --nofollow-import-to=requests ^
    --follow-imports ^
    --jobs=4 ^
    --clang ^
    --remove-output ^
    --output-dir=build_output ^
    --output-filename=ImageManagerApp.exe ^
    --windows-uac-admin ^
    --windows-company-name="杜玛" ^
    --windows-product-name="ImageManagerApp" ^
    --windows-file-version="3.16.9" ^
    --windows-product-version="3.16.9" ^
    --windows-file-description="ImageManagerApp 图片管理器" ^
    ImageManagerApp.py
