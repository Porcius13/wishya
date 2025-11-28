@echo off
echo ========================================
echo   Favit - Farkli Lokalde Calistirma
echo ========================================
echo.

REM Port numarasını buradan değiştirebilirsiniz
set PORT=8080
set HOST=0.0.0.0
set DEBUG=True

echo Port: %PORT%
echo Host: %HOST%
echo Debug: %DEBUG%
echo.
echo Uygulama baslatiliyor...
echo URL: http://localhost:%PORT%
echo.

python run.py

pause

