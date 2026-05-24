@echo off
:: Desplazarse al directorio del proyecto local
cd /d "%~dp0"

:: Comprobar si ya hay una instancia escuchando activamente en el puerto 8000
netstat -ano | findstr :8000 | findstr LISTENING > nul
if %errorlevel% equ 0 goto server_active

echo [Mónica] Iniciando servidor en segundo plano...
start /min "" "venv\Scripts\python.exe" "web_app.py"

:: Esperar a que el servidor FastAPI levante y escuche activamente en el puerto 8000
:wait_loop
ping -n 2 127.0.0.1 > nul
netstat -ano | findstr :8000 | findstr LISTENING > nul
if %errorlevel% neq 0 goto wait_loop
goto end

:server_active
echo [Mónica] El servidor ya se encuentra activo.

:end
:: Abrir automáticamente la interfaz premium en Microsoft Edge (modo App)
echo [Mónica] Abriendo interfaz de usuario...
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=https://127.0.0.1:8000 --ignore-certificate-errors
exit /b
