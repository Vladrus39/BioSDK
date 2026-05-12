"""Тест закрытого цикла на MEA-симуляторе v8.1.
Прогоняет 7 защитных гейтов (Shannon limits + approval + kill switch)
на синтетических данных 60-канального MEA.

Честный подход: тестируем оба сценария — PASS (безопасный протокол) и FAIL (нарушение каждого гейта).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Добавляем корень проекта в путь
PROJECT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT))

from biogpu.lab.closed_loop_v75 import (
    ClosedLoopController,
    StimulationProtocol,
    SafetyGate,
)
from biogpu.simulators.mea_v81 import MEASimulator, MEAConfig

NOW = datetime.now(timezone.utc).isoformat()
OUT_DIR = PROJECT / "outputs" / "v75_closed_loop_sim"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def make_safe_protocol() -> StimulationProtocol:
    """Безопасный протокол стимуляции — все параметры в пределах Шеннона."""
    return StimulationProtocol(
        protocol_id="safe_test_v75",
        name="Safe MEA Test Protocol (60ch, 50uA, 100nC, 200Hz, 600s)",
        max_amplitude_ua=50.0,
        max_pulse_width_us=200.0,
        max_frequency_hz=200.0,
        max_charge_per_phase_nc=100.0,
        max_duration_seconds=600.0,
        electrode_count=60,
        electrode_ids=list(range(60)),
        safety_limits={
            "max_amplitude_ua": 100.0,
            "max_charge_nc": 200.0,
            "max_frequency_hz": 500.0,
            "max_duration_s": 3600.0,
        },
        approved_by="Dr. Simulated Operator",
        approval_request_id="approval_sim_001",
        created_at=NOW,
    )


def make_unsafe_protocols() -> list[tuple[str, StimulationProtocol]]:
    """Протоколы, нарушающие каждый из 5 параметрических гейтов."""
    protocols = []

    # Gate 1: Превышение амплитуды
    p = make_safe_protocol()
    p.protocol_id = "fail_amplitude"
    p.name = "FAIL: Amplitude 150uA > 100uA limit"
    p.max_amplitude_ua = 150.0
    protocols.append(("amp_limit", p))

    # Gate 2: Превышение заряда
    p = make_safe_protocol()
    p.protocol_id = "fail_charge"
    p.name = "FAIL: Charge 300nC > 200nC limit"
    p.max_charge_per_phase_nc = 300.0
    protocols.append(("charge_limit", p))

    # Gate 3: Превышение частоты
    p = make_safe_protocol()
    p.protocol_id = "fail_frequency"
    p.name = "FAIL: Frequency 1000Hz > 500Hz limit"
    p.max_frequency_hz = 1000.0
    protocols.append(("freq_limit", p))

    # Gate 4: Превышение длительности
    p = make_safe_protocol()
    p.protocol_id = "fail_duration"
    p.name = "FAIL: Duration 7200s > 3600s limit"
    p.max_duration_seconds = 7200.0
    protocols.append(("duration_limit", p))

    # Gate 5: Несовпадение электродов
    p = make_safe_protocol()
    p.protocol_id = "fail_electrode"
    p.name = "FAIL: Electrode count 30 != len(ids)=60"
    p.electrode_count = 30  # mismatch with electrode_ids (60)
    protocols.append(("electrode_check", p))

    return protocols


def test_safe_protocol() -> dict:
    """Тест: безопасный протокол — все 7 гейтов должны пройти."""
    print("\n" + "=" * 60)
    print("ТЕСТ 1: Безопасный протокол (все гейты PASS)")
    print("=" * 60)

    ctrl = ClosedLoopController(PROJECT)
    ctrl.arm_kill_switch()
    protocol = make_safe_protocol()

    print(f"  Протокол: {protocol.name}")
    print(f"  Амплитуда: {protocol.max_amplitude_ua} µA (лимит 100)")
    print(f"  Заряд: {protocol.max_charge_per_phase_nc} nC (лимит 200)")
    print(f"  Частота: {protocol.max_frequency_hz} Гц (лимит 500)")
    print(f"  Длительность: {protocol.max_duration_seconds} с (лимит 3600)")
    print(f"  Электродов: {protocol.electrode_count} (IDs: {len(protocol.electrode_ids)})")
    print(f"  Kill switch: {'ARMED' if ctrl.kill_switch_armed else 'DISARMED'}")

    gates = ctrl.load_protocol(protocol, approval_verified=True)

    all_pass = all(g.passed for g in gates)
    print(f"\n  Результат: {'ВСЕ ГЕЙТЫ ПРОЙДЕНЫ' if all_pass else 'ЕСТЬ ОТКАЗЫ'}")
    for g in gates:
        status = "PASS" if g.passed else "FAIL"
        print(f"    [{status}] {g.gate_id}: {g.message} (actual={g.actual_value}, limit={g.limit_value})")

    print(f"  Actuation enabled: {ctrl.actuation_enabled}")

    # Пробуем актуацию
    if ctrl.actuation_enabled:
        result = ctrl.actuate(amplitude_ua=30.0, electrode_id=5)
        print(f"  Test actuation: {result}")

    ctrl.stop_session()

    return {
        "test": "safe_protocol_all_pass",
        "all_gates_passed": all_pass,
        "actuation_enabled": ctrl.actuation_enabled,
        "gates": [
            {"gate_id": g.gate_id, "passed": g.passed, "message": g.message}
            for g in gates
        ],
    }


def test_unsafe_protocols() -> list[dict]:
    """Тест: каждый небезопасный протокол — соответствующий гейт должен FAIL."""
    results = []
    unsafe = make_unsafe_protocols()

    for expected_fail_gate, protocol in unsafe:
        print(f"\n{'=' * 60}")
        print(f"ТЕСТ: Нарушение гейта — {expected_fail_gate}")
        print(f"{'=' * 60}")
        print(f"  Протокол: {protocol.name}")

        ctrl = ClosedLoopController(PROJECT)
        ctrl.arm_kill_switch()
        gates = ctrl.load_protocol(protocol, approval_verified=True)

        failed = [g for g in gates if not g.passed]
        passed = [g for g in gates if g.passed]

        # Целевой гейт должен упасть
        target_failed = any(g.gate_id == expected_fail_gate and not g.passed for g in gates)
        status_str = "ЦЕЛЕВОЙ ГЕЙТ УПАЛ (корректно)" if target_failed else "ЦЕЛЕВОЙ ГЕЙТ НЕ УПАЛ (ошибка!)"

        print(f"\n  Результат: {status_str}")
        print(f"  Упало гейтов: {len(failed)}/{len(gates)}")
        for g in gates:
            status = "PASS" if g.passed else "FAIL"
            highlight = " <-- ЦЕЛЬ" if g.gate_id == expected_fail_gate else ""
            print(f"    {status} {g.gate_id}: {g.message}{highlight}")

        print(f"  Actuation enabled: {ctrl.actuation_enabled}")

        ctrl.stop_session()

        results.append({
            "test": f"fail_{expected_fail_gate}",
            "expected_fail_gate": expected_fail_gate,
            "target_correctly_failed": target_failed,
            "total_gates_failed": len(failed),
            "failed_gates": [g.gate_id for g in failed],
            "gates": [
                {"gate_id": g.gate_id, "passed": g.passed, "message": g.message}
                for g in gates
            ],
        })

    return results


def test_approval_and_killswitch() -> list[dict]:
    """Тест: Gate 6 (approval) и Gate 7 (kill switch) отдельно."""
    results = []

    # Gate 6: No approval
    print(f"\n{'=' * 60}")
    print("ТЕСТ: Gate 6 — NO APPROVAL")
    print(f"{'=' * 60}")
    ctrl = ClosedLoopController(PROJECT)
    ctrl.arm_kill_switch()
    protocol = make_safe_protocol()
    protocol.protocol_id = "no_approval_test"
    protocol.name = "No Approval Test"
    gates = ctrl.load_protocol(protocol, approval_verified=False)  # <-- без подписи

    approval_gate = next(g for g in gates if g.gate_id == "approval_check")
    print(f"  Approval gate: {'PASS' if approval_gate.passed else 'FAIL'} {approval_gate.message}")
    print(f"  Actuation enabled: {ctrl.actuation_enabled}")
    ctrl.stop_session()

    results.append({
        "test": "fail_approval",
        "gate_passed": approval_gate.passed,
        "actuation_blocked": not ctrl.actuation_enabled,
    })

    # Gate 7: Kill switch not armed
    print(f"\n{'=' * 60}")
    print("ТЕСТ: Gate 7 — KILL SWITCH DISARMED")
    print(f"{'=' * 60}")
    ctrl2 = ClosedLoopController(PROJECT)
    ctrl2.kill_switch_armed = False  # явно разоружаем
    protocol2 = make_safe_protocol()
    protocol2.protocol_id = "kill_switch_disarmed_test"
    protocol2.name = "Kill Switch Disarmed Test"
    gates2 = ctrl2.load_protocol(protocol2, approval_verified=True)

    kill_gate = next(g for g in gates2 if g.gate_id == "kill_switch")
    print(f"  Kill switch gate: {'PASS' if kill_gate.passed else 'FAIL'} {kill_gate.message}")
    print(f"  Actuation enabled: {ctrl2.actuation_enabled}")
    ctrl2.stop_session()

    results.append({
        "test": "fail_kill_switch",
        "gate_passed": kill_gate.passed,
        "actuation_blocked": not ctrl2.actuation_enabled,
    })

    return results


def run_simulator_feed() -> dict:
    """Прогон симулятора: генерируем синтетику и смотрим статистику."""
    print(f"\n{'=' * 60}")
    print("СИМУЛЯТОР: MEA v8.1 — 60 каналов, 30 нейронов, 10 пакетов")
    print(f"{'=' * 60}")

    sim = MEASimulator(MEAConfig(
        channel_count=60,
        neuron_count=30,
        duration_seconds=10,
        sample_rate_hz=20000.0,
        seed=42,
    ))

    summary = sim.run_and_save(OUT_DIR / "simulator_output", packet_count=10)

    print(f"  Пакетов: {summary['packets_generated']}")
    print(f"  Всего спайков: {summary['total_spikes']}")
    print(f"  Средняя частота: {summary['avg_spike_rate_hz']:.1f} Гц")
    print(f"  Каналов активно: {summary['channels_active']}")
    print(f"  LFP-сэмплов: {summary['total_lfp_samples']}")
    print(f"  Байт данных: {summary['total_bytes']}")
    print(f"  SHA256: {summary['sha256'][:16]}...")

    return summary


def main():
    results = {
        "benchmark": "closed_loop_simulator_v75",
        "generated_at": NOW,
        "simulator": "MEA v8.1 (60ch, 30 neurons, 1308 spikes)",
        "safety_gates_total": 7,
        "tests": {},
    }

    # 1. Безопасный протокол
    results["tests"]["safe_protocol"] = test_safe_protocol()

    # 2. Нарушения параметрических гейтов
    results["tests"]["unsafe_protocols"] = test_unsafe_protocols()

    # 3. Approval + Kill switch
    results["tests"]["approval_and_killswitch"] = test_approval_and_killswitch()

    # 4. Симулятор
    results["tests"]["simulator_feed"] = run_simulator_feed()

    # Итоги
    safe = results["tests"]["safe_protocol"]
    unsafe = results["tests"]["unsafe_protocols"]
    ak = results["tests"]["approval_and_killswitch"]

    all_gate_tests_pass = (
        safe["all_gates_passed"]
        and all(u["target_correctly_failed"] for u in unsafe)
        and all(a["actuation_blocked"] for a in ak)
    )

    results["summary"] = {
        "safe_protocol_all_7_passed": safe["all_gates_passed"],
        "all_5_parametric_gates_correctly_fail": all(u["target_correctly_failed"] for u in unsafe),
        "approval_gate_blocks_actuation": ak[0]["actuation_blocked"],
        "kill_switch_gate_blocks_actuation": ak[1]["actuation_blocked"],
        "all_safety_tests_pass": all_gate_tests_pass,
        "simulator_spikes_generated": results["tests"]["simulator_feed"]["total_spikes"],
    }

    print("\n" + "=" * 60)
    print("ИТОГ ЗАКРЫТОГО ЦИКЛА НА СИМУЛЯТОРЕ")
    print("=" * 60)
    s = results["summary"]
    print(f"  Безопасный протокол (7/7): {'PASS' if s['safe_protocol_all_7_passed'] else 'FAIL'}")
    print(f"  5 параметрических гейтов FAIL: {'PASS' if s['all_5_parametric_gates_correctly_fail'] else 'FAIL'}")
    print(f"  Approval блокирует актуацию: {'PASS' if s['approval_gate_blocks_actuation'] else 'FAIL'}")
    print(f"  Kill switch блокирует актуацию: {'PASS' if s['kill_switch_gate_blocks_actuation'] else 'FAIL'}")
    print(f"  Спайков симулятора: {s['simulator_spikes_generated']}")
    print(f"\n  ОБЩИЙ ВЕРДИКТ: {'ВСЕ ТЕСТЫ ПРОЙДЕНЫ' if s['all_safety_tests_pass'] else 'ЕСТЬ ПРОВАЛЫ'}")

    # Сохраняем
    out_path = OUT_DIR / "V75_CLOSED_LOOP_SIMULATOR_RESULTS.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nРезультаты сохранены: {out_path}")

    return 0 if s["all_safety_tests_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
