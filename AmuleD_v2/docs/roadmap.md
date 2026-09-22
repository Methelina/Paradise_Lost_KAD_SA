# AmuleD_v2 Roadmap

Весь диагностический вывод переведён на обязательную tagged logging схему: стабильные модульные теги `APP`, `CLI`, `CONFIG`, `STATE`, `IMPORT`, `SERVER`, `KAD`, `ED2K`, `SEARCH`, `DOWNLOAD`, `UPLOAD`, `PEER`, `SHARE`, `HASH`, `CODEC`, `SECURITY`, `IPFILTER`, `NAT`, `DAEMON`, `INSTALL`, `RUNNER` и `TEST`. Python пишет tagged JSONL в `AmuleD_v2\logs\amuled.jsonl`; PowerShell использует `[INSTALL] [LEVEL]` и `[RUNNER] [LEVEL]`. Это позволит будущему GUI раскладывать логи по отдельным окнам, а скриптам — разбирать поток по модулю. Дата фиксации: 2026-09-22. Текущий статус: M0–M2 завершены. В M3 готовы MD4/ED2K hashing, binary codec, tags, packet framing и zlib; SHA1/AICH остаётся незавершённым. В M4 выполнены bundled import и DuckDB persistence `server.met`/`staticservers.dat`; TCP login ещё не реализован. В M7 выполнены bundled shared metadata, ED2K hashing pipeline и DuckDB persistence; AICH и KAD publish остаются. Проект самодостаточен после клонирования: базовые v1 ресурсы входят в `AmuleD_v2\assets\v1`, runtime и installer не требуют донорной папки. Runtime развёрнут через `AmuleD_v2\AmuleD_install.ps1`: Python 3.12.12 в `AmuleD_v2\.venv`, локальный uv в `AmuleD_v2\bin\uv.exe`, зависимости и кэши изолированы внутри проекта. Полный тестовый набор — 100 passed. Локальная база содержит 20 серверов, 1 статический сервер, 494 shared files и 246 shared directories. Этот документ является исходной продуктово-технической спецификацией для полностью чистого Python-клиента ED2K/Kademlia в папке [AmuleD_v2](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2). Скрипты [AmuleD_install.ps1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/AmuleD_install.ps1), [AmuleD_Run.ps1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/AmuleD_Run.ps1) и [requirements.txt](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/requirements.txt) сохраняют авторскую структуру приветствия/меню и реализуют полностью портативный Trellis2-style uv runtime.

## 1. Фактическое состояние проекта

