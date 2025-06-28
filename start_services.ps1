# 启动校园二手交易平台服务
Write-Host "正在启动校园二手交易平台..." -ForegroundColor Green

# 启动后端服务
Write-Host "启动后端服务..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Minimized

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Yellow
Set-Location frontend
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Minimized

# 返回根目录
Set-Location ..

Write-Host "服务启动完成！" -ForegroundColor Green
Write-Host "后端API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "前端应用: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan

# 保持脚本运行
Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor Red
try {
    while ($true) {
        Start-Sleep -Seconds 10
    }
} catch {
    Write-Host "正在停止服务..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | Stop-Process -Force
    Write-Host "服务已停止" -ForegroundColor Green
} 