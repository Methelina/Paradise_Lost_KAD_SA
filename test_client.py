import os
import time
import requests
from bs4 import BeautifulSoup
import sys

# === Конфигурация ===
AMULE_WEB_URL = "http://127.0.0.1:4711"
PASSWORD = os.environ.get("AMULE_PASSWORD", "1488")
COOKIES_FILE = "amule_cookie.txt"

def get_fresh_session():
    """Всегда делаем новый вход и сохраняем куку."""
    session = requests.Session()
    login_data = {"pass": PASSWORD, "submit": "Submit"}
    resp = session.post(f"{AMULE_WEB_URL}/login.php", data=login_data, timeout=10)
    
    if "amuleweb_session_id" not in session.cookies:
        raise Exception("Не удалось авторизоваться в aMule")
    
    with open(COOKIES_FILE, "w") as f:
        f.write(f"amuleweb_session_id={session.cookies['amuleweb_session_id']}")
    
    return session

def get_session_from_cookie():
    """Загружаем куку из файла и возвращаем сессию."""
    if not os.path.exists(COOKIES_FILE):
        return get_fresh_session()
    
    session = requests.Session()
    with open(COOKIES_FILE, "r") as f:
        line = f.read().strip()
        if "=" in line:
            name, value = line.split("=", 1)
            session.cookies.set(name, value)
    return session

def clear_search_results(session):
    """Очищаем предыдущие результаты поиска."""
    try:
        session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={"command": "clearsearch"}, timeout=5)
    except Exception:
        pass  # Игнорируем ошибки очистки

def show_search_progress_bar(session, query, search_type="Kad", max_duration=30):
    """Показываем прогресс-бар с реальным состоянием поиска."""
    clear_search_results(session)  # ← КРИТИЧЕСКИ ВАЖНО: иначе дубли!

    try:
        session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={
            "searchval": query,
            "searchtype": search_type,
            "command": "search"
        }, timeout=10)
    except requests.RequestException as e:
        print(f"\n[ERROR] Не удалось инициировать поиск в {search_type}: {e}")
        return []

    start_time = time.time()
    end_time = start_time + max_duration
    cursor_chars = ["\\", "|", "/", "-"]
    results = []

    while True:
        current_time = time.time()
        if current_time >= end_time:
            # Время истекло
            sys.stdout.write(f"\r[{search_type}] STATUS: [{'▓' * 40}] 100.00%  \n")
            sys.stdout.flush()
            break

        try:
            resp = session.get(f"{AMULE_WEB_URL}/amuleweb-main-search.php", timeout=10)
            if resp.status_code != 200:
                raise requests.RequestException(f"HTTP {resp.status_code}")
            soup = BeautifulSoup(resp.text, "html.parser")

            # Парсим новые результаты с защитой от битых строк
            for row in soup.select("tbody tr"):
                try:
                    cols = row.find_all("td")
                    if len(cols) < 3:
                        continue
                    cb = cols[0].find("input", type="checkbox")
                    if not cb or not isinstance(cb.get("name"), str) or len(cb["name"]) != 32:
                        continue
                    file_hash = cb["name"]
                    name = cols[0].get_text().replace(file_hash, "").strip()
                    size = cols[1].get_text(strip=True)
                    sources_text = cols[2].get_text(strip=True)
                    sources = int(sources_text) if sources_text.isdigit() else 0

                    # Предотвращаем дубли по хэшу
                    if not any(r['hash'] == file_hash for r in results):
                        results.append({
                            "hash": file_hash,
                            "name": name,
                            "size": size,
                            "sources": sources,
                            "network_type": search_type
                        })
                except Exception:
                    # Игнорируем ошибки парсинга отдельной строки
                    continue

            # Обновляем прогресс-бар
            elapsed = current_time - start_time
            progress = min(int((elapsed / max_duration) * 100), 100)
            filled_width = int(40 * progress / 100)
            empty_width = 40 - filled_width
            filled_part = "▓" * filled_width
            empty_part = "░" * empty_width
            percentage = (elapsed / max_duration) * 100
            cursor_char = cursor_chars[int(elapsed * 2) % len(cursor_chars)]  # ~2 обновления/сек

            sys.stdout.write(f"\r[{search_type}] STATUS: [{filled_part}{empty_part}] {percentage:.2f}% {cursor_char}")
            sys.stdout.flush()
            time.sleep(1.0)  # ← Снижаем нагрузку: опрос раз в секунду

        except requests.RequestException as e:
            print(f"\n[WARN] Проблема при опросе {search_type}-поиска: {e}")
            time.sleep(1.0)
            continue

    return results

