#!/usr/bin/env python3
# apply_amule_config.py
# Author: Linda MacGill aka L∴L∴

import sys
import json
import os
import tarfile
from pathlib import Path

# Пути относительно скрипта
SCRIPT_DIR = Path(__file__).parent
ARCHIVE_PATH = SCRIPT_DIR / "amuled-demon.tar.gz"
TEMPLATE_PATH = SCRIPT_DIR / "amule-config-template.json"
CONFIG_DIR = SCRIPT_DIR / "amule-daemon-config"

# Хардкоженные значения по умолчанию
DEFAULT_VIDEO_PLAYER = r"H:\Program Files\VLC_105-emule\vlc101010101010101010.exe"
DEFAULT_INCOMING_DIR = r"Y:\software\AI\ComfyUI-Easy-Install\ComfyUI-Easy-Install\ComfyUI\models"
DEFAULT_TEMP_DIR = r"Y:\software\AI\ComfyUI-Easy-Install\snork_TMP"


def deploy_amule_if_needed():
    """Распаковывает amuled-demon.tar.gz, если он существует."""
    if not ARCHIVE_PATH.exists():
        print(f"[!] Архив не найден: {ARCHIVE_PATH}")
        print("[!] Убедитесь, что рядом со скриптом лежит 'amuled-demon.tar.gz'")
        sys.exit(1)

    print(f"[+] Найден архив: {ARCHIVE_PATH}")
    print(f"[+] Распаковка в: {SCRIPT_DIR}")

    try:
        with tarfile.open(ARCHIVE_PATH, "r:gz") as tar:
            tar.extractall(path=SCRIPT_DIR)
        print("[+] aMule успешно развёрнут.")
    except Exception as e:
        print(f"[!] Ошибка при распаковке: {e}", file=sys.stderr)
        sys.exit(1)


def escape_path_for_conf(path: str) -> str:
    """Преобразует путь в формат для .conf: Y:\dir → Y:\\dir"""
    return path.replace("\\", "\\\\")


def write_conf_file(data: dict, output_path: Path):
    """Записывает словарь в формате aMule .conf"""
    with open(output_path, "w", encoding="utf-8") as f:
        for section, keys in data.items():
            f.write(f"[{section}]\n")
            for key, value in keys.items():
                if isinstance(value, str):
                    f.write(f"{key}={value}\n")
                elif isinstance(value, (int, bool)):
                    f.write(f"{key}={int(value)}\n")
                else:
                    f.write(f"{key}={value}\n")
            f.write("\n")


def apply_config(video_player: str, incoming_dir: str, temp_dir: str):
    # Убедимся, что папка конфигурации существует (после распаковки она должна быть)
    if not CONFIG_DIR.exists():
        print(f"[!] Папка конфигурации отсутствует: {CONFIG_DIR}", file=sys.stderr)
        print("[!] Возможно, архив не содержал её или был повреждён.")
        sys.exit(1)

    if not TEMPLATE_PATH.exists():
        print(f"[!] Шаблон конфигурации отсутствует: {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Автоматически определяем OSDirectory как путь к amule-daemon-config с завершающим слэшем
    os_directory = escape_path_for_conf(str(CONFIG_DIR.resolve()) + os.sep)

    # Обновляем пути
    config["eMule"]["VideoPlayer"] = escape_path_for_conf(video_player)
    config["eMule"]["IncomingDir"] = escape_path_for_conf(incoming_dir)
    config["eMule"]["TempDir"] = escape_path_for_conf(temp_dir)
    config["eMule"]["OSDirectory"] = os_directory

    # Записываем оба конфига
    amule_conf = CONFIG_DIR / "amule.conf"
    remote_conf = CONFIG_DIR / "remote.conf"

    write_conf_file(config, amule_conf)
    write_conf_file(config, remote_conf)

    print(f"[+] Записаны конфиги: {amule_conf}, {remote_conf}")


def main():
    # Шаг 1: развёртывание, если есть архив
    deploy_amule_if_needed()

    # Шаг 2: получение путей
    if len(sys.argv) == 4:
        video_player = sys.argv[1]
        incoming_dir = sys.argv[2]
        temp_dir = sys.argv[3]
    elif len(sys.argv) == 1:
        video_player = DEFAULT_VIDEO_PLAYER
        incoming_dir = DEFAULT_INCOMING_DIR
        temp_dir = DEFAULT_TEMP_DIR
    else:
        print("Использование:", file=sys.stderr)
        print(f"  {sys.argv[0]}                              # использовать встроенные пути", file=sys.stderr)
        print(f"  {sys.argv[0]} VIDEO_PLAYER INCOMING_DIR TEMP_DIR", file=sys.stderr)
        sys.exit(1)

    # Шаг 3: применение конфигурации
    apply_config(video_player, incoming_dir, temp_dir)
    print("[+] Конфигурация aMule успешно применена.")


if __name__ == "__main__":
    main()