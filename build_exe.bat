@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo        ReadMe Hero - EXE Builder
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv was not found.
    echo Create/activate the project virtual environment first.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Could not activate .venv.
    pause
    exit /b 1
)

echo [1/3] Installing/updating PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo [ERROR] PyInstaller installation failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Building ReadMeHero.exe...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
python -m PyInstaller "ReadMeHero.spec" --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] EXE build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Build completed successfully.
echo.
echo EXE: %CD%\dist\ReadMeHero.exe
if exist "dist\ReadMeHero.exe" (
    for %%A in ("dist\ReadMeHero.exe") do echo Size: %%~zA bytes
)
echo.
echo You can now run dist\ReadMeHero.exe
pause
endlocal
