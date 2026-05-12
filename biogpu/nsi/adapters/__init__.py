"""NSI-1.0 adapter implementations."""
from biogpu.nsi import NSIAdapter

# Registry of available adapters
_ADAPTERS: dict[str, type[NSIAdapter]] = {}


def register_adapter(adapter_cls: type[NSIAdapter]) -> type[NSIAdapter]:
    """Register an NSI-1.0 adapter class."""
    _ADAPTERS[adapter_cls.adapter_id] = adapter_cls
    return adapter_cls


def get_adapter(adapter_id: str) -> type[NSIAdapter] | None:
    """Get a registered adapter by id."""
    return _ADAPTERS.get(adapter_id)


def list_adapters() -> list[str]:
    """List all registered adapter ids."""
    return list(_ADAPTERS.keys())


# Import adapters to trigger registration
from biogpu.nsi.adapters import mcs  # noqa: F401
from biogpu.nsi.adapters import giroldini  # noqa: F401
from biogpu.nsi.adapters import dandi  # noqa: F401
from biogpu.nsi.adapters import edf  # noqa: F401
from biogpu.nsi.adapters import gcp2  # noqa: F401
from biogpu.nsi.adapters import tressoldi  # noqa: F401
from biogpu.nsi.adapters import finalspark  # noqa: F401
