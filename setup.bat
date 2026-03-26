@echo off
setlocal EnableDelayedExpansion

:: ============================================================================
:: StimTool3 Setup Script
:: Automates PsychoPy installation, virtual environment creation, dependency
:: installation, and environment configuration for running StimTool3.
:: ============================================================================

set "PSYCHOPY_VERSION=2020.1.3"
set "PSYCHOPY_INSTALL_DIR=C:\Program Files\PsychoPy3"
set "PSYCHOPY_PYTHON=%PSYCHOPY_INSTALL_DIR%\python.exe"
set "STIMTOOL_DIR=%~dp0"
set "INSTALLER_NAME=StandalonePsychoPy3-%PSYCHOPY_VERSION%-win64.exe"
set "INSTALLER_URL=https://github.com/psychopy/psychopy/releases/download/%PSYCHOPY_VERSION%/%INSTALLER_NAME%"
set "INSTALLER_PATH=%TEMP%\%INSTALLER_NAME%"

set "VENV_DIR=C:\StimTool3Env"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat"

@REM set "LJM_INSTALLER_NAME=LabJack-2019-05-20.exe"
@REM set "LJM_INSTALLER_URL=https://labjack.com/sites/default/files/software/%LJM_INSTALLER_NAME%"
set "LJM_INSTALLER_NAME=LabJackBasic_2025-02-12.exe"
set "LJM_INSTALLER_URL=https://files.labjack.com/installers/LJM/Windows/x86_64/beta/%LJM_INSTALLER_NAME%"
set "LJM_INSTALLER_PATH=%TEMP%\%LJM_INSTALLER_NAME%"

set "PASS=0"
set "FAIL=0"
set "WARN=0"

echo.
echo ============================================================
echo   StimTool3 Setup
echo ============================================================
echo.

:: ------------------------------------------------------------------
:: Step 1: Check / Install PsychoPy
:: ------------------------------------------------------------------
echo [Step 1/6] Checking PsychoPy installation...
echo.

if exist "%PSYCHOPY_PYTHON%" (
    echo   [OK] PsychoPy3 found at %PSYCHOPY_INSTALL_DIR%
    set /a PASS+=1
    goto :check_psychopy_version
) else (
    echo   PsychoPy3 not found at expected location.
    echo.
    goto :install_psychopy
)

:install_psychopy
echo   StimTool3 requires PsychoPy %PSYCHOPY_VERSION%.
echo.
set /p INSTALL_CHOICE="   Would you like to download and install it now? (Y/N): "
if /i not "%INSTALL_CHOICE%"=="Y" (
    echo.
    echo   Skipping PsychoPy installation.
    echo   You will need to install PsychoPy %PSYCHOPY_VERSION% manually before running StimTool3.
    echo   Download from: %INSTALLER_URL%
    set /a FAIL+=1
    goto :setup_venv
)

echo.
echo   Downloading PsychoPy %PSYCHOPY_VERSION%...
echo   URL: %INSTALLER_URL%
echo   This may take several minutes depending on your connection.
echo.

:: Try PowerShell download (available on all modern Windows)
powershell -Command "& { $ProgressPreference = 'SilentlyContinue'; try { Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%INSTALLER_PATH%' -UseBasicParsing; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 } }"

if %ERRORLEVEL% neq 0 (
    echo.
    echo   [FAIL] Download failed. Please check your internet connection.
    echo   You can download manually from: %INSTALLER_URL%
    set /a FAIL+=1
    goto :setup_venv
)

echo   Download complete.
echo.
echo   Installing PsychoPy %PSYCHOPY_VERSION%...
echo   (The installer window may appear -- please follow any prompts)
echo.

:: Run the installer. /S = silent mode for NSIS installers.
:: /D sets the install directory (must be last parameter for NSIS).
"%INSTALLER_PATH%" /S /D=%PSYCHOPY_INSTALL_DIR%

:: Wait briefly for the installation to complete
timeout /t 5 /nobreak >nul

if exist "%PSYCHOPY_PYTHON%" (
    echo   [OK] PsychoPy %PSYCHOPY_VERSION% installed successfully.
    set /a PASS+=1
    del "%INSTALLER_PATH%" 2>nul
) else (
    echo   [FAIL] Installation may not have completed successfully.
    echo   Please verify that PsychoPy is installed at: %PSYCHOPY_INSTALL_DIR%
    echo   You can run the installer manually from: %INSTALLER_PATH%
    set /a FAIL+=1
    goto :setup_venv
)

