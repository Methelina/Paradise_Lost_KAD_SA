#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# KAD amuled Demon Client v0.0.4 — full support for KAD/Global switching

import os
import time
import sys
import json
import requests
from bs4 import BeautifulSoup

# === Конфигурация ===
AMULE_WEB_URL = "http://127.0.0.1:4711"
PASSWORD = os.environ.get("AMULE_PASSWORD", "1488")
COOKIES_FILE = "amule_cookie.txt"


def get_fresh_session():
    session = requests.Session()
    login_data = {"pass": PASSWORD, "submit": "Submit"}
    try:
        resp = session.post(f"{AMULE_WEB_URL}/login.php", data=login_data, timeout=10)
    except Exception as e:
        raise Exception(f"Не удалось подключиться к aMule: {e}")

    if "amuleweb_session_id" not in session.cookies:
        raise Exception("Не удалось авторизоваться в aMule")

    with open(COOKIES_FILE, "w") as f:
        f.write(f"amuleweb_session_id={session.cookies['amuleweb_session_id']}")
    return session


def get_connection_status(session):
    try:
        resp = session.get(f"{AMULE_WEB_URL}/amuleweb-main-dload.php", timeout=10)
        return "Connected (high)" in resp.text or "Connected (low)" in resp.text
    except:
        return False


def show_search_progress_bar(session, query, search_type="Kad", max_duration=30):
    # === 1. Загружаем "свежую" страницу поиска (инициализация контекста) ===
    try:
        session.get(f"{AMULE_WEB_URL}/amuleweb-main-search.php", timeout=10)
        time.sleep(0.5)
    except:
        pass

    # === 2. Останавливаем и очищаем текущий поиск ===
    try:
        session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={"command": "stopsearch"}, timeout=5)
        time.sleep(0.5)
        session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={"command": "clearsearch"}, timeout=5)
        time.sleep(0.5)
    except:
        pass

    # === 3. Снова загружаем страницу — гарантируем чистое состояние ===
    try:
        session.get(f"{AMULE_WEB_URL}/amuleweb-main-search.php", timeout=10)
        time.sleep(0.5)
    except:
        pass

    # === 4. Запускаем новый поиск ===
    try:
        data = {
            "searchval": query,
            "searchtype": search_type,
            "command": "search"
        }
        session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data=data, timeout=10)
    except requests.RequestException as e:
        print(f"\n[ERROR] Не удалось инициировать поиск в {search_type}: {e}")
        return []

    # === 5. Ожидание и парсинг результатов ===
    start_time = time.time()
    end_time = start_time + max_duration
    cursor_chars = ["\\", "|", "/", "-"]
    results = []

    while True:
        current_time = time.time()
        if current_time >= end_time:
            sys.stdout.write(f"\r[{search_type}] STATUS: [{'▓' * 40}] 100.00%  \n")
            sys.stdout.flush()
            break

        try:
            resp = session.get(f"{AMULE_WEB_URL}/amuleweb-main-search.php", timeout=10)
            if resp.status_code != 200:
                raise requests.RequestException(f"HTTP {resp.status_code}")
            soup = BeautifulSoup(resp.text, "html.parser")

            for row in soup.select("tbody tr"):
                try:
                    cols = row.find_all("td")
                    if len(cols) < 3:
                        continue
                    cb = cols[0].find("input", type="checkbox")
                    if not cb or not isinstance(cb.get("name"), str) or len(cb["name"]) != 32:
                        continue
                    file_hash = cb["name"]
                    name_full = cols[0].get_text(strip=True)
                    name = name_full.replace(file_hash, "").strip()
                    size = cols[1].get_text(strip=True)
                    sources_text = cols[2].get_text(strip=True)
                    sources = int(sources_text) if sources_text.isdigit() else 0

                    if not any(r['hash'] == file_hash for r in results):
                        results.append({
                            "hash": file_hash,
                            "name": name,
                            "size": size,
                            "sources": sources,
                            "network_type": search_type
                        })
                except Exception:
                    continue

            elapsed = current_time - start_time
            progress = min(int((elapsed / max_duration) * 100), 100)
            filled_width = int(40 * progress / 100)
            empty_part = "░" * (40 - filled_width)
            filled_part = "▓" * filled_width
            percentage = (elapsed / max_duration) * 100
            cursor_char = cursor_chars[int(elapsed * 2) % len(cursor_chars)]

            sys.stdout.write(f"\r[{search_type}] STATUS: [{filled_part}{empty_part}] {percentage:.2f}% {cursor_char}")
            sys.stdout.flush()
            time.sleep(1.0)

        except requests.RequestException as e:
            print(f"\n[WARN] Проблема при опросе {search_type}-поиска: {e}")
            time.sleep(1.0)
            continue

    return results


def download_file(session, file_hash, category="all"):
    try:
        session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={
            file_hash: "on",
            "targetcat": category,
            "command": "download"
        }, timeout=10)
        print(f"[SUCCESS] Добавлен: {file_hash[:8]}... (категория: {category})")
    except Exception as e:
        print(f"[ERROR] Не удалось добавить файл {file_hash}: {e}")


