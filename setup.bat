@echo off
REM Script de instalación para el proyecto Mónica en Windows

echo Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual.
    exit /b 1
)

echo Activando entorno virtual e instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Instalando navegadores de Playwright...
playwright install

echo ---------------------------------------------------------------
echo Instalación completada. Use "venv\Scripts\activate.bat" para activar.
echo Ejecutar "python web_app.py" para iniciar la interfaz web.
echo ---------------------------------------------------------------
