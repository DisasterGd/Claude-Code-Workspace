@echo off
chcp 65001 >nul
echo ============================================
echo   Symbol Finder — PyInstaller 打包脚本
echo ============================================
echo.

REM 检查 PyInstaller 是否已安装
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] PyInstaller 未安装，正在安装...
    pip install pyinstaller
    echo.
)

echo [1/3] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo [2/3] 开始打包...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "SymbolFinder" ^
    --icon=NONE ^
    --add-data "symbol_data.py;." ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败！请检查错误信息。
    pause
    exit /b 1
)

echo [3/3] 打包完成！
echo.
echo 可执行文件位于: dist\SymbolFinder.exe
echo.
pause
