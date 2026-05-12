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
python _deploy.py --prod
```

## Приоритеты

1. Проверить почту `vladimoryachok@gmail.com` на ответ от FinalSpark
2. Если токен есть — сертифицировать FinalSpark адаптер, closed-loop на live hardware
3. Если токена нет — разослать beta-приглашения, скачать CRCNS/3Brain датасеты
4. Кросс-датасет классификация с лейблами (Sleep, OpenNeuro, Tressoldi, Giroldini)
5. Публикация на реальный PyPI (уже опубликовано v0.1.4)

## Что нового в v0.1.4 (сессия 2026-05-12)

- **Перепозиционирование**: "Unified neural data library" вместо "vendor-neutral standard"
- **Реальный PyPI**: `pip install biosdk` (pypi.org, не test.pypi.org)
- **GitHub описание**: обновлено — Unified neural data library + evidence bundles
- **README переписан**: честные метрики per-dataset, evidence bundles на первом плане
- **Sleep PSG staging**: 66.7% cross-subject (5-class, chance 20%, 3.3x)
- **OpenNeuro eyes open/closed**: 83.7% cross-session (2-class, chance 50%, 1.7x)
- **4 размеченных датасета**: Sleep, OpenNeuro, Tressoldi, Giroldini
- **Честный бейзлайн**: sklearn SVM 50.7% vs BioSDK 52.4% на Giroldini MEA
- **Документация**: MASTER_STATUS, HANDOFF, CHANGELOG, SECURITY — всё обновлено
- **7 NSI-1.0 адаптеров, 83 conformance теста**

## Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `HANDOFF_FOR_DEEPSEEK_2026_05_11.md` | Полная история (v0.1.4 addendum) |
| `MASTER_STATUS_V85.md` | Единый источник правды (v0.1.4 addendum) |
| `README.md` | Описание (GitHub + PyPI) — переписан |
| `pyproject.toml` | Метаданные pip пакета v0.1.4 |
| `_deploy.py` | Скрипт деплоя (поддерживает --prod) |
| `.env` | Все секреты: GitHub, PyPI, FinalSpark (gitignored) |
| `CHANGELOG.md` | История версий (включая [0.1.4]) |
| `SECURITY.md` | Политика безопасности (0.1.4 в supported versions) |
| `LICENSE` + `COMMERCIAL_LICENSE.md` | Open Core лицензии |

## Результаты классификации (все датасеты)

| Dataset | Accuracy | Chance | Improvement | Samples |
|---------|----------|--------|-------------|---------|
| OpenNeuro Eyes (2-class) | 83.7% | 50% | 1.7x | 647 |
| Sleep PSG (5-class) | 66.7% | 20% | 3.3x | 303 |
| Tressoldi EEG (2-class) | 64.2% | 50% | 1.3x | 10,878 |
| Giroldini MEA (4-class) | 52.4% | 25% | 2.1x | 11,547 |

**Честный бейзлайн**: sklearn SVM 50.7% на Giroldini MEA. BioSDK: +1.7 п.п.
Ценность — в unified API + evidence bundles, не в алгоритмическом преимуществе.

## Важно

- **Позиционирование**: Unified neural data library, НЕ standard, НЕ OS, НЕ Vulkan
- **Токены**: `.env` (не в git). PyPI — реальный токен. `%USERPROFILE%\.pypirc` — testpypi
- SSH: `C:\Users\vladi\.ssh\id_ed25519_biosdk`
- Коммиты: `_deploy.py` делает всё сам. Для ручных — `_git_commit.bat`
- Длинные однострочники ломаются — писать в .py файлы
- Эмодзи и юникод-стрелки (→, ✅) крашат консоль — избегать
- Dashboard на порту 8420 (может висеть)

---

*BioSDK v0.1.4. Unified neural data library. Real PyPI. Open Core. 4 labeled datasets. Evidence bundles.*
