import json
from datetime import datetime, timezone

path = r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap\PROJECT_STATUS_V85.json"
with open(path, "r", encoding="utf-8") as f:
    s = json.load(f)

now = datetime.now(timezone.utc).isoformat()

s["version"] = "v9.5"
s["session_date"] = "2026-05-12"
s["generated_at"] = now

# Обновлённая кросс-модальная классификация
s["cross_modal_classification_v95"] = {
    "benchmark": "cross_modal_classification_v95",
    "n_datasets": 6,
    "n_windows": 269,
    "approaches_tested": 3,
    "results": {
        "first6_baseline": 0.9433,
        "channel_averaged": 0.9967,
        "pca_projected": 0.5289,
        "best_approach": "channel_averaged",
        "best_accuracy": 0.9967,
        "improvement_vs_baseline": 0.0534,
    },
    "honest_interpretation": "Канально-усреднённые NSI-1.0 признаки дают практически идеальную кросс-модальную классификацию (99.67%). PCA проваливается (52.89%) из-за несовместимых базисов. NSI-1.0 признаки робастны к методу агрегации. Все 6 фич несут информацию всех каналов.",
    "output": "outputs/v92_cross_modal_classification/V95_CROSS_MODAL_IMPROVED.json",
}

# Сравнительный анализ BioSDK vs FinalSpark
s["biosdk_vs_finalspark_v95"] = {
    "document": "docs/BIOSDK_VS_FINALSPARK_V95.md",
    "key_finding": "BioSDK и FinalSpark не конкуренты, а потенциальные партнёры. Разные уровни стека: стандарт vs платформа.",
    "synergy": [
        "FinalSpark даёт доступ к живым нейронам",
        "BioSDK даёт стандартный интерфейс для сравнения с ЛЮБЫМИ другими данными",
        "Safety gates BioSDK валидируют стимуляцию FinalSpark",
        "Evidence bundles для воспроизводимых публикаций",
    ],
}

# Статья марта 2025
s["finalspark_march_2025_update"] = {
    "date": "2025-03-28",
    "source": "bgr.com / stemfast.com",
    "key_claims": {
        "first_bioprocessor": True,
        "energy_efficiency": "миллион раз меньше энергии чем цифровые чипы",
        "organoids": 16,
        "institutions_with_access": 9,
        "payment": "криптовалюта",
    },
    "note": "Эти заявления не верифицированы независимо. BioSDK не делает заявлений об энергоэффективности.",
}

# Обновляем пробелы
s["honest_gaps_closed_this_session"].extend([
    "cross_modal_classification_improved_99_67_percent_v95",
    "biosdk_vs_finalspark_comparison_v95",
    "finalspark_all_links_reviewed_v95",
])

s["honest_gaps_remaining"] = [
    "cross_dataset_classification_accuracy_mcs_no_labels",
    "external_api_validation_awaiting_finalspark_token",
    "closed_loop_hardware_still_required",
    "zero_beta_participants_but_packet_ready",
]

s["bio_compute_pipeline"]["cross_modal_classification_accuracy"] = 0.9967
s["bio_compute_pipeline"]["cross_modal_classification_method"] = "channel_averaged"

with open(path, "w", encoding="utf-8") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)

print("PROJECT_STATUS_V85.json обновлён до v9.5")
print(f"Кросс-модальная (лучшая): {s['cross_modal_classification_v95']['results']['best_accuracy']}")
print(f"Пробелов осталось: {len(s['honest_gaps_remaining'])}")
