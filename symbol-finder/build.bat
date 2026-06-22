@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   Symbol Finder - PyInstaller Packager
echo ============================================
echo.

REM --- Switch to script's own directory ---
cd /d "%~dp0"
echo [INFO] Working directory: %CD%

REM --- Hardcoded Python paths (tried in order) ---
set PYTHON=
if exist "d:\software\anaconda3\python.exe"     set PYTHON=d:\software\anaconda3\python.exe
if exist "C:\ProgramData\anaconda3\python.exe"   set PYTHON=C:\ProgramData\anaconda3\python.exe
if exist "C:\Users\%USERNAME%\anaconda3\python.exe" set PYTHON=C:\Users\%USERNAME%\anaconda3\python.exe
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe" set PYTHON=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe
if exist "C:\Python313\python.exe"               set PYTHON=C:\Python313\python.exe

REM --- Fallback: scan PATH ---
if "%PYTHON%"=="" (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        set PYTHON=%%i
        goto :found
    )
)

:found
if "%PYTHON%"=="" (
    echo [ERROR] Cannot find Python.
    echo Tried: Anaconda, Python313, PATH scan - all failed.
    echo.
    echo Please install Python or run this from a normal (non-admin) shell.
    pause
    exit /b 1
)
echo [INFO] Python: %PYTHON%

REM --- Check / Install PyInstaller ---
"%PYTHON%" -m PyInstaller --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [INFO] Installing PyInstaller...
    "%PYTHON%" -m pip install pyinstaller
    if !errorlevel! neq 0 (
        echo [ERROR] pip install pyinstaller failed
        pause
        exit /b 1
    )
)

echo [1/3] Cleaning old build files...
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"
del /q "SymbolFinder.spec" 2>nul

echo [2/3] Building...
"%PYTHON%" -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "SymbolFinder" ^
    --add-data "symbol_data.py;." ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    main.py

if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Build failed! See above.
    pause
    exit /b 1
)

echo [3/3] Done!
echo Executable: dist\SymbolFinder.exe
echo.
pause
