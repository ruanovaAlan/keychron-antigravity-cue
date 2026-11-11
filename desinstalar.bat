@echo off
chcp 65001 > nul
echo Desinstalando integración de Keychron con Antigravity...
if exist "%USERPROFILE%\Desktop\Configurar Luces Keychron.bat" del "%USERPROFILE%\Desktop\Configurar Luces Keychron.bat"
if exist "%USERPROFILE%\.gemini\config\hooks.json" del "%USERPROFILE%\.gemini\config\hooks.json"
echo.
echo Desinstalación completada. Se eliminaron los hooks y el acceso directo.
pause
