@echo off
echo ============================================
echo        DAIP-LIVE 辩论模型切换演示
echo ============================================
echo.

echo 正在检查Ollama服务...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama服务未运行，请先启动: ollama serve
    pause
    exit /b 1
)

echo ✅ Ollama服务正常运行
echo.

echo 📋 可用角色:
echo   - tech_analyst (技术分析师) - llama3:8b
echo   - ethics_expert (伦理专家) - mistral:7b
echo   - pro_arguer (正方辩手) - llama3:8b
echo   - con_arguer (反方辩手) - mistral:7b
echo.

echo 🚀 启动DAIP-LIVE TUI...
echo.
echo 💡 使用提示:
echo    1. 输入: /debate start AI伦理问题 --roles tech_analyst,ethics_expert --rounds 2
echo    2. 观察底部状态栏的模型切换
echo    3. 按 Ctrl+C 退出
echo.

python -m daip_live.cli

echo.
echo 感谢体验DAIP-LIVE辩论系统！
pause