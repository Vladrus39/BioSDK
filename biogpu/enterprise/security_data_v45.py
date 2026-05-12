from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass(frozen=True)
class DataHandlingRule:
    id: str
    scope: str
    rule: str
    required_for: List[str]


def data_handling_rules() -> List[DataHandlingRule]:
    return [
        DataHandlingRule("DH1", "uploaded_data", "Customer neural data must be stored in isolated workspaces with job-level audit logs.", ["hosted_beta", "enterprise_on_prem"]),
        DataHandlingRule("DH2", "exports", "Result bundles must include manifest, parameters, metrics, and audit log; raw customer data should not be redistributed unless explicitly requested.", ["all"]),
        DataHandlingRule("DH3", "api_credentials", "External API credentials must never be stored in generated result bundles or committed to repository.", ["external_api", "hosted_beta"]),
        DataHandlingRule("DH4", "live_systems", "Live actuation is blocked by default and requires lab/vendor approval, allowlisted schema, and operator confirmation.", ["live_shadow", "closed_loop"]),
        DataHandlingRule("DH5", "claims", "Reports must distinguish replay, read-only live shadow, and approved live closed-loop evidence.", ["all"]),
    ]


def rules_as_dicts() -> List[Dict[str, object]]:
    return [asdict(r) for r in data_handling_rules()]
