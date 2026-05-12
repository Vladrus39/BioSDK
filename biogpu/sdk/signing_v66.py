"""Trusted Release Signing v6.6 — HMAC-SHA256 artifact signing pipeline."""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class SignedArtifact:
    path: str
    sha256: str
    signature: str
    algorithm: str = "HMAC-SHA256"
    signed_at: str = ""
    key_id: str = "v6.6-release-signing"


def load_signing_key(key_path: str | Path = "data/production/keys/release_signing.key") -> bytes:
    return Path(key_path).read_text(encoding="utf-8").strip().encode()


def sign_file(file_path: str | Path, key: bytes | None = None) -> SignedArtifact:
    if key is None:
        key = load_signing_key()
    path = Path(file_path)
    content = path.read_bytes()
    sha = hashlib.sha256(content).hexdigest()
    sig = hmac.new(key, content, hashlib.sha256).hexdigest()
    from datetime import datetime
    return SignedArtifact(
        path=str(path),
        sha256=sha,
        signature=sig,
        signed_at=datetime.utcnow().isoformat() + "Z",
    )


def verify_file(file_path: str | Path, signature: str, key: bytes | None = None) -> bool:
    if key is None:
        key = load_signing_key()
    content = Path(file_path).read_bytes()
    expected = hmac.new(key, content, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def sign_artifact_bundle(bundle_dir: str | Path, key: bytes | None = None) -> dict[str, Any]:
    bundle = Path(bundle_dir)
    results = []
    for f in sorted(bundle.rglob("*")):
        if f.is_file():
            signed = sign_file(f, key)
            results.append(asdict(signed))
    manifest = {
        "bundle": str(bundle),
        "algorithm": "HMAC-SHA256",
        "artifact_count": len(results),
        "artifacts": results,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    manifest_path = bundle / "SIGNING_MANIFEST_V66.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


print("v6.6 signing OK")
