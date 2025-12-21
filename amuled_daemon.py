# amuled_daemon.py:
# V.0.0.2
# Author: Linda MacGill aka L∴L∴

import subprocess
import sys
import threading
import ctypes
from pathlib import Path

# Кодировка вывода aMule (ANSI для wxBase на Windows)
CONSOLE_ENCODING = 'cp1251'

def read_output(pipe, name):
    try:
        for line in iter(pipe.readline, b''):
            text = line.decode(CONSOLE_ENCODING, errors='replace').rstrip()
            print(f"[{name}] {text}")
        pipe.close()
    except Exception as e:
        print(f"[!] Ошибка чтения {name}: {e}", file=sys.stderr)

# Пути
script_dir = Path(__file__).parent
amuled = script_dir / "amuled.exe"
config_dir = script_dir / "amule-daemon-config"

# Проверка наличия amuled.exe
if not amuled.is_file():
    print(f"[!] {amuled} не найден", file=sys.stderr)
    sys.exit(1)

# Проверка наличия папки конфигурации
if not config_dir.is_dir():
    print(f"[!] Папка конфигурации не найдена: {config_dir}", file=sys.stderr)
    print("[!] Создайте папку 'amule-daemon-config' и поместите туда файлы aMule (preferences.dat и др.)", file=sys.stderr)
    sys.exit(1)

# Формируем аргументы: обязательно /o для вывода в stdout
args = [str(amuled), "/c", str(config_dir), "/o"]

# Скрываем окно приложения
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE

# Запуск
proc = subprocess.Popen(
    args,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stdin=subprocess.DEVNULL,
    bufsize=0,
    universal_newlines=False,
    startupinfo=startupinfo
)

# Чтение вывода в фоне
threading.Thread(target=read_output, args=(proc.stdout, "OUT"), daemon=True).start()
threading.Thread(target=read_output, args=(proc.stderr, "ERR"), daemon=True).start()

print(f"[+] aMuleD-Daemon запущен скрыто с конфигурацией: {config_dir}")
print(f"[+] PID: {proc.pid}, кодировка: {CONSOLE_ENCODING}")

try:
    proc.wait()
except KeyboardInterrupt:
    print("\n[!] Прерывание пользователем. Завершаем aMuleD...")
    proc.terminate()
    proc.wait()