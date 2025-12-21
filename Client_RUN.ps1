# KAD amuled Demon Client Runner by L'.L'.

function Show-WelcomeMessage {
    Write-Host "KAD amuled Demon Client by L'.L'." -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "██████████████████░░" -ForegroundColor DarkYellow
    Write-Host "██████████████████░░" -ForegroundColor DarkYellow
    Write-Host "██    ██████    ██░░" -ForegroundColor DarkYellow
    Write-Host "██      ██      ██░░" -ForegroundColor DarkYellow
    Write-Host "██  ██      ██  ██░░" -ForegroundColor DarkYellow
    Write-Host "██  ██  ██  ██  ██░░" -ForegroundColor DarkYellow
    Write-Host "██    ██    ██    ██░░" -ForegroundColor DarkYellow
    Write-Host "██████████████████░░" -ForegroundColor DarkYellow
    Write-Host "██████████████████░░" -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "Decentralized P2P amule-daemon via KAD/eD2k network." -ForegroundColor DarkYellow
    Write-Host ""
}

try {
    Show-WelcomeMessage

    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $venvPath   = Join-Path $scriptPath ".venv"
    $clientPath = Join-Path $scriptPath "test_client.py"

    if (!(Test-Path $venvPath)) {
        Write-Host "[CLIENT] ERROR: Среда KAD-amuled-demon не установлена." -ForegroundColor Red
        Write-Host "[CLIENT] INFO: Запустите KAD_Amuled_Demon_Installer.ps1 для установки." -ForegroundColor Yellow
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }

    if (!(Test-Path $clientPath)) {
        Write-Host "[CLIENT] ERROR: test_client.py не найден в папке скрипта." -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }

    Write-Host "[CLIENT] INFO: Запуск test_client.py..." -ForegroundColor Green
    & "$venvPath\Scripts\python.exe" $clientPath

    # ←←← КЛЮЧЕВОЕ ДОБАВЛЕНИЕ: проверка кода возврата Python-скрипта
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[CLIENT] ERROR: test_client.py завершился с ошибкой (код: $LASTEXITCODE)." -ForegroundColor Red
        Write-Host "[CLIENT] INFO: Проверьте логи или сообщения выше." -ForegroundColor Yellow
        Read-Host "Нажмите Enter для выхода"
        exit $LASTEXITCODE
    } else {
        Write-Host "[CLIENT] INFO: test_client.py завершился успешно." -ForegroundColor Green
    }

} catch {
    Write-Host "[CLIENT] ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}