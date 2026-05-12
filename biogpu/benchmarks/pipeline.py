from __future__ import annotations
import numpy as np
from biogpu.encoding import V1LikeEncoder
from biogpu.stimulation import StimulationPlanner, SimulationSafetyLayer
from biogpu.substrates import SimulatedMEA
from biogpu.reading import BasicSpikeFeatureExtractor
from biogpu.schemas import SpikeTrain


def _maybe_reset(substrate, cfg: dict) -> None:
    if cfg.get("reset_between_patterns", True) and hasattr(substrate, "reset_state"):
        substrate.reset_state()


def _feature_extractor_from_cfg(cfg: dict) -> BasicSpikeFeatureExtractor:
    feature_cfg = cfg.get("features", {}) or {}
    bins = int(feature_cfg.get("readout_bins", feature_cfg.get("bins", 1)))
    window_ms = float(feature_cfg.get("window_ms", cfg.get("readout_window_ms", 20.0)))
    return BasicSpikeFeatureExtractor(num_units=cfg["substrate"].get("reservoir_units", 256), window_ms=window_ms, readout_bins=bins)


def run_single_frame_pipeline(patterns, cfg, return_artifacts: bool = False):
    encoder = V1LikeEncoder(max_events_per_pixel=cfg["encoder"].get("max_events_per_pixel", 3), use_orientation_banks=cfg["encoder"].get("use_orientation_banks", True))
    planner = StimulationPlanner(substrate_id="simulated_mea")
    safety = SimulationSafetyLayer()
    substrate = SimulatedMEA(seed=cfg.get("seed", 42), **cfg["substrate"])
    substrate.connect()
    extractor = _feature_extractor_from_cfg(cfg)
    X_features, y, raw, spike_counts, active_ratios, event_counts = [], [], [], [], [], []
    sample_spikes: SpikeTrain | None = None
    sample_feature_counts = None
    for p in patterns:
        _maybe_reset(substrate, cfg)
        events = encoder.encode(p)
        stim = planner.plan(events)
        safety.validate(stim)
        substrate.send_stimulation(stim)
        spikes = substrate.read_spikes(window_ms=extractor.window_ms)
        fv = extractor.transform(spikes)
        if sample_spikes is None and len(spikes.unit_ids) > 0:
            sample_spikes = spikes
            sample_feature_counts = fv.values[:cfg["substrate"].get("reservoir_units", 256)].copy()
        X_features.append(fv.values)
        y.append(p.label)
        raw.append(p.data.reshape(-1))
        spike_counts.append(len(spikes.unit_ids))
        active_ratios.append(float(np.mean(np.asarray(fv.values[:cfg["substrate"].get("reservoir_units", 256)]) > 0)))
        event_counts.append(len(events.events))
    substrate.close()
    result = (np.asarray(X_features), np.asarray(y), np.asarray(raw), np.asarray(spike_counts), np.asarray(active_ratios), np.asarray(event_counts))
    if return_artifacts:
        return result + ({"sample_spikes": sample_spikes, "sample_counts": sample_feature_counts},)
    return result


def run_sequence_pipeline(patterns, cfg, return_artifacts: bool = False):
    encoder = V1LikeEncoder(max_events_per_pixel=cfg["encoder"].get("max_events_per_pixel", 3), use_orientation_banks=cfg["encoder"].get("use_orientation_banks", True))
    planner = StimulationPlanner(substrate_id="simulated_mea")
    safety = SimulationSafetyLayer()
    substrate = SimulatedMEA(seed=cfg.get("seed", 99), **cfg["substrate"])
    substrate.connect()
    extractor = _feature_extractor_from_cfg(cfg)
    X_features, y, raw, spike_counts, active_ratios, event_counts = [], [], [], [], [], []
    sample_spikes: SpikeTrain | None = None
    sample_feature_counts = None
    for p in patterns:
        _maybe_reset(substrate, cfg)
        total_events = 0
        for t, frame in enumerate(p.data):
            frame_pattern = type(p)(id=f"{p.id}_t{t}", data=frame, label=p.label, metadata=p.metadata)
            events = encoder.encode(frame_pattern)
            total_events += len(events.events)
            stim = planner.plan(events)
            safety.validate(stim)
            substrate.send_stimulation(stim)
        spikes = substrate.read_spikes(window_ms=extractor.window_ms)
        fv = extractor.transform(spikes)
        if sample_spikes is None and len(spikes.unit_ids) > 0:
            sample_spikes = spikes
            sample_feature_counts = fv.values[:cfg["substrate"].get("reservoir_units", 256)].copy()
        X_features.append(fv.values)
        y.append(p.label)
        raw.append(p.data.reshape(-1))
        spike_counts.append(len(spikes.unit_ids))
        active_ratios.append(float(np.mean(np.asarray(fv.values[:cfg["substrate"].get("reservoir_units", 256)]) > 0)))
        event_counts.append(total_events)
    substrate.close()
    result = (np.asarray(X_features), np.asarray(y), np.asarray(raw), np.asarray(spike_counts), np.asarray(active_ratios), np.asarray(event_counts))
    if return_artifacts:
        return result + ({"sample_spikes": sample_spikes, "sample_counts": sample_feature_counts},)
    return result
