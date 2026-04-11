@echo off
echo ===================================
echo 亚马逊AIGC产品图智能生成助手 DEMO
echo ===================================
echo.

echo 正在检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo 正在检查npm环境...
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到npm，请检查Node.js安装
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
npm install

if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)

echo.
echo 依赖包安装成功！
echo 正在启动开发服务器...
echo.
echo 应用将在 http://localhost:3000 启动
echo 按 Ctrl+C 可停止服务器
echo.

npm run dev

pause





