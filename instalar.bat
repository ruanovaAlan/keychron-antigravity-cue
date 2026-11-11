@echo off
chcp 65001 > nul
title Instalador Keychron Cue para Antigravity
echo ========================================================
echo  Instalador de Avisos Visuales Keychron para Antigravity
echo ========================================================
echo.

:: 1. Instalar libreria hidapi
echo [1/4] Instalando dependencias de Python (hidapi)...
pip install hidapi
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudo instalar hidapi.
    echo Asegurate de tener Python instalado y anadido al PATH de Windows.
    echo.
    pause
    exit /b %errorlevel%
)

:: 2. Crear carpeta en el perfil del usuario
echo [2/4] Copiando archivos a %USERPROFILE%\.keychron...
if not exist "%USERPROFILE%\.keychron" mkdir "%USERPROFILE%\.keychron"
copy /Y "%~dp0keychron_notifier.py" "%USERPROFILE%\.keychron\" > nul
copy /Y "%~dp0app_keychron_config.py" "%USERPROFILE%\.keychron\" > nul
if not exist "%USERPROFILE%\.keychron\config.json" copy /Y "%~dp0config.json" "%USERPROFILE%\.keychron\" > nul

:: 3. Configurar hooks globales de Antigravity
echo [3/4] Conectando con Antigravity...
if not exist "%USERPROFILE%\.gemini\config" mkdir "%USERPROFILE%\.gemini\config"

powershell -NoProfile -Command "$cmd = 'python \"' + $env:USERPROFILE.Replace('\','/') + '/.keychron/keychron_notifier.py\" --hook'; $cfg = @{ 'keychron-modes' = @{ 'enabled' = $true; 'PreInvocation' = @(@{ 'type' = 'command'; 'command' = $cmd; 'timeout' = 5 }); 'PreToolUse' = @(@{ 'matcher' = '*'; 'hooks' = @(@{ 'type' = 'command'; 'command' = $cmd; 'timeout' = 5 }) }); 'Stop' = @(@{ 'type' = 'command'; 'command' = $cmd; 'timeout' = 5 }) } }; $json = $cfg | ConvertTo-Json -Depth 6; [System.IO.File]::WriteAllText(\"$env:USERPROFILE\.gemini\config\hooks.json\", $json, [System.Text.Encoding]::UTF8)"

:: 4. Crear acceso directo en el Escritorio
echo [4/4] Creando acceso directo en el Escritorio...
(
echo @echo off
echo start pythonw "%%USERPROFILE%%\.keychron\app_keychron_config.py"
) > "%USERPROFILE%\Desktop\Configurar Luces Keychron.bat"

echo.
echo ========================================================
echo  ¡Instalación completada con éxito!
echo.
echo  1. Conecta tu teclado Keychron con el CABLE USB (modo Cable).
echo  2. Abre 'Configurar Luces Keychron.bat' en tu Escritorio
echo     para personalizar los modos de luz a tu gusto.
echo  3. ¡Tu Antigravity ya reaccionará a cada acción!
echo ========================================================
echo.
pause