:check_psychopy_version
:: Verify the installed PsychoPy version matches what we expect
"%PSYCHOPY_PYTHON%" -c "import psychopy; print(psychopy.__version__)" 2>nul | findstr /C:"%PSYCHOPY_VERSION%" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   [OK] PsychoPy version confirmed: %PSYCHOPY_VERSION%
    set /a PASS+=1
) else (
    echo   [WARN] Could not confirm PsychoPy version is %PSYCHOPY_VERSION%.
    echo          StimTool3 is tested against this version; other versions may have issues.
    set /a WARN+=1
)

:: ------------------------------------------------------------------
:: Step 2: Create StimTool3 virtual environment
:: ------------------------------------------------------------------
:setup_venv
echo.
echo [Step 2/6] Setting up StimTool3 virtual environment...
echo.
echo   StimTool3 uses a virtual environment at %VENV_DIR% for additional
echo   packages (opencv, pyaudio, etc.) that are not bundled with PsychoPy.
echo.

if not exist "%PSYCHOPY_PYTHON%" (
    echo   [SKIP] Cannot create venv -- PsychoPy Python not found.
    set /a FAIL+=1
    goto :install_labjack
)

if exist "%VENV_PYTHON%" (
    echo   [OK] Virtual environment already exists at %VENV_DIR%
    set /a PASS+=1
    goto :install_venv_packages
) else (
    echo   Creating virtual environment using PsychoPy's Python...
    "%PSYCHOPY_PYTHON%" -m venv "%VENV_DIR%"

    if exist "%VENV_PYTHON%" (
        echo   [OK] Virtual environment created at %VENV_DIR%
        set /a PASS+=1
    ) else (
        echo   [FAIL] Failed to create virtual environment.
        echo          You can create it manually with:
        echo          "%PSYCHOPY_PYTHON%" -m venv "%VENV_DIR%"
        set /a FAIL+=1
        goto :install_labjack
    )
)

:install_venv_packages
echo.
echo   Installing packages into virtual environment...
echo.

:: Install opencv-python (pinned version for compatibility)
"%VENV_PYTHON%" -c "import cv2" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] opencv-python already installed.
    set /a PASS+=1
) else (
    echo   Installing opencv-python==4.4.0.42...
    "%VENV_PYTHON%" -m pip install opencv-python==4.4.0.42 2>nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] opencv-python installed.
        set /a PASS+=1
    ) else (
        echo   [WARN] Failed to install opencv-python. You can install manually:
        echo          "%VENV_PYTHON%" -m pip install opencv-python==4.4.0.42
        set /a WARN+=1
    )
)

:: Install pyaudio (pinned version for compatibility)
"%VENV_PYTHON%" -c "import pyaudio" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] pyaudio already installed.
    set /a PASS+=1
) else (
    echo   Installing pyaudio==0.2.11...
    "%VENV_PYTHON%" -m pip install pyaudio==0.2.11 2>nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] pyaudio installed.
        set /a PASS+=1
    ) else (
        echo   [WARN] Failed to install pyaudio. You can install manually:
        echo          "%VENV_PYTHON%" -m pip install pyaudio==0.2.11
        set /a WARN+=1
    )
)

:: ------------------------------------------------------------------
:: Step 3: Check / Install LabJack LJM Driver and Python package
:: ------------------------------------------------------------------
:install_labjack
echo.
echo [Step 3/6] Checking LabJack LJM setup...
echo.
echo   Some StimTool3 tasks require a LabJack device for respiratory
echo   sensing and hardware control. This step is optional if you do
echo   not plan to use LabJack hardware.
echo.

:: Check if LJM driver DLL is already installed
set "LJM_FOUND=0"
if exist "C:\Windows\System32\LabJackM.dll" set "LJM_FOUND=1"
if exist "C:\Program Files (x86)\LabJack\Drivers\LabJackM.dll" set "LJM_FOUND=1"

if "%LJM_FOUND%"=="1" (
    echo   [OK] LabJack LJM driver found.
    set /a PASS+=1
    goto :check_ljm_python
) else (
    echo   LabJack LJM driver not found.
    echo.
    set /p LJM_CHOICE="   Would you like to download and install the LabJack LJM driver? (Y/N): "
    if /i not "!LJM_CHOICE!"=="Y" (
        echo.
        echo   Skipping LabJack driver installation.
        echo   Tasks that require LabJack hardware will not be available.
        goto :check_ljm_python
    )
    goto :do_install_ljm
)

:do_install_ljm
echo.
echo   Downloading LabJack LJM driver...
echo   URL: %LJM_INSTALLER_URL%
echo.

