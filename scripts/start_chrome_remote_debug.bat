@echo off
echo ============================================
echo    Chrome DevTools MCP - Remote Debug Mode
echo ============================================
echo.
echo This script starts Chrome with remote debugging enabled
echo so that Chrome DevTools MCP can connect to your existing browser.
echo.
echo After Chrome opens, you can use:
echo - chrome-devtools-remote MCP server in KiloKode/Cline
echo - Open new tabs in your existing browser session
echo - Record user actions and generate test code
echo.
echo Press any key to start Chrome...
pause >nul

echo Starting Chrome with remote debugging on port 9222...
echo.
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-remote-debug"
echo.
echo ============================================
echo Chrome started successfully!
echo.
echo Remote debugging URL: http://127.0.0.1:9222
echo.
echo You can now use chrome-devtools-remote MCP server
echo to control this browser instance.
echo.
echo To stop: Close the Chrome window or press Ctrl+C here
echo ============================================
pause