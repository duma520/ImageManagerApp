@echo off
chcp 65001 >nul
title 编译 ImageManagerApp

nuitka --standalone ^
    --enable-plugin=pyside6 ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=icon.ico ^
    --include-data-files=icon.ico=icon.ico ^
    --follow-imports ^
    --jobs=4 ^
    --clang ^
    --remove-output ^
    --output-dir=build_output ^
    --output-filename=ImageManagerApp.exe ^
    --windows-uac-admin ^
    --windows-company-name="杜玛" ^
    --windows-product-name="ImageManagerApp" ^
    --windows-file-version="3.16.8" ^
    --windows-product-version="3.16.8" ^
    --windows-file-description="ImageManagerApp 图片管理器" ^
    --nofollow-import-to=tkinter ^
    --nofollow-import-to=matplotlib ^
    --nofollow-import-to=numpy ^
    --nofollow-import-to=pytest ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=doctest ^
    ImageManagerApp.py