powershell -Command "& { $ProgressPreference = 'SilentlyContinue'; try { Invoke-WebRequest -Uri '%LJM_INSTALLER_URL%' -OutFile '%LJM_INSTALLER_PATH%' -UseBasicParsing; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 } }"

if %ERRORLEVEL% neq 0 (
    echo   [WARN] Download failed. You can install the LabJack LJM driver manually from:
    echo          https://labjack.com/support/software/installers/ljm
    set /a WARN+=1
    goto :check_ljm_python
)

echo   Download complete.
echo   Running LabJack LJM installer...
echo   (Please follow the installer prompts)
echo.

:: LabJack installer -- attempt silent install
"%LJM_INSTALLER_PATH%" /S

timeout /t 5 /nobreak >nul

set "LJM_FOUND=0"
if exist "C:\Windows\System32\LabJackM.dll" set "LJM_FOUND=1"
if exist "C:\Program Files (x86)\LabJack\Drivers\LabJackM.dll" set "LJM_FOUND=1"

if "%LJM_FOUND%"=="1" (
    echo   [OK] LabJack LJM driver installed successfully.
    set /a PASS+=1
    del "%LJM_INSTALLER_PATH%" 2>nul
) else (
    echo   [WARN] Could not confirm LabJack LJM driver installation.
    echo          You can install manually from: https://labjack.com/support/software/installers/ljm
    set /a WARN+=1
)

:check_ljm_python
:: Install the labjack-ljm Python package into the venv if available
if not exist "%VENV_PYTHON%" (
    if not exist "%PSYCHOPY_PYTHON%" goto :verify_deps
    REM Fall back to PsychoPy Python if no venv
    set "LJM_PIP_PYTHON=%PSYCHOPY_PYTHON%"
) else (
    set "LJM_PIP_PYTHON=%VENV_PYTHON%"
)

"%LJM_PIP_PYTHON%" -c "from labjack import ljm" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] labjack-ljm Python package found.
    set /a PASS+=1
) else (
    echo   labjack-ljm Python package not found.
    set /p LJM_PIP_CHOICE="   Install labjack-ljm Python package now? (Y/N): "
    if /i "!LJM_PIP_CHOICE!"=="Y" (
        echo   Installing labjack-ljm...
        "%LJM_PIP_PYTHON%" -m pip install labjack-ljm 2>nul
        if !ERRORLEVEL! equ 0 (
            echo   [OK] labjack-ljm Python package installed.
            set /a PASS+=1
        ) else (
            echo   [WARN] Failed to install labjack-ljm. You can install manually:
            echo          "%LJM_PIP_PYTHON%" -m pip install labjack-ljm
            set /a WARN+=1
        )
    ) else (
        echo   Skipping labjack-ljm installation.
    )
)

:: ------------------------------------------------------------------
:: Step 4: Verify Python dependencies
:: ------------------------------------------------------------------
:verify_deps
echo.
echo [Step 4/6] Verifying Python dependencies...
echo.

if not exist "%PSYCHOPY_PYTHON%" (
    echo   [SKIP] Cannot verify dependencies -- PsychoPy Python not found.
    set /a FAIL+=1
    goto :verify_stimtool
)

:: Core dependencies (should come with PsychoPy standalone)
echo   PsychoPy environment (using %PSYCHOPY_PYTHON%):
for %%P in (numpy psychopy serial pygame) do (
    "%PSYCHOPY_PYTHON%" -c "import %%P" 2>nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] %%P
        set /a PASS+=1
    ) else (
        echo   [FAIL] %%P -- not found
        set /a FAIL+=1
    )
)

:: Optional PsychoPy dependencies
for %%P in (pandas) do (
    "%PSYCHOPY_PYTHON%" -c "import %%P" 2>nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] %%P
        set /a PASS+=1
    ) else (
        echo   [WARN] %%P -- not found (optional, needed by some tasks)
        set /a WARN+=1
    )
)

REM Venv dependencies
if not exist "%VENV_PYTHON%" goto :skip_venv_check
echo.
echo   Virtual environment (using %VENV_PYTHON%):
for %%P in (cv2 pyaudio) do (
    "%VENV_PYTHON%" -c "import %%P" 2>nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] %%P
        set /a PASS+=1
    ) else (
        echo   [FAIL] %%P -- not found in venv
        set /a FAIL+=1
    )
)
:skip_venv_check

echo.
echo   Optional hardware packages (only needed if using the associated hardware):
for %%P in (pylink) do (
    "%PSYCHOPY_PYTHON%" -c "import %%P" 2>nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] %%P
        set /a PASS+=1
    ) else (
        echo   [--] %%P -- not installed (only needed for EyeLink hardware)
    )
)