Корень проекта: [O:\Work\Coding\Paradise_Lost_KAD_SA](file:///O:/Work/Coding/Paradise_Lost_KAD_SA). Сейчас существующий Python-код в корне является обёрткой вокруг бинарников aMule, а не реализацией ED2K/Kademlia. Ключевые файлы обёртки: [amuled_daemon.py](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amuled_daemon.py), [apply_amule_config.py](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/apply_amule_config.py), [test_client.py](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/test_client.py), [amule-config-template.json](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amule-config-template.json), [KAD_Amuled_Demon_Launcher.ps1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/KAD_Amuled_Demon_Launcher.ps1) и [Client_RUN.ps1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/Client_RUN.ps1).

Текущая обёртка запускает [amuled.exe](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amuled.exe), работает через HTTP `amuleweb` на порту 4711 и не реализует binary EC protocol на порту 4712. Цель AmuleD_v2 — полностью убрать зависимость от [amuled.exe](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amuled.exe), [amule.exe](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amule.exe), [amuleweb.exe](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amuleweb.exe), [amulecmd.exe](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amulecmd.exe), [amulegui.exe](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amulegui.exe) и любых `.dll` из старой связки.

Исходная кодовая база aMule 2.3.3 доступна через [docs\src](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/docs/src), который резолвится в [O:\Work\Coding\aMule-2.3.3](file:///O:/Work/Coding/aMule-2.3.3). Основные исходники для протокольной матрицы: [src\include\protocol](file:///O:/Work/Coding/aMule-2.3.3/src/include/protocol), [src\Packet.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/Packet.cpp), [src\Tag.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/Tag.cpp), [src\kademlia](file:///O:/Work/Coding/aMule-2.3.3/src/kademlia), [src\PartFile.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/PartFile.cpp), [src\DownloadQueue.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/DownloadQueue.cpp), [src\UploadQueue.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/UploadQueue.cpp), [src\EncryptedStreamSocket.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/EncryptedStreamSocket.cpp), [src\EncryptedDatagramSocket.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/EncryptedDatagramSocket.cpp) и [src\libs\ec\cpp](file:///O:/Work/Coding/aMule-2.3.3/src/libs/ec/cpp).

Уже подготовленные recon-документы: [current-wrapper.recon.md](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/recon/current-wrapper.recon.md), [emule-source-modules.recon.md](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/recon/emule-source-modules.recon.md) и [persistence-config.recon.md](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/recon/persistence-config.recon.md). Документ [EC_Protocol.txt](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/docs/EC_Protocol.txt) сохранять как справочный материал, но совместимость с EC в новом клиенте не требуется.

## 2. Зафиксированные продуктовые решения

AmuleD_v2 должен стать полноценным кросс-платформенным Python-клиентом ED2K/Kademlia, а не узкой утилитой. Долгосрочная цель — функциональная паритетность с aMule/eMule по следующим направлениям: ED2K, Kademlia, поиск, закачки, шаринг, upload, очереди, source exchange, IP-filter, NAT/firewall behavior, категории, ограничения, статистика и security layer. Obfuscation и secure identification включаются по факту необходимости живой сети, но архитектурно закладываются с самого начала.

Основной рабочий ориентир совместимости — eMule 0.50, поскольку он подтверждённо стабильно работает. Исходники aMule 2.3.3 используются для реверс-инженеринга протоколов, структур, констант и поведения, но не для прямого копирования кода.

CLI по умолчанию английский. Поддерживаются one-shot команды, интерактивная консоль, daemon mode и JSON output. Встроенный HTTP/web interface откладывается. Совместимость с aMule External Connect protocol не требуется; управление осуществляется собственным CLI и собственным control layer.

Категории — простые. Лимиты, очереди, IP-filter и пользовательские ограничения повторяют поведение оригинала. Поддержка proxy в первой версии не реализуется, но в коде должна быть явная заглушка и точка расширения.

Обязательные типы ссылок: ED2K file links, ED2K server links, magnet links и TXT-файлы со списками ссылок.

## 3. Платформа, runtime и зависимости

Целевая минимальная версия Python — 3.12. Целевые ОС — Windows, Linux и macOS. Разрешены кросс-платформенные зависимости, если они необходимы для реализации.

Portable runtime создаётся через uv и `.venv` внутри [AmuleD_v2](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2). Установщик должен быть идемпотентным, создавать окружение только при необходимости, не перезаписывать пользовательский конфиг и не выходить за пределы [AmuleD_v2](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2), кроме явно указанных внешних Incoming/Temp/Shared путей.

Предварительный набор зависимостей: `duckdb` для runtime state и индексов, `aiohttp` для HTTP/bootstrap и будущего web/API, `cryptography` или `pycryptodome` для security layer, `prompt_toolkit` для REPL, `rich` для таблиц и CLI output, JSONC/JSON5 parser для конфигов, а также отдельная кросс-платформенная библиотека для UPnP/NAT-PMP на соответствующем этапе.

Конфиги хранятся в JSONC. Runtime-данные, очереди, индексы и статистика хранятся в DuckDB. Файловые части закачек хранятся в temp-файлах, а метаданные — в DuckDB и/или JSON sidecar, если это удобнее для atomic recovery.

## 4. Хранение данных и режим портативности

Базовая структура AmuleD_v2 должна быть такой: [AmuleD_v2\src](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/src), [AmuleD_v2\config](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/config), [AmuleD_v2\db](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/db), [AmuleD_v2\logs](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/logs), [AmuleD_v2\tmp](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/tmp), [AmuleD_v2\incoming](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/incoming), [AmuleD_v2\temp](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/temp) и [AmuleD_v2\shared](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/shared). Папки [bin](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/bin), [db](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/db), [logs](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/logs) и [tmp](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/tmp) уже существуют, но требуют осмысленного наполнения.

По умолчанию всё состояние должно быть portable. Внешние Incoming/Temp/Shared пути задаются явно в конфиге. Старые пути из [amule-config-template.json](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/amule-config-template.json) не считаются автоматически правильными для новой версии.

Порты по умолчанию сохраняются из v1: client TCP/UDP 8089. Порты 4711 и 4712 резервируются как legacy web/API и legacy EC соответственно, но EC protocol не реализуется, а web/API появится только позже, если будет принято такое решение.

## 5. Использование ресурсов AmuleD v1

Проект самодостаточен для запуска после клонирования с GitHub. Безопасные стартовые ресурсы v1 уже входят в [assets\v1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1): [GeoIP.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/GeoIP.dat), [nodes.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/nodes.dat), [server.met](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/server.met), [staticservers.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/staticservers.dat), [ipfilter.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/ipfilter.dat), [ipfilter_static.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/ipfilter_static.dat), [shareddir.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/shareddir.dat) и [shared_files.json](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/shared_files.json). Runtime и installer ссылаются только на эти проектные пути.

Файлы `known.met`, `known2_64.met`, `clients.met`, `preferences*.dat` и `cryptkey.dat` не входят в базовый дистрибутив: они содержат пользовательскую историю, кредиты или identity material. Такие данные могут импортироваться только явно через compatibility/import layer; для первого запуска они не требуются.

## 6. Лицензионная стратегия

Желаемая лицензия — Apache License. Прямой перенос кода из aMule/eMule под Apache невозможен, потому что исходники aMule/eMule распространяются под GPL. Поэтому roadmap фиксирует clean-room / protocol-reimplementation подход.

Clean-room правило: исходники изучаются и используются для выявления протокольных фактов, форматов и наблюдаемого поведения, затем пишется независимая спецификация, после чего Python-код реализуется по спецификации без копирования GPL-кода. Если в будущем будет принято решение напрямую портировать C++ фрагменты, лицензия проекта должна быть пересмотрена в GPL-совместимую сторону.

## 7. Целевая архитектура

Корневой Python package располагается в [AmuleD_v2\src\amuled_v2](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/src/amuled_v2). Основные подмодули: `cli`, `daemon`, `config`, `logging_setup`, `state`, `core`, `core.hashes`, `core.codec`, `core.ed2k`, `core.kad`, `core.transfer`, `core.search`, `core.sharing`, `core.security`, `core.ipfilter`, `core.nat` и `tests`.

Весь сетевой core строится на `asyncio`: ED2K TCP, ED2K UDP, Kademlia UDP, периодические таймеры, source reask, search, upload/download scheduling и shutdown должны работать в одной управляемой event-loop модели. CLI и daemon используют один и тот же internal service layer, чтобы не было двух разных реализаций логики.

## 8. Roadmap этапов

### M0 — спецификация и clean-room протокольная матрица — DONE

Созданы [AmuleD_v2_SPEC.md](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/docs/AmuleD_v2_SPEC.md), [PROTOCOL_MATRIX.md](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/docs/PROTOCOL_MATRIX.md) и [LICENSE_POLICY.md](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/docs/LICENSE_POLICY.md). Составлена матрица ED2K/Kademlia opcodes, пакетов, состояний и behavioral parity по файлам из [src\include\protocol](file:///O:/Work/Coding/aMule-2.3.3/src/include/protocol), [src\kademlia](file:///O:/Work/Coding/aMule-2.3.3/src/kademlia) и core networking files. Зафиксировано, что реализация не копирует GPL-код.

Критерий выхода: документированы протокольные families, MVP scope, full parity scope, clean-room ограничения и план тестовых векторов.

### M1 — перестройка portable skeleton — DONE

Заменены [AmuleD_install.ps1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/AmuleD_install.ps1), [AmuleD_Run.ps1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/AmuleD_Run.ps1) и [requirements.txt](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/requirements.txt) с сохранением авторского ASCII welcome/menu. Добавлены `pyproject.toml`, portable uv installer, JSONC-конфиг [config\amuled.jsonc](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/config/amuled.jsonc) и пакет [src\amuled_v2](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/src/amuled_v2).

Критерий выхода: повторный запуск installer не ломает конфиг, runner запускает `python -m amuled_v2 --help`, все runtime-каталоги создаются внутри [AmuleD_v2](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2).

### M2 — config, logging, DuckDB, CLI router — DONE

Реализовать загрузку JSONC, schema validation, portable defaults, external path resolution, structured logging, DuckDB schema, миграции БД, CLI router, JSON output и базовый daemon lifecycle.

Критерий выхода: команды `status`, `config show`, `config set`, `daemon start`, `daemon stop` и `--json` работают без сети.

### M3 — hash и binary codec layer — IN PROGRESS

Реализовать MD4, ED2K file hash, SHA1/AICH interfaces, little-endian binary IO, packet framing, tag system и zlib packed packets. Источники поведения: [md4.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/utils/aLinkCreator/src/md4.cpp), [ed2khash.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/utils/aLinkCreator/src/ed2khash.cpp), [Packet.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/Packet.cpp), [MemFile.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/MemFile.cpp), [SafeFile.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/SafeFile.cpp) и [Tag.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/Tag.cpp).

Критерий выхода: unit tests покрывают hash vectors, packet encode/decode, tag encode/decode и packed payload roundtrip.

### M4 — ED2K server engine — IN PROGRESS

Импорт реальных v1 ресурсов `server.met` и `staticservers.dat` уже реализован и проверен: 20 серверов и 1 статический сервер. Далее реализуются TCP login, low/high ID handling, server status, search, source request, reconnect и server statistics. Основные источники: [Client2Server\TCP.h](file:///O:/Work/Coding/aMule-2.3.3/src/include/protocol/ed2k/Client2Server/TCP.h), [Client2Server\UDP.h](file:///O:/Work/Coding/aMule-2.3.3/src/include/protocol/ed2k/Client2Server/UDP.h), [ServerList.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/ServerList.cpp) и [SearchList.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/SearchList.cpp).

Критерий выхода: ED2K server login/search работает в loopback simulator, затем проверяется на живом сервере после явного разрешения.

### M5 — Kademlia discovery и routing

Реализовать UInt128, XOR distance, routing buckets, bootstrap из nodes URL или bundled [nodes.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/nodes.dat), UDP packet codec, hello/ping/pong, базовый routing maintenance и firewall checks. Основные источники: [UInt128.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/kademlia/utils/UInt128.cpp), [RoutingZone.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/kademlia/routing/RoutingZone.cpp), [KademliaUDPListener.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/kademlia/net/KademliaUDPListener.cpp) и [UDPFirewallTester.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/kademlia/kademlia/UDPFirewallTester.cpp).

Критерий выхода: клиент bootstrap-ится, наполняет routing table и устойчиво отвечает на базовые Kad checks.

### M6 — unified search и links

Объединить KAD search и ED2K server search в единый search engine. Поддержать ED2K file links, ED2K server links, magnet links и TXT import. Реализовать deduplication по ED2K hash, result cache, JSON output и добавление результатов в очередь закачки.

Критерий выхода: одинаковый результатный формат используется для KAD, ED2K, CLI и JSON.

### M7 — sharing и hashing pipeline — IN PROGRESS

Импорт реальных v1 `shared_files.json` и `shareddir.dat` реализован и проверен: 494 файлов и 246 каталогов. ED2K hashing pipeline и link generation реализованы на synthetic-тестах. Далее реализуются AICH pipeline, known-file index в DuckDB, priorities persistence, category assignment и KAD publish readiness. Основные источники: [SharedFileList.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/SharedFileList.cpp), [KnownFile.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/KnownFile.cpp), [KnownFileList.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/KnownFileList.cpp) и [ED2KLink.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/ED2KLink.cpp).

Критерий выхода: shared files отображаются в CLI, для них генерируются ED2K-ссылки, неизменённые файлы не перехэшируются повторно.

### M8 — download engine

Реализовать native `.part` storage, chunk bitmap, gaps, block scheduling, verified chunks, resume, pause/cancel, priorities, simple categories, disk space checks и final assembly into Incoming. Основные источники: [PartFile.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/PartFile.cpp), [GapList.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/GapList.cpp), [DownloadQueue.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/DownloadQueue.cpp), [updownclient.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/updownclient.cpp) и [ClientTCPSocket.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/ClientTCPSocket.cpp).

Критерий выхода: файл добавляется по ссылке, качается блоками 180 KB, собирается по chunk 9 728 000 байт, корректно resume-ится после перезапуска.

### M9 — peer transfer и queues

Реализовать client hello, file request, hashset request, queue rank, request parts, sending parts, compressed parts, UDP reask, dead source handling, upload slots и download slots. Основные источники: [BaseClient.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/BaseClient.cpp), [updownclient.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/updownclient.cpp), [UploadQueue.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/UploadQueue.cpp), [ClientUDPSocket.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/ClientUDPSocket.cpp) и [OtherStructs.h](file:///O:/Work/Coding/aMule-2.3.3/src/OtherStructs.h).

Критерий выхода: один файл может качаться из нескольких источников, а shared file может отдаваться другому peer.

### M10 — source exchange и original-like limits

Реализовать server sources, KAD sources, source scoring, source exchange, max connections, max sources per file, slot allocation и bandwidth throttler. Основные источники: [DownloadQueue.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/DownloadQueue.cpp), [UploadQueue.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/UploadQueue.cpp), [UploadBandwidthThrottler.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/UploadBandwidthThrottler.cpp) и [DeadSourceList.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/DeadSourceList.cpp).

Критерий выхода: поведение очередей и лимитов соответствует зафиксированной parity-матрице.

### M11 — security layer

Реализовать TCP RC4 obfuscation, DH handshake, UDP obfuscation, secure identification и client credits по факту необходимости живой сети. Основные источники: [EncryptedStreamSocket.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/EncryptedStreamSocket.cpp), [EncryptedDatagramSocket.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/EncryptedDatagramSocket.cpp), [RC4Encrypt.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/RC4Encrypt.cpp), [ClientCredits.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/ClientCredits.cpp) и [ClientCreditsList.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/ClientCreditsList.cpp).

Критерий выхода: security layer не ломает соединение с eMule 0.50 и проходит согласованные vectors.

### M12 — IP-filter, GeoIP, UPnP, NAT-PMP

Реализовать `ipfilter.dat`, `ipfilter_static.dat`, URL auto-update, GeoIP lookup через bundled [GeoIP.dat](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1/GeoIP.dat), UPnP, NAT-PMP и firewall diagnostics. Основные источники: [IPFilter.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/IPFilter.cpp), [IPFilterScanner.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/IPFilterScanner.cpp) и [UDPFirewallTester.cpp](file:///O:/Work/Coding/aMule-2.3.3/src/kademlia/kademlia/UDPFirewallTester.cpp).

Критерий выхода: клиент корректно определяет low/high ID scenario и может автоматически открывать порты на поддерживаемых роутерах.

### M13 — CLI surface

Реализовать команды `status`, `connect`, `disconnect`, `server list`, `server add`, `server remove`, `search kad`, `search ed2k`, `search results`, `search clear`, `download add`, `download list`, `download pause`, `download resume`, `download cancel`, `download priority`, `share list`, `share add`, `share remove`, `share priority`, `kad status`, `kad bootstrap`, `stats`, `config show` и `config set`. Все команды должны поддерживать человекочитаемый и JSON output.

Критерий выхода: полный CLI flow доступен в one-shot и REPL режимах.

### M14 — daemon mode и process management

Реализовать фоновый процесс, PID/state control, управление через CLI, graceful shutdown и сигналы ОС. Автозапуск при старте ОС не входит в первый релиз.

Критерий выхода: daemon можно безопасно запускать, останавливать и опрашивать без потери состояния.

### M15 — compatibility/import layer

Базовые bundled ресурсы уже импортированы из [assets\v1](file:///O:/Work/Coding/Paradise_Lost_KAD_SA/AmuleD_v2/assets/v1) в DuckDB. Реализовать оставшийся import-once bridge для optional donor resources: `known.met`, `known2_64.met`, `clients.met`, preferences и partial files из donor `Temp`. Эти ресурсы не входят в базовый дистрибутив и должны подключаться только явной пользовательской командой.

Критерий выхода: v1 resources можно импортировать в native JSONC/DuckDB state без записи обратно в binary `.met/.dat` форматы.

### M16 — live-network validation и stabilization

Проверять последовательно: KAD bootstrap, KAD search, ED2K login, ED2K search, source discovery, partial download, resume, hashing, sharing, upload peer, obfuscation и long-run stability. Для каждого шага фиксировать packet traces, найденные несовместимости и поведенческие отличия от eMule 0.50.

Критерий выхода: клиент стабильно работает в реальной сети и готов к тестовому релизу.

## 9. Тестовая стратегия

Unit tests должны покрывать MD4/ED2K hashes, packet codec, tags, UInt128, routing buckets, part bitmaps, queue logic, IP-filter parser, link parser и storage migrations. Protocol simulators должны включать fake ED2K server, fake ED2K peer и fake Kad node на loopback. CLI smoke tests должны проверять one-shot, REPL, JSON output и daemon lifecycle.

Live-network tests включаются только после стабилизации local/loopback слоя. Для каждого протокольного изменения нужны regression vectors и, где возможно, hex captures совместимых клиентов.

## 10. Немедленный следующий шаг

Следующий рабочий шаг — завершить SHA1/AICH-слой M3, затем реализовать ED2K TCP login, server status и серверный search через codec/state слои. После этого добавляются Kad bootstrap и unified search.
