# NSI-1.0 — Neural Signal Interface v1.0

**Спецификация стандарта**
**Версия**: 1.0 | **Дата**: 2026-05-12 | **Статус**: Черновик

---

## 1. Назначение

NSI-1.0 (Neural Signal Interface) — это **вендор-нейтральный протокол** для чтения,
обработки и сравнения нейрофизиологических данных из любых источников.

**Аналогия**: NSI-1.0 для нейроданных — то же, что Vulkan для GPU, ROS для робототехники,
FHIR для медицинских записей. Единый интерфейс, разные реализации.

**Ключевой принцип**: NSI-1.0 НЕ преобразует одну модальность в другую. Он даёт
общий ЯЗЫК для сравнения. MEA остаётся MEA, EEG остаётся EEG — но через NSI-1.0
их МОЖНО сравнить.

---

## 2. Базовый протокол

Каждый NSI-1.0 адаптер ОБЯЗАН реализовать 5 методов:

```python
class NSIAdapter:
    adapter_id: str       # Уникальный идентификатор (напр. "mcs_mea2100")
    vendor: str           # Производитель (напр. "mcs")
    modality: str         # Модальность (напр. "mea", "eeg", "ecephys")

    def open(path) -> NSIDataset:           # (1) Открыть источник данных
    def metadata(path) -> NSIMetadata:      # (2) Прочитать метаданные
    def iter_windows(path, window_s, overlap) -> Iterator[ndarray]:  # (3) Итератор окон
    def feature_vector(window) -> ndarray:  # (4) Извлечь признаки из окна
    def close():                            # (5) Освободить ресурсы
```

### 2.1. open(path) → NSIDataset

Открывает источник данных и возвращает структуру NSIDataset.

**Контракт**:
- `path` — строка или Path. Для файловых адаптеров — путь к файлу. Для API-адаптеров — идентификатор ресурса.
- Возвращает `NSIDataset` с полями: `.metadata`, `.data`, `.feature_names`, `._adapter`
- `.data` должен быть `np.ndarray` формы `(n_channels, n_samples)` или `None` если данные недоступны
- При отсутствии данных (no token) — возвращает `.data` заполненный нулями с корректной размерностью

### 2.2. metadata(path) → NSIMetadata

Читает метаданные БЕЗ загрузки всех данных. Должен работать всегда, даже без токена.

**Контракт**:
- Возвращает `NSIMetadata` с полями:
  - `source_path: str` — путь/идентификатор источника
  - `source_format: str` — формат ("hdf5", "nwb", "edf", "csv", "xlsx", "neuroplatform_api")
  - `vendor: str` — производитель
  - `modality: str` — модальность
  - `channel_count: int` — количество каналов
  - `sample_rate_hz: float` — частота дискретизации
  - `duration_s: float | None` — длительность (None для потоковых данных)
  - `extra: dict` — дополнительные поля (свободная форма)

### 2.3. iter_windows(path, window_s, overlap) → Iterator[ndarray]

Итератор скользящих окон по данным.

**Контракт**:
- `window_s: float` — размер окна в секундах
- `overlap: float` — перекрытие (0.0 = без перекрытия, 0.5 = 50%)
- Генерирует `np.ndarray` формы `(n_channels, window_samples)`
- Тип: `float32`
- При отсутствии данных — возвращает пустой итератор (не ошибку)

### 2.4. feature_vector(window) → ndarray

Извлекает 6 стандартных признаков на каждый канал из окна.

**Стандартные признаки (на канал)**:
| # | Название | Формула | Размерность |
|---|---------|--------|------------|
| 0 | RMS | sqrt(mean(x²)) | амплитуда |
| 1 | MAV | mean(|x|) | амплитуда |
| 2 | ZC | sum(diff(sign(x))) | счёт |
| 3 | VAR | var(x) | амплитуда² |
| 4 | PEAK | max(|x|) | амплитуда |
| 5 | SKEW | mean(x³)/std(x)³ | безразмерная |

**Контракт**:
- Вход: `window` формы `(n_channels, n_samples)`, `float32`
- Выход: `ndarray` длины `n_channels * 6`, `float32`
- Порядок: `ch0_rms, ch0_mav, ch0_zc, ch0_var, ch0_peak, ch0_skew, ch1_rms, ...`

**Именование признаков**: `ch{i}_{feat}` где `feat ∈ {rms, mav, zc, var, peak, skew}`

### 2.5. close()

Освобождает ресурсы. Для файловых адаптеров — закрывает файлы. Для API — разрывает соединение.

**Контракт**:
- Идемпотентный: повторный вызов не должен вызывать ошибку
- Не бросает исключений при нормальном завершении

---

## 3. Conformance-тесты

Каждый адаптер ОБЯЗАН пройти **8 обязательных тестов**:

