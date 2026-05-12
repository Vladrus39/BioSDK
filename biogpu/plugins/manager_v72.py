"""BioSDK Plugin Manager v7.2 — Adapter registry, loader, certification."""
from __future__ import annotations

import importlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class PluginManifest:
    name: str
    version: str
    plugin_type: str  # adapter, decoder, encoder, readout, dataset, safety
    description: str = ""
    author: str = ""
    entry_point: str = ""
    capabilities: list[str] = field(default_factory=list)
    safety_level: str = "read_only"  # read_only, live_shadow, live_actuation
    certified: bool = False
    certification_hash: str = ""
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_file(cls, path: str | Path) -> "PluginManifest":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class PluginRegistry:
    """Central plugin registry for BioSDK."""

    def __init__(self, root: str | Path = "biogpu/plugins/registry"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.plugins: dict[str, PluginManifest] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        index = self.root / "plugin_index.json"
        if index.exists():
            data = json.loads(index.read_text(encoding="utf-8"))
            for item in data.get("plugins", []):
                manifest = PluginManifest(**item)
                self.plugins[manifest.name] = manifest

    def _save_registry(self) -> None:
        index = self.root / "plugin_index.json"
        index.write_text(json.dumps({
            "version": "v7.2",
            "plugin_count": len(self.plugins),
            "plugins": [p.to_dict() for p in self.plugins.values()],
        }, indent=2, ensure_ascii=False), encoding="utf-8")

    def register(self, manifest: PluginManifest) -> None:
        self.plugins[manifest.name] = manifest
        self._save_registry()

    def unregister(self, name: str) -> None:
        self.plugins.pop(name, None)
        self._save_registry()

    def get(self, name: str) -> PluginManifest | None:
        return self.plugins.get(name)

    def list_by_type(self, plugin_type: str) -> list[PluginManifest]:
        return [p for p in self.plugins.values() if p.plugin_type == plugin_type]

    def list_certified(self) -> list[PluginManifest]:
        return [p for p in self.plugins.values() if p.certified]

    def certify(self, name: str, certification_data: str) -> bool:
        import hashlib
        plugin = self.plugins.get(name)
        if not plugin:
            return False
        plugin.certified = True
        plugin.certification_hash = hashlib.sha256(certification_data.encode()).hexdigest()
        self._save_registry()
        return True

    def decertify(self, name: str) -> bool:
        plugin = self.plugins.get(name)
        if not plugin:
            return False
        plugin.certified = False
        plugin.certification_hash = ""
        self._save_registry()
        return True


def discover_plugins(search_path: str | Path = "biogpu/plugins/adapters") -> list[PluginManifest]:
    """Discover plugin manifests in a directory tree."""
    base = Path(search_path)
    if not base.exists():
        return []
    manifests = []
    for manifest_file in base.rglob("plugin_manifest.json"):
        try:
            manifest = PluginManifest.from_file(manifest_file)
            manifests.append(manifest)
        except Exception:
            continue
    return manifests


def load_plugin(manifest: PluginManifest, search_path: str | Path = ".") -> Any:
    """Load a plugin by its entry point."""
    if not manifest.entry_point:
        raise ValueError(f"Plugin {manifest.name} has no entry_point")
    # entry_point format: "module.path:ClassName"
    module_path, _, class_name = manifest.entry_point.partition(":")
    module = importlib.import_module(module_path)
    return getattr(module, class_name, None)
