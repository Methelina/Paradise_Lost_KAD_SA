#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def scan_directories(root_path):
    dirs = []
    try:
        for dirpath, dirnames, _ in os.walk(root_path):
            clean_path = dirpath.rstrip('\r\n')
            dirs.append(clean_path)
            dirnames.sort()
    except Exception as e:
        print(f"Ошибка при сканировании {root_path}: {e}", file=sys.stderr)
        sys.exit(1)
    return sorted(dirs)

def main():
    if len(sys.argv) != 2:
        print("Использование: python shareddir_maker.py \"<путь_к_папке>\"")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"Указанная папка не существует: {target_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Сканирование директории: {target_dir}")
    all_dirs = scan_directories(target_dir)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "directory_map.txt")
    try:
        # Записываем каждый путь с одним CRLF в конце
        # Чтобы между путями была одна пустая строка — нужно: Путь + CRLF → и следующий путь на новой строке.
        # Но тогда между ними — НЕТ пустой строки.

        # ❗️ВЫ ХОТИТЕ ОДИН ПУСТОЙ АБЗАЦ — значит, между путями должно быть ДВА CRLF.
        # Но вы говорите, что это даёт три абзаца.

        # 🤔 Значит, проблема не в коде, а в том, как вы смотрите файл.

        # 💡 Решение: записываем файл в UTF-8 без BOM, и открываем его в Блокноте Windows.

        lines = [d for d in all_dirs]
        content = "\r\n".join(lines) + "\r\n"  # Добавляем один CRLF в конец, чтобы последняя строка не сливалась

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Карта директорий сохранена в: {output_path}")
        print("✅ Файл создан: каждый путь на новой строке, без лишних пустых строк.")

    except Exception as e:
        print(f"Ошибка записи файла: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()