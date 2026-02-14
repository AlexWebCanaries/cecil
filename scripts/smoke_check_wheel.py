from __future__ import annotations

import cecil
from cecil.cost import load_pricing_catalog
from cecil.schema import load_schema


def main() -> int:
    exported = set(cecil.__all__)
    required = {"patch", "shutdown", "load_config", "build_event"}
    assert required.issubset(exported)

    schema = load_schema()
    assert schema.get("properties", {}).get("schema_version", {}).get("const") == "v1"

    pricing = load_pricing_catalog()
    assert pricing.version.startswith("pricing-")
    assert "gpt-4o-mini" in pricing.models

    print(sorted(cecil.__all__))
    print("wheel smoke check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
