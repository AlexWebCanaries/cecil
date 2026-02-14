# Compatibility Matrix

## Python
- 3.9
- 3.10
- 3.11
- 3.12

## Provider SDK ranges (validated via mocks in this repo)
- OpenAI: `>=1.40.0, <=1.51.0` (CI contract workflow)
- Anthropic: `>=0.35.0, <=0.39.0` (CI contract workflow)
- Contract target paths:
  - `openai.resources.chat.completions.Completions.create`
  - `anthropic.resources.messages.Messages.create`

## Non-goals
- SaaS backend services
- Dashboard/frontend code
- Cloud infrastructure provisioning

## Known limitations
- Cost estimation is fixture-based and model coverage is not exhaustive.
- Adapter patching is best-effort and relies on provider SDK internals.