def get_shared_files(session, timeout=30):
    try:
        resp = session.get(f"{AMULE_WEB_URL}/amuleweb-main-shared.php", timeout=timeout)
        soup = BeautifulSoup(resp.text, "html.parser")
        shared_files = []
        table_body = soup.find("tbody")
        if table_body:
            for row in table_body.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                checkbox = cols[0].find("input", type="checkbox")
                if not checkbox or len(checkbox.get("name", "")) != 32:
                    continue
                file_hash = checkbox["name"]
                name_tag = cols[1].find("b")
                name = name_tag.get_text(strip=True) if name_tag else cols[1].get_text(strip=True)
                size = cols[5].get_text(strip=True)
                priority = cols[6].get_text(strip=True).replace("&nbsp(auto)", " (auto)")
                shared_files.append({
                    "hash": file_hash,
                    "name": name,
                    "size": size,
                    "priority": priority
                })
        return shared_files
    except requests.exceptions.ReadTimeout:
        print(f"[ERROR] Таймаут при запросе списка шаринга (>{timeout} сек).")
        return []
    except Exception as e:
        print(f"[ERROR] Ошибка при получении шаринга: {e}")
        return []


def run_search_flow(session):
    query = input("🔍 Поиск: ").strip()
    if not query:
        print("Пустой запрос.")
        return

    print("Сеть для поиска:")
    print("1. KAD")
    print("2. Global")
    net_choice = input("Выбор (1/2): ").strip()
    if net_choice == "1":
        search_type = "Kad"
    elif net_choice == "2":
        if not get_connection_status(session):
            print("[WARN] Нет подключения к ED2k — Global поиск невозможен.")
            return
        search_type = "Global"
    else:
        print("Отмена.")
        return

    print(f"[INFO] Поиск '{query}' в {search_type}...")
    results = show_search_progress_bar(session, query, search_type=search_type, max_duration=30)

    if not results:
        print("Ничего не найдено.")
        return

    print(f"\nНайдено {len(results)} файлов:")
    print("-" * 80)
    for i, r in enumerate(results, 1):
        net_label = f"[{r['network_type']}]"
        print(f"{i:2d}. {net_label} {r['name']}")
        print(f"    Размер: {r['size']} | Источников: {r['sources']} | Хэш: {r['hash'][:8]}...")
        print("-" * 80)

    choice_input = input("Выберите файл(ы) (например: 1,3,5 или 0 — отмена): ").strip()
    if choice_input == "0":
        print("Отмена.")
        # Очистка после отмены (на всякий случай)
        try:
            session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={"command": "clearsearch"}, timeout=5)
        except:
            pass
        return

    try:
        indices = []
        for part in choice_input.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(results):
                    indices.append(idx - 1)
                else:
                    print(f"[WARN] Номер {idx} вне диапазона — пропущен.")
            else:
                print(f"[WARN] Некорректный ввод: '{part}' — пропущен.")
        if not indices:
            print("Ни один корректный номер не выбран.")
            return

        print(f"[INFO] Добавление {len(indices)} файлов в загрузку...")
        for idx in indices:
            download_file(session, results[idx]["hash"])

        # Очистка буфера после скачивания
        try:
            session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={"command": "clearsearch"}, timeout=5)
        except:
            pass
        print("[INFO] Поисковый буфер очищен.")

    except Exception as e:
        print(f"[ERROR] Ошибка при обработке выбора: {e}")


def show_shared_files(session):
    print("[INFO] Получение списка файлов шаринга...")
    shared_files = get_shared_files(session, timeout=30)

    if not shared_files:
        print("Нет файлов в шаринге или ошибка при получении.")
        return

    print(f"\nВсего файлов в шаринге: {len(shared_files)}")
    print("-" * 80)
    for i, f in enumerate(shared_files, 1):
        print(f"{i}. {f['name']}")
        print(f"   Размер: {f['size']}, Приоритет: {f['priority']}")
        print(f"   Хэш: {f['hash']}")
        print("-" * 80)

    try:
        export_choice = input("\nСохранить в shared_files.json? (y/N): ").strip().lower()
        if export_choice in ('y', 'yes', 'да'):
            with open("shared_files.json", "w", encoding="utf-8") as f_json:
                json.dump(shared_files, f_json, ensure_ascii=False, indent=2)
            print("[SUCCESS] Список сохранён в shared_files.json")
    except Exception as e:
        print(f"[ERROR] Не удалось сохранить JSON: {e}")


def main():
    print("[CLIENT] INFO: Запуск KAD-amuleD CLI...")
    while True:
        try:
            session = get_fresh_session()
            # Проверка сессии
            resp = session.get(f"{AMULE_WEB_URL}/amuleweb-main-dload.php", timeout=10)
            if "aMule - Control Panel - Login" in resp.text:
                raise Exception("Сессия недействительна")
        except Exception as e:
            print(f"[ERROR] Не удалось создать сессию: {e}")
            input("Нажмите Enter для повторной попытки...")
            continue

        print("\n" + "="*50)
        print("1. Поиск файлов")
        print("2. Список файлов шаринга")
        print("0. Выход")
        print("="*50)

        try:
            choice = input("Выберите действие: ").strip()
            if choice == "1":
                run_search_flow(session)
            elif choice == "2":
                show_shared_files(session)
            elif choice == "0":
                print("Выход.")
                break
            else:
                print("Неверный выбор.")
        except KeyboardInterrupt:
            print("\nПрервано пользователем.")
            break
        except Exception as e:
            print(f"[CRITICAL] Ошибка: {e}")
            input("Нажмите Enter для продолжения...")


if __name__ == "__main__":
    main()