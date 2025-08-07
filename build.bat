@echo off
title 一键打包 FastAPI 项目为 exe
chcp 65001 >nul

echo 正在清理旧的虚拟环境与打包文件...
rmdir /s /q venv 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q /f app.spec 2>nul

echo.
echo ✅ 清理完成，开始创建虚拟环境...
python -m venv venv

if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo ❌ 找不到虚拟环境，终止。
    pause
    exit /b
)

echo.
echo 正在升级 pip...
python -m pip install --upgrade pip

echo.
echo 正在安装依赖（仅基础库）...
pip install pandas fastapi uvicorn pyinstaller

echo.
echo ✅ 环境准备完成，开始打包...
pyinstaller app.py --noconfirm --onefile ^
  --add-data "index.html;." ^
  --add-data "css;css" ^
  --add-data "js;js" ^
  --add-data "source;source" ^
  --add-data "data;data"

echo.
echo ✅ 打包完成！可执行文件位于 dist\app.exe
pause
