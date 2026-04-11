@echo off
echo ========================================
echo 停止所有Python进程
echo ========================================
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo 清理数据库缓存
echo ========================================
cd instance
if exist aigc_assistant.db-shm del aigc_assistant.db-shm
if exist aigc_assistant.db-wal del aigc_assistant.db-wal
cd ..

echo.
echo ========================================
echo 启动后端服务器
echo ========================================
python app.py

