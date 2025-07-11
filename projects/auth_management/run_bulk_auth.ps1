# PowerShell скрипт для удобного запуска массовой авторизации
param(
    [switch]$Headless,      # Скрытый режим браузера
    [switch]$Force,         # Принудительная переавторизация
    [string]$CsvPath = "",  # Путь к CSV файлу
    [switch]$Help           # Показать справку
)

# Цвета для вывода
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"

function Show-Help {
    Write-Host "=" * 60 -ForegroundColor $Cyan
    Write-Host "  МАССОВАЯ АВТОРИЗАЦИЯ - PowerShell скрипт" -ForegroundColor $Cyan
    Write-Host "=" * 60 -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "Использование:" -ForegroundColor $Yellow
    Write-Host "  .\run_bulk_auth.ps1                    # Визуальный режим"
    Write-Host "  .\run_bulk_auth.ps1 -Headless          # Скрытый режим"
    Write-Host "  .\run_bulk_auth.ps1 -Force             # Принудительная переавторизация"
    Write-Host "  .\run_bulk_auth.ps1 -Headless -Force   # Скрытый + принудительный"
    Write-Host "  .\run_bulk_auth.ps1 -CsvPath 'path\to\file.csv'  # Другой CSV файл"
    Write-Host ""
    Write-Host "Параметры:" -ForegroundColor $Yellow
    Write-Host "  -Headless    Запуск браузера в скрытом режиме"
    Write-Host "  -Force       Принудительная переавторизация всех пользователей"
    Write-Host "  -CsvPath     Путь к CSV файлу (по умолчанию: data\bulk_users.csv)"
    Write-Host "  -Help        Показать эту справку"
    Write-Host ""
}

if ($Help) {
    Show-Help
    exit 0
}

# Устанавливаем рабочую директорию
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Определяем путь к CSV файлу
if ($CsvPath -eq "") {
    $CsvPath = "data\bulk_users.csv"
}

# Проверяем существование CSV файла
if (-not (Test-Path $CsvPath)) {
    Write-Host "ОШИБКА: CSV файл не найден: $CsvPath" -ForegroundColor $Red
    Write-Host "Убедитесь, что файл существует или укажите правильный путь с -CsvPath" -ForegroundColor $Red
    exit 1
}

# Формируем описание режима
$ModeInfo = @()
if ($Headless) {
    $ModeInfo += "СКРЫТЫЙ режим"
} else {
    $ModeInfo += "ВИЗУАЛЬНЫЙ режим"
}

if ($Force) {
    $ModeInfo += "ПРИНУДИТЕЛЬНАЯ переавторизация"
} else {
    $ModeInfo += "пропуск пользователей с действующими куками"
}

# Выводим информацию о запуске
Write-Host "=" * 60 -ForegroundColor $Cyan
Write-Host "  МАССОВАЯ АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЕЙ" -ForegroundColor $Cyan
Write-Host "=" * 60 -ForegroundColor $Cyan
Write-Host "Файл CSV: $CsvPath" -ForegroundColor $Yellow
Write-Host "Режим: $($ModeInfo -join ', ')" -ForegroundColor $Yellow
Write-Host "=" * 60 -ForegroundColor $Cyan

# Подтверждение для принудительного режима
if ($Force) {
    Write-Host ""
    Write-Host "⚠️  ВНИМАНИЕ: Принудительный режим переавторизует ВСЕХ пользователей!" -ForegroundColor $Yellow
    Write-Host "   Это может занять значительное время..." -ForegroundColor $Yellow
    
    $Response = Read-Host "`nПродолжить? (y/N)"
    if ($Response -notin @('y', 'yes', 'Y', 'YES', 'да', 'Да')) {
        Write-Host "Операция отменена." -ForegroundColor $Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "🚀 Запуск авторизации..." -ForegroundColor $Green
Write-Host "   Браузер: $(if ($Headless) { 'скрытый' } else { 'видимый' })" -ForegroundColor $Green
Write-Host "   Переавторизация: $(if ($Force) { 'принудительная' } else { 'умная' })" -ForegroundColor $Green
Write-Host ""

# Формируем команду Python
$PythonArgs = @("scripts\authorize_users_from_csv.py", "`"$CsvPath`"")

if ($Headless) {
    $PythonArgs += "--headless"
}

if ($Force) {
    $PythonArgs += "--relogin"
}

# Запускаем Python скрипт
try {
    & python $PythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor $Green
        Write-Host "  АВТОРИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!" -ForegroundColor $Green
        Write-Host "=" * 60 -ForegroundColor $Green
    } else {
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor $Red
        Write-Host "  АВТОРИЗАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ!" -ForegroundColor $Red
        Write-Host "=" * 60 -ForegroundColor $Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "КРИТИЧЕСКАЯ ОШИБКА: $_" -ForegroundColor $Red
    exit 1
}
