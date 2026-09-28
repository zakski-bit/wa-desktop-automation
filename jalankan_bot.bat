@echo off
title WA Mentoring Sender
chcp 65001 >nul
cd /d "%~dp0"
echo ===================================================
echo     Membuka WA Mentoring Sender Automation...
echo ===================================================
python wa_sender.py
pause
