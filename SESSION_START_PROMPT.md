# BioSDK v0.1.4 — Session Start Prompt

**Скопируй это в новое окно DeepSeek:**

---

Продолжай с `HANDOFF_FOR_DEEPSEEK_2026_05_11.md`. Проект BioSDK v0.1.4.

Путь: `C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap`
Python: `D:\GameDev\miniconda3\python.exe` (3.13.11)

## Быстрый старт

```powershell
cd "C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap"

# Статус
python _session_check.py

# Адаптеры
python _list_adapters.py

# Деплой (сборка + PyPI + GitHub)
python _deploy.py
```

## Приоритеты

1. Проверить почту `vladimoryachok@gmail.com` на ответ от FinalSpark
2. Если токен есть — сертифицировать FinalSpark адаптер, closed-loop на live hardware
3. Если токена нет — разослать beta-приглашения
4. Кросс-датасет классификация MCS (если появятся лейблы)
5. Опубликовать на реальный PyPI

## Что нового в v0.1.4

- **Security**: API-ключи через env vars, HMAC-подпись через `BIOSDK_SIGNING_KEY`
- **GitHub**: https://github.com/Vladrus39/BioSDK (6 коммитов)
- **Open Core**: MIT (community) + Commercial (enterprise)
- **pip**: `biosdk` v0.1.4 на TestPyPI
- **Деплой**: `python _deploy.py` — одной командой
- **CHANGELOG.md**, **SECURITY.md**, **.dockerignore** — добавлены
- **7 NSI-1.0 адаптеров, 83 conformance теста, 99.67% cross-modal**

## Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `HANDOFF_FOR_DEEPSEEK_2026_05_11.md` | Полная история |
| `MASTER_STATUS_V85.md` | Единый источник правды |
| `README.md` | Описание (GitHub + PyPI) |
| `pyproject.toml` | Метаданные pip пакета v0.1.4 |
| `_deploy.py` | Скрипт деплоя |
| `.env` | Все секреты (gitignored) |
| `CHANGELOG.md` | История версий |
| `SECURITY.md` | Политика безопасности |
| `LICENSE` + `COMMERCIAL_LICENSE.md` | Open Core лицензии |

## Важно

- Коммиты через `_git_commit.bat` (PowerShell ест кавычки)
- Токены: `.env` (не в git), `%USERPROFILE%\.pypirc`
- SSH: `C:\Users\vladi\.ssh\id_ed25519_biosdk`

---

*BioSDK v0.1.4. GitHub + PyPI. Open Core. 83 conformance. 99.67% cross-modal.*
