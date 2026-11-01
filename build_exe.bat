@echo off
setlocal

where python >nul 2>nul
if %errorlevel%==0 (
    set PY=python
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set PY=py
    ) else (
        echo Python not found. Install Python from python.org and tick "Add Python to PATH".
        pause
        exit /b 1
    )
)

echo Installing PyInstaller...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    pause
    exit /b 1
)

echo.
echo Building exe...
%PY% -m PyInstaller --onefile --windowed --name BlenderRenderQueue render_queue.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Done! Your file: dist\BlenderRenderQueue.exe
pause