:: ------------------------------------------------------------------
:: Step 5: Verify StimTool3 can load
:: ------------------------------------------------------------------
:verify_stimtool
echo.
echo [Step 5/6] Verifying StimTool3 environment...
echo.

if not exist "%PSYCHOPY_PYTHON%" (
    echo   [SKIP] Cannot verify -- PsychoPy Python not found.
    set /a FAIL+=1
    goto :create_shortcut
)

:: Check that StimToolLib can be imported
"%PSYCHOPY_PYTHON%" -c "import sys; sys.path.insert(0, r'%STIMTOOL_DIR%.'); import StimToolLib" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] StimToolLib loads successfully.
    set /a PASS+=1
) else (
    echo   [WARN] StimToolLib did not import cleanly.
    echo          This may be due to missing hardware drivers (parallel port, serial)
    echo          which is normal if you are not connected to that hardware.
    set /a WARN+=1
)

:: Check that key files exist
if exist "%STIMTOOL_DIR%StimTool.py" (
    echo   [OK] StimTool.py found.
    set /a PASS+=1
) else (
    echo   [FAIL] StimTool.py not found in %STIMTOOL_DIR%
    set /a FAIL+=1
)

if exist "%STIMTOOL_DIR%StimToolLib.py" (
    echo   [OK] StimToolLib.py found.
    set /a PASS+=1
) else (
    echo   [FAIL] StimToolLib.py not found in %STIMTOOL_DIR%
    set /a FAIL+=1
)

if exist "%STIMTOOL_DIR%Default.params" (
    echo   [OK] Default.params found.
    set /a PASS+=1
) else (
    echo   [FAIL] Default.params not found in %STIMTOOL_DIR%
    set /a FAIL+=1
)

if exist "%STIMTOOL_DIR%ParameterSelector" (
    echo   [OK] ParameterSelector directory found.
    set /a PASS+=1
) else (
    echo   [WARN] ParameterSelector directory not found.
    set /a WARN+=1
)

:: Check that venv path exists (tasks hardcode C:\StimTool3Env)
if exist "%VENV_DIR%" (
    echo   [OK] StimTool3Env directory found at %VENV_DIR%
    set /a PASS+=1
) else (
    echo   [WARN] %VENV_DIR% not found. Tasks using CameraDriver, video
    echo          recording, or LabJack may not work correctly.
    set /a WARN+=1
)

:: ------------------------------------------------------------------
:: Step 6: Create desktop shortcut
:: ------------------------------------------------------------------
:create_shortcut
echo.
echo [Step 6/6] Desktop shortcut...
echo.

set "SHORTCUT_PATH=%USERPROFILE%\Desktop\StimTool3.lnk"
if exist "%SHORTCUT_PATH%" (
    echo   [OK] Desktop shortcut already exists.
    set /a PASS+=1
    goto :summary
)

set /p SHORTCUT_CHOICE="   Create a desktop shortcut for StimTool3? (Y/N): "
if /i not "%SHORTCUT_CHOICE%"=="Y" (
    echo   Skipping shortcut creation.
    goto :summary
)

:: Create shortcut via PowerShell
powershell -Command "& { $ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%PSYCHOPY_PYTHON%'; $s.Arguments = 'StimTool.py'; $s.WorkingDirectory = '%STIMTOOL_DIR%.'; $s.Description = 'StimTool3'; $s.Save() }"

if exist "%SHORTCUT_PATH%" (
    echo   [OK] Desktop shortcut created.
    set /a PASS+=1
) else (
    echo   [WARN] Could not create desktop shortcut.
    set /a WARN+=1
)

:: ------------------------------------------------------------------
:: Summary
:: ------------------------------------------------------------------
:summary
echo.
echo ============================================================
echo   Setup Summary
echo ============================================================
echo.
echo   Passed:  %PASS%
echo   Warnings: %WARN%
echo   Failed:  %FAIL%
echo.

if %FAIL% gtr 0 (
    echo   Some checks FAILED. Please review the output above and address
    echo   any issues before running StimTool3.
) else if %WARN% gtr 0 (
    echo   Setup completed with warnings. StimTool3 should run, but some
    echo   optional features may not be available.
) else (
    echo   Setup completed successfully! You can now run StimTool3.
)

echo.
echo   To run StimTool3 manually:
echo     "%PSYCHOPY_PYTHON%" "%STIMTOOL_DIR%StimTool.py"
echo.
echo ============================================================
echo.

pause
endlocal
