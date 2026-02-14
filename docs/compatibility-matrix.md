# Compatibility Matrix

## Python
- 3.9
- 3.10
- 3.11
- 3.12

## Provider SDK ranges (enforced by CI)
- OpenAI: `1.40.0`, `1.51.0`
- Anthropic: `0.35.0`, `0.39.0`
- Contract target paths:
  - `openai.resources.chat.completions.Completions.create`
  - `anthropic.resources.messages.Messages.create`

### CI Mapping
- Workflow: [`provider-compat.yml`](/Users/alexmilman/Dev/cecil/.github/workflows/provider-compat.yml)
- Job: `matrix`
- Test file: `/Users/alexmilman/Dev/cecil/tests/compat/test_provider_contracts.py`
- Enforcement:
  - installs pinned provider SDK versions from matrix
  - sets expected version env vars
  - fails if import path or version assertions fail

## Non-goals
- SaaS backend services
- Dashboard/frontend code
- Cloud infrastructure provisioning

## Known limitations
- Cost estimation is fixture-based and model coverage is not exhaustive.
- Adapter patching is best-effort and relies on provider SDK internals.
