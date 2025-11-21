@echo off
title Hermes
color 0A

echo.
echo ========================================
echo              HERMES
echo    Envio automatico de WhatsApp
echo ========================================
echo.
echo Iniciando...
echo.

:: Verificar errores de sintaxis antes de ejecutar
python -m py_compile Hermes.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo  Se detecto un error de sintaxis en Hermes.py
    echo  Asegurate de que el archivo no tenga marcadores git o cambios incompletos.
    echo  Vuelve a descargar el proyecto si el problema continua.
    echo ========================================
    pause
    exit /b 1
)

python Hermes.py

pause
