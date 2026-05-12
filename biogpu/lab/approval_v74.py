"""BioSDK Lab Approval Workflow v7.4 — Multi-stage operator approvals."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    PENDING_OPERATOR = "pending_operator"
    PENDING_SAFETY = "pending_safety"
    APPROVED = "approved"
    DENIED = "denied"
    REVOKED = "revoked"


@dataclass
class ApprovalRequest:
    request_id: str
    title: str
    protocol_type: str  # replay, read_only, live_shadow, live_actuation
    description: str = ""
    operator_id: str = ""
    safety_reviewer_id: str = ""
    status: ApprovalStatus = ApprovalStatus.DRAFT
    signed_operator: bool = False
    signed_safety: bool = False
    operator_signature: str = ""
    safety_signature: str = ""
    created_at: str = ""
    updated_at: str = ""
    approved_at: str = ""
    expires_at: str = ""
    constraints: dict[str, Any] = field(default_factory=dict)
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


class ApprovalWorkflow:
    """Multi-stage lab approval workflow."""

    def __init__(self, project_root: str | Path = "."):
        self.root = Path(project_root)
        self.approvals_dir = self.root / "data" / "production" / "approvals"
        self.approvals_dir.mkdir(parents=True, exist_ok=True)
        self.requests: dict[str, ApprovalRequest] = {}
        self._load()

    def _load(self) -> None:
        for f in self.approvals_dir.glob("approval_*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["status"] = ApprovalStatus(data["status"])
                req = ApprovalRequest(**data)
                self.requests[req.request_id] = req
            except Exception:
                continue

    def _save(self, req: ApprovalRequest) -> None:
        path = self.approvals_dir / f"approval_{req.request_id}.json"
        path.write_text(json.dumps(req.to_dict(), indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    def create_request(self, title: str, protocol_type: str, description: str = "", operator_id: str = "") -> ApprovalRequest:
        import uuid
        req = ApprovalRequest(
            request_id=str(uuid.uuid4())[:12],
            title=title,
            protocol_type=protocol_type,
            description=description,
            operator_id=operator_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        req.audit_log.append({"action": "created", "timestamp": req.created_at, "actor": operator_id})
        self.requests[req.request_id] = req
        self._save(req)
        return req

    def submit_for_operator(self, request_id: str, operator_id: str) -> ApprovalRequest | None:
        req = self.requests.get(request_id)
        if not req or req.status != ApprovalStatus.DRAFT:
            return None
        req.status = ApprovalStatus.PENDING_OPERATOR
        req.operator_id = operator_id
        req.updated_at = datetime.now(timezone.utc).isoformat()
        req.audit_log.append({"action": "submitted_operator", "timestamp": req.updated_at, "actor": operator_id})
        self._save(req)
        return req

    def operator_approve(self, request_id: str, signature: str) -> ApprovalRequest | None:
        req = self.requests.get(request_id)
        if not req or req.status != ApprovalStatus.PENDING_OPERATOR:
            return None
        req.signed_operator = True
        req.operator_signature = hashlib.sha256(signature.encode()).hexdigest()
        req.status = ApprovalStatus.PENDING_SAFETY
        req.updated_at = datetime.now(timezone.utc).isoformat()
        req.audit_log.append({"action": "operator_approved", "timestamp": req.updated_at})
        self._save(req)
        return req

    def safety_approve(self, request_id: str, signature: str, constraints: dict[str, Any] | None = None) -> ApprovalRequest | None:
        req = self.requests.get(request_id)
        if not req or req.status != ApprovalStatus.PENDING_SAFETY:
            return None
        req.signed_safety = True
        req.safety_signature = hashlib.sha256(signature.encode()).hexdigest()
        if constraints:
            req.constraints.update(constraints)
        req.status = ApprovalStatus.APPROVED
        req.approved_at = datetime.now(timezone.utc).isoformat()
        req.expires_at = (datetime.now(timezone.utc).timestamp() + 86400)  # 24h default
        req.expires_at = datetime.fromtimestamp(req.expires_at, tz=timezone.utc).isoformat()
        req.updated_at = datetime.now(timezone.utc).isoformat()
        req.audit_log.append({"action": "safety_approved", "timestamp": req.updated_at})
        self._save(req)
        return req

    def deny(self, request_id: str, reason: str) -> ApprovalRequest | None:
        req = self.requests.get(request_id)
        if not req:
            return None
        req.status = ApprovalStatus.DENIED
        req.updated_at = datetime.now(timezone.utc).isoformat()
        req.audit_log.append({"action": "denied", "reason": reason, "timestamp": req.updated_at})
        self._save(req)
        return req

    def revoke(self, request_id: str, reason: str) -> ApprovalRequest | None:
        req = self.requests.get(request_id)
        if not req or req.status != ApprovalStatus.APPROVED:
            return None
        req.status = ApprovalStatus.REVOKED
        req.updated_at = datetime.now(timezone.utc).isoformat()
        req.audit_log.append({"action": "revoked", "reason": reason, "timestamp": req.updated_at})
        self._save(req)
        return req

    def is_approved(self, request_id: str) -> bool:
        req = self.requests.get(request_id)
        if not req or req.status != ApprovalStatus.APPROVED:
            return False
        # Check expiry
        if req.expires_at:
            exp = datetime.fromisoformat(req.expires_at)
            if datetime.now(timezone.utc) > exp:
                return False
        return True
