@echo off
setlocal ENABLEDELAYEDEXPANSION
chcp 65001 >nul
title FastAPI 打包（增强版 - 全局错误捕获）

REM ===== 可配置选项 =====
set KEY=5f1c2a9e7b0d4e8f9a1c3e5d7f9b2a6c
set ONEFILE=1
set FORCE_PIP_INSTALL=1
set PYTHONNOUSERSITE=1
set PIP_DISABLE_PIP_VERSION_CHECK=1
set PIP_NO_INPUT=1

echo.
echo ================== 步骤 1/4：准备虚拟环境 ==================
if not exist venv\Scripts\activate.bat (
  echo 🧪 正在创建虚拟环境...
  python -m venv venv || (echo ❌ 创建虚拟环境失败！ & goto end)
)

call venv\Scripts\activate.bat || (echo ❌ 激活虚拟环境失败！ & goto end)

if %FORCE_PIP_INSTALL%==1 (
  echo 🔼 正在升级 pip...
  python -m pip install --upgrade pip || (echo ❌ pip 升级失败！ & goto end)
  echo 📦 安装依赖（requirements.txt）...
  pip install -r requirements.txt || (echo ❌ 依赖安装失败！ & goto end)
) else (
  if not exist venv\.deps.ok (
    echo 🔼 正在升级 pip...
    python -m pip install --upgrade pip || (echo ❌ pip 升级失败！ & goto end)
    echo 📦 首次安装依赖（requirements.txt）...
    pip install -r requirements.txt || (echo ❌ 依赖安装失败！ & goto end)
    echo ok> venv\.deps.ok
  ) else (
    echo ⏭️ 跳过依赖安装（如需重装，请设置 FORCE_PIP_INSTALL=1）
  )
)

echo.
echo ================== 步骤 2/4：清理旧构建 ==================
echo 🧹 正在清理 build/ dist/ run.spec...

if exist build (
  rmdir /s /q build || (echo ❌ 無法刪除 build 目錄！ & goto end)
)

if exist dist (
  rmdir /s /q dist || (echo ❌ 無法刪除 dist 目錄！ & goto end)
)

if exist run.spec (
  del /q /f run.spec || (echo ❌ 無法刪除 run.spec 文件！ & goto end)
)

echo.
echo ================== 步骤 3/4：构建命令准备 ==================
set COMMON_ARGS=run.py --noconfirm ^
 --add-data "app;app" ^
 --add-data "common;common" ^
 --add-data "index.html;."

REM 添加固定的 data 文件（supplements.db 可写，其他只读）
set DATA_ARGS= ^
 --add-data "data/characters.db;data" ^
 --add-data "data/dialects_all.db;data" ^
 --add-data "data/dialects_query.db;data" ^
 --add-data "data/supplements.db;data" ^
 --add-data "data/dependency;data/dependency"

REM 模式参数
if "%ONEFILE%"=="1" (
  echo 📦 模式: 單文件發布（--onefile）
  set MODE_ARG=--onefile
) else (
  echo 🚀 模式: 多文件開發（--onedir）
  set MODE_ARG=--onedir
)

echo.
echo ================== 步骤 4/4：开始打包 ==================
set PYI=venv\Scripts\pyinstaller.exe
echo 🔧 執行打包命令...
"%PYI%" %COMMON_ARGS% %MODE_ARG% %DATA_ARGS%
if errorlevel 1 (
  echo ❌ 打包過程出錯！
  goto end
)

echo.
echo ✅ 打包完成！
if "%ONEFILE%"=="1" (
  echo ▶️ 輸出檔案: dist\run.exe
  echo ⚠️ 首次啟動將解壓資源，體積大會稍慢。
) else (
  echo ▶️ 輸出目錄: dist\run\
  echo ▶️ 運行方法: dist\run\run.exe
)

:end
echo.
echo 🔚 腳本執行完畢。
pause
exit /b
