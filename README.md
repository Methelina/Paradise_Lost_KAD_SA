# 🌌 Paradise Lost KAD SA — aMule Daemon Automation Suite

> **Полностью автоматизированный, портативный лаунчер и контроллер для aMule (eDonkey2000 / Kademlia) с управлением через Web API и демонизацией.**

---

## 📦 Что это?

`Paradise Lost` — это набор Python-скриптов и вспомогательных бинарных артефактов, который позволяет:

- Развернуть **aMule daemon** (`amuled`) с полным KAD-поддержанием и веб-интерфейсом (`amuleweb`) без установки в систему.
- Динамически генерировать конфигурации (`amule.conf`, `remote.conf`) под любое окружение.
- Управлять демоном: запуск, остановка, перезагрузка, мониторинг статуса.
- Взаимодействовать с aMule через **HTTP JSON‑RPC / Web Interface**, используя встроенный клиент (`test_client.py` / `amule_client.py`).
- Интегрироваться с внешними приложениями (например, добавление ссылок ed2k, поиск, загрузка файлов).

Проект **не требует** компиляции aMule — поставляется предварительно собранный `amuled` (Linux, совместимый с большинством дистрибутивов), упакованный в `amuled-demon.tar.gz`. Всё управление — через Python 3.8+.

---

## 🧱 Архитектура

| Компонент               | Назначение                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `amuled`               | Ядро сети eDonkey2000/Kademlia. Запускается как демон (фоновый процесс).     |
| `amuleweb`             | Встроенный веб-сервер, предоставляющий HTTP API (JSON-RPC) для управления. |
| `amuled_daemon.py`     | Главный управляющий скрипт: запуск/остановка демона, логирование, PID-файл. |
| `apply_amule_config.py`| Генератор конфигураций: подставляет пути, порты, права доступа и пр.        |
| `amule_client.py`      | Python-клиент для общения с amuleweb через JSON-RPC (по HTTP).             |
| `test_client.py`       | Тестовый пример: подключение, поиск файлов, статистика, добавление ссылок. |

**Поток данных**:
- Пользователь запускает `amuled_daemon.py start`.
- Скрипт распаковывает (при первом запуске) `amuled-demon.tar.gz` в `.cache/amule/`.
- Генерирует `amule.conf`, `remote.conf` и др. в папке конфигурации.
- Запускает `amuled` как дочерний процесс с перенаправлением stdout/stderr в log-файл.
- `amuleweb` стартует автоматически (включено в конфиге) и слушает порт (по умолчанию 4711).
- Скрипт `amule_client.py` подключается к `http://127.0.0.1:4711` и выполняет команды через HTTP POST.

---

## ⚙️ Технические детали реализации

### 1. Демонизация и управление процессом (`amuled_daemon.py`)

- Использует стандартный подход: `subprocess.Popen` с `start_new_session=True` для отделения от терминала.
- PID записывается в `amule.pid` для последующей остановки (`os.kill(-pid, signal.SIGTERM)` для всей группы процессов).
- Логи → `amuled.log` и `amuleweb.log` с ротацией по размеру (через `logging.handlers.RotatingFileHandler`).
- Поддерживаются команды: `start`, `stop`, `restart`, `status`, `logs`.
- При остановке сначала посылается `SIGTERM`, затем таймаут → `SIGKILL`.

### 2. Генерация конфигурации (`apply_amule_config.py`)

Конфиги пишутся с нуля, без зависимостей от системных файлов. Ключевые параметры:

- **amule.conf**:
  - `[Core]` → `TempDir`, `IncomingDir`, `Port`, `UDPPort`, `KademliaPort`, `MaxConnections`.
  - `[Webserver]` → `UseWebserver=1`, `Port=4711`, `Password=` (хеш MD5 пароля), `AllowGuest=0`.
  - `[ExternalConnect]` → `ECEnabled=1`, `Port=4712` (если нужен отдельный RPC).
  - `[Kademlia]` → `KademliaEnable=1`, `Bootstrap nodes` встроены (по умолчанию).
  - Автоматическая подстановка абсолютных путей к `TempDir`, `IncomingDir`, `ConfigDir` через `pathlib`.
- **remote.conf** → используется для `amuleweb`:
  - `[web]` → `Host=127.0.0.1`, `Port=4711`, `Password=` (MD5), `Template=default`.

Пароль в конфиге хранится в виде MD5-хеша (`hashlib.md5(password.encode()).hexdigest()`), что соответствует ожиданиям amuleweb.

### 3. Взаимодействие с amuleweb через JSON-RPC (`amule_client.py`)

- **Протокол**:
  - POST запросы на `http://<host>:<port>/ulrpc`.
  - Тело: JSON-RPC 2.0 объект, например: `{"jsonrpc": "2.0", "method": "get_stats", "params": [], "id": 1}`.
  - Авторизация: Basic Auth с логином `amule` (по умолчанию) и паролем (MD5 не нужен, сам amuleweb принимает plaintext и сверяет с хешем в `remote.conf`).
- **Поддерживаемые методы** (согласно документации aMule Web UI):
  - `get_stats` — статистика (скорости, соединения, очередь).
  - `get_files` — список текущих загрузок.
  - `get_sources` — источники для файлов.
  - `add_links` — добавить ed2k-ссылки (или magnet).
  - `search` — поиск по сети KAD (по имени, типу, размеру).
  - `kill` — мягкое завершение amuled.
