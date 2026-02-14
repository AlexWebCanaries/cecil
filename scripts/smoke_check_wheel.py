from __future__ import annotations

import llm_observer
from llm_observer.cost import load_pricing_catalog
from llm_observer.schema import load_schema


def main() -> int:
    exported = set(llm_observer.__all__)
    required = {"patch", "shutdown", "load_config", "build_event"}
    assert required.issubset(exported)

    schema = load_schema()
    assert schema.get("properties", {}).get("schema_version", {}).get("const") == "v1"

    pricing = load_pricing_catalog()
    assert pricing.version.startswith("pricing-")
    assert "gpt-4o-mini" in pricing.models

    print(sorted(llm_observer.__all__))
    print("wheel smoke check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
