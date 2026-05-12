# BioSDK v0.1.3 — Session Start Prompt

**Скопируй это в новое окно DeepSeek:**

---

Продолжай с `HANDOFF_FOR_DEEPSEEK_2026_05_11.md`. Проект BioSDK v0.1.3.

Путь: `C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap`
Python: `D:\GameDev\miniconda3\python.exe` (3.13.11)

## Быстрый старт

```powershell
cd "C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap"

# Статус
python _session_check.py

# Адаптеры (должно быть 7)
python _list_adapters.py

# Кросс-модальная классификация (99.67%)
python _bic_os_cross_modal_v95.py

# Деплой (сборка + PyPI + GitHub)
python _deploy.py
```

## Приоритеты

1. Проверить почту `vladimoryachok@gmail.com` на ответ от FinalSpark
2. Если токен есть — сертифицировать FinalSpark адаптер, closed-loop на live hardware
3. Если токена нет — разослать beta-приглашения
4. Кросс-датасет классификация MCS (если появятся лейблы)
5. Опубликовать на реальный PyPI

## Что нового в v0.1.3

- **GitHub**: https://github.com/Vladrus39/BioSDK (публичный, 1159 файлов)
- **Open Core**: MIT (community) + Commercial (enterprise)
- **pip пакет**: `biosdk` v0.1.3 на TestPyPI
- **Деплой**: `python _deploy.py` — сборка + PyPI + GitHub + проверка одной командой
- **Секреты**: `.env` — все токены/ключи в одном месте (gitignored)
- **Единый README**: один файл для GitHub и PyPI
- **7 NSI-1.0 адаптеров** (5 certified + 1 skeleton + 1 reference)
- **99.67%** кросс-модальная классификация (channel-averaged, 6.0x chance)
- **FinalSpark адаптер**: скелет готов, 41/41 conformance на моках, ждёт токен

## Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `HANDOFF_FOR_DEEPSEEK_2026_05_11.md` | Полная история сессий v8.5->v0.1.3 |
| `MASTER_STATUS_V85.md` | Единый источник правды |
| `PROJECT_STATUS_V85.json` | Машинно-читаемый статус |
| `README.md` | Описание проекта (GitHub + PyPI) |
| `pyproject.toml` | Метаданные pip пакета |
| `_deploy.py` | Скрипт полного деплоя |
| `.env` | Все секреты проекта |
| `LICENSE` | MIT (community tier) |
| `COMMERCIAL_LICENSE.md` | Enterprise условия |

## Ссылки

| Ресурс | URL |
|--------|-----|
| GitHub | https://github.com/Vladrus39/BioSDK |
| PyPI | https://test.pypi.org/project/biosdk/ |
| Установка | `pip install -i https://test.pypi.org/simple/ biosdk` |

## Важно

- Длинные однострочники в shell ломаются — пиши в `.py` файлы
- Коммиты через `_git_commit.bat` (PowerShell ест кавычки)
- Dashboard на порту 8420 (может висеть с прошлой сессии)
- Токен test.pypi.org в `%USERPROFILE%\.pypirc` (секция `[testpypi]`)
- GitHub токен в `.env` (`GITHUB_TOKEN`)
- SSH ключ: `C:\Users\vladi\.ssh\id_ed25519_biosdk`

---

*BioSDK v0.1.3. GitHub + PyPI. Open Core. 7 адаптеров. 83 conformance теста. 99.67% cross-modal.*