def search_files_sequential(session, query, wait_sec=30):
    """Поиск файлов последовательно в Kad и Global сетях с прогресс-барами."""
    print(f"[INFO] Поиск '{query}' в Kad...")
    kad_results = show_search_progress_bar(session, query, search_type="Kad", max_duration=wait_sec)
    
    print(f"[INFO] Поиск '{query}' в Global...")
    global_results = show_search_progress_bar(session, query, search_type="Global", max_duration=wait_sec)
    
    # Объединяем, избегая дублей
    all_results = []
    seen_hashes = set()

    for r in kad_results:
        all_results.append(r)
        seen_hashes.add(r['hash'])

    for r in global_results:
        if r['hash'] in seen_hashes:
            # Найден в обоих сетях
            for existing in all_results:
                if existing['hash'] == r['hash']:
                    existing['network_type'] = "Kad/Global"
                    break
        else:
            all_results.append(r)
            seen_hashes.add(r['hash'])

    return all_results

def download_file(session, file_hash, category="all"):
    try:
        session.post(f"{AMULE_WEB_URL}/amuleweb-main-search.php", data={
            file_hash: "on",
            "targetcat": category,
            "command": "download"
        }, timeout=10)
        print(f"[SUCCESS] Файл {file_hash} добавлен в загрузку (категория: {category})")
    except Exception as e:
        print(f"[ERROR] Не удалось добавить файл в загрузку: {e}")

def get_shared_files(session, timeout=30):
    """Получаем список всех файлов шаринга."""
    try:
        resp = session.get(f"{AMULE_WEB_URL}/amuleweb-main-shared.php", timeout=timeout)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        shared_files = []
        table_body = soup.find("tbody")
        if table_body:
            for row in table_body.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 6:
                    checkbox = cols[0].find("input", type="checkbox")
                    if checkbox and len(checkbox.get("name", "")) == 32:
                        file_hash = checkbox["name"]
                        name = cols[0].get_text().replace(file_hash, "").strip()
                        size = cols[1].get_text(strip=True)
                        uploaded_session = cols[2].get_text(strip=True)
                        uploaded_total = cols[3].get_text(strip=True)
                        ratio = cols[4].get_text(strip=True)
                        priority = cols[5].get_text(strip=True).replace("&nbsp(auto)", " (auto)").strip()
                        shared_files.append({
                            "hash": file_hash,
                            "name": name,
                            "size": size,
                            "uploaded_session": uploaded_session,
                            "uploaded_total": uploaded_total,
                            "ratio": ratio,
                            "priority": priority
                        })
        return shared_files
    except requests.exceptions.ReadTimeout:
        print(f"[ERROR] Таймаут при запросе списка файлов шаринга (>{timeout} секунд). Возможно, много файлов в шаринге.")
        return []
    except Exception as e:
        print(f"[ERROR] Ошибка при получении списка файлов шаринга: {str(e)}")
        return []

# === Основной поток ===
if __name__ == "__main__":
    print("[INFO] Авторизация в aMule...")
    session = get_fresh_session()

    # Проверка сессии
    try:
        resp = session.get(f"{AMULE_WEB_URL}/amuleweb-main-dload.php", timeout=10)
        if "aMule - Control Panel - Login" in resp.text:
            raise Exception("Сессия не работает — показана страница входа!")
    except Exception as e:
        print(f"[ERROR] Проверка сессии не удалась: {e}")
        exit(1)

    print("\n=== Меню ===")
    print("1. Искать файлы")
    print("2. Список файлов шаринга")
    
    try:
        choice = int(input("Выберите действие (1 или 2): "))
        
        if choice == 1:
            query = input("🔍 Поиск: ").strip()
            if not query:
                print("Пустой запрос")
                exit()
            
            results = search_files_sequential(session, query, wait_sec=30)
            
            if not results:
                print("Ничего не найдено")
                exit()

            print(f"\nНайдено {len(results)} файлов:")
            print("-" * 100)
            
            for i, r in enumerate(results, 1):
                network_label = {
                    "Kad": "[KAD]",
                    "Global": "[Global]",
                    "Kad/Global": "[KAD/Global]"
                }.get(r['network_type'], f"[{r['network_type']}]")
                
                print(f"{i:2d}. {network_label} {r['name']}")
                print(f"    Размер: {r['size']} | Источников: {r['sources']} | Хэш: {r['hash']}")
                print("-" * 100)

            try:
                choice = int(input("Выберите файл (0 — отмена): "))
                if 1 <= choice <= len(results):
                    download_file(session, results[choice - 1]["hash"])
            except (ValueError, KeyboardInterrupt):
                pass
                
        elif choice == 2:
            print("[INFO] Получение списка файлов шаринга...")
            shared_files = get_shared_files(session, timeout=30)
            
            if not shared_files:
                print("Нет файлов в шаринге или произошла ошибка при получении")
            else:
                print(f"\nВсего файлов в шаринге: {len(shared_files)}")
                print("-" * 80)
                
                for i, f in enumerate(shared_files, 1):
                    print(f"{i}. {f['name']}")
                    print(f"   Размер: {f['size']}, Загрузка: {f['uploaded_total']}, Соотношение: {f['ratio']}, Приоритет: {f['priority']}")
                    print(f"   Хэш: {f['hash']}")
                    print("-" * 80)
        else:
            print("Неверный выбор")
            
    except (ValueError, KeyboardInterrupt):
        print("Отменено пользователем")