- Клиент написан на чистом `requests` с `urllib3.disable_warnings()` (если самоподписанный сертификат).
- Пример в `test_client.py` демонстрирует авторизацию, выполнение команд и обработку ошибок.

### 4. Пакетная поставка aMule

Проект включает предварительно скомпилированный **статически связанный** `amuled` (ELF, x86_64) с минимальными зависимостями (libcrypto, libssl, libz). Архив `amuled-demon.tar.gz` содержит:

```
amuled-demon/
├── bin/amuled
├── bin/amuleweb
├── share/amule/ (языковые файлы, темы)
└── lib/ (несколько .so, если нужны — но в основном статическая линковка)
```

При первом запуске `amuled_daemon.py` распаковывает архив в `.local/opt/paradise_lost/amule/` и добавляет бинарные файлы в `PATH` временно.

Проверка: скрипт делает `ldd amuled` (на Linux) и выводит предупреждение, если какие-то shared libs отсутствуют (но обычно всё ок).

---

## 🚀 Быстрый старт (технический)

### Требования
- Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch) или WSL2.
- Python 3.8+ с `pip install requests beautifulsoup4 pathlib`
- Свободный порт 4711 (для веб-интерфейса) и порты TCP/UDP (по умолчанию 4662/4672/4692 — можно менять).

### Установка (автоматическая)

```bash
git clone https://github.com/Methelina/Paradise_Lost_KAD_SA.git
cd Paradise_Lost_KAD_SA
chmod +x *.py

# Первый запуск — всё распакуется само
python amuled_daemon.py start
```

Логи будут в `.logs/amuled.log` и `.logs/amuleweb.log`. Проверьте статус:
```bash
python amuled_daemon.py status
```

### Проверка соединения с API (JSON-RPC)

```bash
python test_client.py --host 127.0.0.1 --port 4711 --password your_password
```

Если не задан пароль в конфиге, по умолчанию `password=amule` (т.е. он используется при генерации, его можно переопределить в `apply_amule_config.py`).

### Остановка демона
```bash
python amuled_daemon.py stop
```

---

## 🔧 Расширенная конфигурация

Все настройки находятся в корневой папке после первого запуска:
- `.config/amule/amule.conf`
- `.config/amule/remote.conf`
- `.config/amule/amule.key` (если EC включён)

Изменить порты, папки загрузки, ограничения можно прямо в `amule.conf` → затем перезапустить демон (`restart`).

**Пример увеличения лимитов соединений:**
```ini
[Core]
MaxConnections=500
MaxSourcesPerFile=300
UploadLimit=50
```

**Включение внешнего доступа к amuleweb (из другой подсети):**
В `remote.conf` поменять `Host=0.0.0.0` и настроить файрвол.  
**⚠️ Опасно:** лучше использовать SSH-туннель или VPN.

---

## 🧪 Пример использования Python-клиента

```python
from amule_client import AMuleClient

client = AMuleClient(host='127.0.0.1', port=4711, password='your_password')
if client.login():
    stats = client.get_stats()
    print(f"Скорость скачивания: {stats['download_speed']} B/s")
    client.add_link('ed2k://|file|...|')
    results = client.search('ubuntu iso', filetype='archive')
    for res in results:
        print(f"{res['name']}, {res['size']} bytes")
else:
    print("Ошибка авторизации")
```

---

## 📂 Структура репозитория (техническая)

```
.
├── amuled_daemon.py           # Основной скрипт управления демоном
├── apply_amule_config.py      # Генератор конфигов (вызывается автоматически)
├── amule_client.py            # Клиент для JSON-RPC API
├── test_client.py             # Пример использования клиента
├── amuled-demon.tar.gz        # Предкомпилированный aMule (x86_64 Linux)
├── .cache/                    # Создаётся при первом запуске (распаковка)
├── .config/amule/             # Конфиги, PID-файл, логи
└── README.md                  # Этот файл
```

---

## 🐛 Отладка

- **amuled не стартует** → посмотри `logs/amuled.log`. Частая ошибка: порт занят или нет прав на запись в `IncomingDir`.
- **amuleweb не отвечает** → проверь `remote.conf`: `Host=127.0.0.1`, `Port=4711`, парольные хеши совпадают. Также можно напрямую в браузере открыть `http://127.0.0.1:4711` — там будет веб-интерфейс.
- **Не добавляются ссылки** → возможно amuled не запущен в полноценном режиме (попробуй `amuled_daemon.py restart`). Также проверь, есть ли у ed2k-ссылок правильный хеш.
- **KAD не работает** → убедись, что `KademliaEnable=1` и исходящие UDP-пакеты не блокируются файрволом. Можно вручную добавить bootstrap узлы (список есть в amule.org).

---

## 📜 Лицензия

Проект распространяется под **MIT License**. aMule — GPLv2, но мы не пересобираем его, а распространяем бинарные файлы, которые легально доступны для некоммерческого использования.

---

## 🤝 Благодарности

- Команде aMule за мощный и стабильный бэкенд.
- Kademlia-сети за живучесть спустя два десятилетия.
- Всем, кто ещё помнит, что такое eDonkey2000 😉

---
