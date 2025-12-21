# amuled_daemon.py
# V.0.0.4 — только запуск amuled.exe, без логирования
# Author: Linda MacGill aka L∴L∴

import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent
amuled = script_dir / "amuled.exe"
config_dir = script_dir / "amule-daemon-config"

if not amuled.is_file():
    sys.exit(f"[!] {amuled} не найден")

if not config_dir.is_dir():
    sys.exit(f"[!] Папка конфигурации отсутствует: {config_dir}")

# Запуск amuled.exe без перехвата stdout/stderr
subprocess.Popen([
    str(amuled), "/c", str(config_dir), "/o"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)