# KAD amuled Demon Installer v1.3 by L'.L'.
# Версия с логированием в лаунчере, без uv в системе

function Show-WelcomeMessage {
    Write-Host "KAD amuled Demon Installer v1.3 by L'.L'." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host "██    ██████    ██░░" -ForegroundColor Cyan
    Write-Host "██      ██      ██░░" -ForegroundColor Cyan
    Write-Host "██  ██      ██  ██░░" -ForegroundColor Cyan
    Write-Host "██  ██  ██  ██  ██░░" -ForegroundColor Cyan
    Write-Host "██    ██    ██    ██░░" -ForegroundColor Cyan
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host "██████████████████░░" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Decentralized P2P amule-daemon via KAD/eD2k network." -ForegroundColor Cyan
    Write-Host ""
}

# Зеркало Aliyun
$env:PIP_INDEX_URL = "https://mirrors.aliyun.com/pypi/simple/"
$env:UV_INDEX_URL = "https://mirrors.aliyun.com/pypi/simple/"

function Test-Environment {
    Write-Host "[SETUP] INFO: Проверка Python..." -ForegroundColor Blue
    if (!(Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "[SETUP] ERROR: Python не найден!" -ForegroundColor Red
        return $false
    }
    Write-Host "[SETUP] OK: Python найден." -ForegroundColor Green
    return $true
}

function Test-Venv {
    param([string]$venvPath)
    if (!(Test-Path $venvPath)) {
        Write-Host "[SETUP] INFO: Создание виртуальной среды (.venv)..." -ForegroundColor Yellow
        python -m venv $venvPath
    } else {
        Write-Host "[SETUP] OK: Виртуальная среда уже существует." -ForegroundColor Green
    }
}

function Install-Uv {
    param([string]$venvPath, [string]$proxy = $null)

    Write-Host "[SETUP] INFO: Установка uv в виртуальную среду..." -ForegroundColor Blue

    $old_http_proxy = $env:HTTP_PROXY
    $old_https_proxy = $env:HTTPS_PROXY

    if ($proxy) {
        $env:HTTP_PROXY = $proxy
        $env:HTTPS_PROXY = $proxy
        Write-Host "[SETUP] INFO: Используется прокси при установке uv: $proxy" -ForegroundColor Yellow
    }

    & "$venvPath\Scripts\python.exe" -m pip install --quiet uv

    $env:HTTP_PROXY = $old_http_proxy
    $env:HTTPS_PROXY = $old_https_proxy
}

function Install-Dependencies {
    param([string]$venvPath, [string]$proxy = $null)

    Write-Host "[SETUP] INFO: Установка зависимостей через uv..." -ForegroundColor Blue

    $old_http_proxy = $env:HTTP_PROXY
    $old_https_proxy = $env:HTTPS_PROXY

    if ($proxy) {
        $env:HTTP_PROXY = $proxy
        $env:HTTPS_PROXY = $proxy
        Write-Host "[SETUP] INFO: Используется прокси при установке зависимостей: $proxy" -ForegroundColor Yellow
    }

    & "$venvPath\Scripts\uv.exe" pip install requests beautifulsoup4 lxml

    $env:HTTP_PROXY = $old_http_proxy
    $env:HTTPS_PROXY = $old_https_proxy
}

function Get-UserInput {
    Write-Host "[SETUP] INFO: Настройка путей для apply_amule_config.py..." -ForegroundColor Blue

    $proxy = Read-Host "Прокси (например, http://127.0.0.1:18080, или Enter для пропуска)"
    if ($proxy -eq "") { $proxy = $null }

    $videoPlayer = Read-Host "Путь к VLC (VideoPlayer) [по умолчанию: H:\Program Files\VLC_105-emule\vlc.exe]"
    if ($videoPlayer -eq "") {
        $videoPlayer = "H:\Program Files\VLC_105-emule\vlc.exe"
    }

    $incoming = Read-Host "IncomingDir (папка для загрузок)"
    while (!(Test-Path $incoming)) {
        $create = Read-Host "Папка '$incoming' не найдена. Создать? (y/n)"
        if ($create -eq "y") {
            New-Item -ItemType Directory -Path $incoming -Force | Out-Null
            break
        }
        $incoming = Read-Host "IncomingDir"
    }

    $temp = Read-Host "TempDir (временная папка)"
    while (!(Test-Path $temp)) {
        $create = Read-Host "Папка '$temp' не найдена. Создать? (y/n)"
        if ($create -eq "y") {
            New-Item -ItemType Directory -Path $temp -Force | Out-Null
            break
        }
        $temp = Read-Host "TempDir"
    }

    return @{
        proxy        = $proxy
        videoPlayer  = $videoPlayer
        incomingDir  = $incoming
        tempDir      = $temp
    }
}

# === Функция отслеживания лога ===
function Watch-Log {
    param([string]$LogPath)

    Write-Host "[LOG] Ожидание создания лог-файла: $LogPath" -ForegroundColor DarkGray
    while (!(Test-Path $LogPath)) {
        Start-Sleep -Seconds 1
    }
    Write-Host "[LOG] Файл создан. Начинаю вывод в реальном времени..." -ForegroundColor DarkGray

    Get-Content $LogPath -Encoding Default -Wait | ForEach-Object {
        $line = $_

        # Обработка "Сообщение сервера"
        if ($line -match '^\s*[\d!][\d\-:\s]+: Сообщение сервера: (.+)$') {
            $msg = $matches[1]
            $timestampPart = $line -replace ': Сообщение сервера:.*', ''
            Write-Host "[SERVER] ${timestampPart}: $msg" -ForegroundColor Cyan
            return
        }

        # Определяем цвет по ключевым словам
        if ($line -match '.*: Прием ') {
            Write-Host "[LOG] $line" -ForegroundColor Yellow
        }
        elseif ($line -match '.*: Загрузка завершена:') {
            Write-Host "[LOG] $line" -ForegroundColor Green
        }
        elseif ($line -match '.*: Ошибка') {
            Write-Host "[LOG] $line" -ForegroundColor Red
        }
        elseif ($line -match '.*: ПРЕДУПРЕЖДЕНИЕ:') {
            Write-Host "[LOG] $line" -ForegroundColor White
        }
        else {
            # Все остальные строки — серым (DarkGray)
            Write-Host "[LOG] $line" -ForegroundColor DarkGray
        }
    }
}

# === Основной блок ===
try {
    Show-WelcomeMessage

    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $venvPath   = Join-Path $scriptPath ".venv"
    $daemonPath = Join-Path $scriptPath "amuled_daemon.py"
    $configPath = Join-Path $scriptPath "apply_amule_config.py"
    $logPath    = Join-Path $scriptPath "amule-daemon-config\logfile"

    if (!(Test-Environment)) { exit 1 }
    Test-Venv -venvPath $venvPath

    # === БЫСТРЫЙ СТАРТ ===
    if (Test-Path $daemonPath) {
        Write-Host "[SETUP] OK: Найден amuled_daemon.py — запуск демона..." -ForegroundColor Green
        & "$venvPath\Scripts\python.exe" $daemonPath

        # Запуск отслеживания лога
        Watch-Log -LogPath $logPath
        exit 0
    }

    # === ПОЛНАЯ УСТАНОВКА ===
    if (!(Test-Path $configPath)) {
        Write-Host "[SETUP] ERROR: apply_amule_config.py не найден!" -ForegroundColor Red
        exit 1
    }

    $user = Get-UserInput

    Install-Uv -venvPath $venvPath -proxy $user.proxy
    Install-Dependencies -venvPath $venvPath -proxy $user.proxy

    Write-Host "[SETUP] INFO: Запуск apply_amule_config.py..." -ForegroundColor Blue
    & "$venvPath\Scripts\python.exe" $configPath $user.videoPlayer $user.incomingDir $user.tempDir

    Write-Host "`n[SETUP] OK: Установка завершена. Запуск демона..." -ForegroundColor Green
    if (Test-Path $daemonPath) {
        & "$venvPath\Scripts\python.exe" $daemonPath
    } else {
        Write-Host "[SETUP] WARN: amuled_daemon.py не найден!" -ForegroundColor Yellow
    }

    # Отслеживание лога
    Watch-Log -LogPath $logPath

} catch {
    Write-Host "[SETUP] ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}