| # | Тест | Что проверяет |
|---|-----|--------------|
| 1 | Регистрация | adapter_id, vendor, modality определены |
| 2 | Метаданные | metadata() возвращает корректный NSIMetadata |
| 3 | Разные источники | metadata() работает для всех допустимых path |
| 4 | Открытие | open() возвращает NSIDataset с правильной размерностью |
| 5 | Признаки | feature_vector() возвращает n_channels * 6 значений |
| 6 | Конечность | Все признаки — конечные числа |
| 7 | Окна | iter_windows() генерирует окна правильной формы |
| 8 | Закрытие | close() не бросает исключений |

**Дополнительные тесты** (для API-адаптеров):
| # | Тест | Что проверяет |
|---|-----|--------------|
| 9 | Safety gates | check_stimulation_safety() корректно валидирует параметры |
| 10 | Graceful failure | При отсутствии токена — метаданные работают, данные = zeros |

---

## 4. Реестр адаптеров

**Сертифицированные (42/42 conformance):**

| # | ID | Производитель | Модальность | Каналы | Частота | Тесты |
|---|----|-------------|-----------|--------|--------|-------|
| 1 | mcs_mea2100 | MCS | MEA | 17 | 500 Hz | 8/8 |
| 2 | dandi_nwb | DANDI/Allen | ecephys | 5-96 | 100-30k Hz | 8/8 |
| 3 | physionet_edf | PhysioNet | Sleep/EEG | 7-21 | 100-200 Hz | 8/8 |
| 4 | gcp2_csv | GCP2 | RNG | 1 | ~1/60 Hz | 9/9 |
| 5 | tressoldi_h3 | Tressoldi | EEG | 14 | 128 Hz | 9/9 |

**Скелет (41/41 на моках, ждёт токен):**

| # | ID | Производитель | Модальность | Каналы | Частота | Тесты |
|---|----|-------------|-----------|--------|--------|-------|
| 6 | finalspark_neuroplatform | FinalSpark | MEA wetware | 8 | 30 kHz | 41/41 mock |

**Эталонный (не сертифицирован):**
| # | ID | Производитель | Модальность | Каналы | Частота |
|---|----|-------------|-----------|--------|--------|
| — | giroldini_mea | Giroldini | MEA | 59 | 20 kHz |

---

## 5. Модель данных

### NSIDataset
```
NSIDataset:
    metadata: NSIMetadata
    data: np.ndarray          # (n_channels, n_samples) float32
    feature_names: list[str]  # ["ch0_rms", "ch0_mav", ...]
    _adapter: NSIAdapter     # обратная ссылка
```

### NSIMetadata
```
NSIMetadata:
    source_path: str
    source_format: str       # "hdf5" | "nwb" | "edf" | "csv" | "xlsx" | "neuroplatform_api"
    vendor: str
    modality: str            # "mea" | "eeg" | "sleep" | "rng" | "ecephys" | "mea_wetware"
    channel_count: int
    sample_rate_hz: float
    duration_s: float | None
    extra: dict              # свободные метаданные
```

---

## 6. Правила сертификации

Адаптер считается **сертифицированным NSI-1.0**, если:

1. Проходит ВСЕ 8 обязательных conformance-тестов
2. Реализует все 5 методов протокола
3. `feature_vector()` использует стандартные 6 признаков (RMS, MAV, ZC, VAR, PEAK, SKEW)
4. Именование признаков соответствует `ch{i}_{feat}`
5. `metadata()` работает без данных (быстрый проброс)
6. `close()` идемпотентен

**Сертификация НЕ требует**:
- Наличия реальных данных (можно тестировать на синтетике)
- Токена/доступа к железу
- Специфичных для вендора фич (они идут в `extra`)

---

## 7. Пример использования

```python
from biogpu.nsi.adapters.mcs import McsMea2100Adapter

adapter = McsMea2100Adapter()

# Открыть файл — один вызов для любого формата
ds = adapter.open("recording.h5")
print(f"{ds.metadata.vendor}: {ds.metadata.channel_count} каналов, "
      f"{ds.metadata.sample_rate_hz} Гц")

# Извлечь признаки из окон
X = []
for window in adapter.iter_windows("recording.h5", window_s=1.0):
    features = adapter.feature_vector(window)
    X.append(features)
X = np.array(X)
print(f"Матрица признаков: {X.shape}")

# Сравнить с данными из другого источника
from biogpu.nsi.adapters.dandi import DandiNWBAdapter
dandi = DandiNWBAdapter()
ds2 = dandi.open("allen_visual.nwb")
# Те же 6 признаков на канал — можно сравнивать напрямую
```

---

## 8. Философия стандарта

1. **Простота**: 5 методов, 6 признаков. Освоить за час.
2. **Расширяемость**: `extra: dict` для любых вендор-специфичных данных.
3. **Честность**: metadata-only mode когда нет доступа к данным. Не скрываем ошибки.
4. **Сравнимость**: одни и те же признаки на всех модальностях.
5. **Безопасность**: Shannon limits на стимуляцию встроены в протокол.

---

*NSI-1.0 v1.0. 5 методов. 6 признаков. Любые нейроданные.*
