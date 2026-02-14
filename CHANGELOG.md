# Changelog

## Unreleased

### feat
- add session-based usage analytics reporting API (`start_session`, report print/json/save)

### docs
- document sync-only provider instrumentation scope and async limitation

### fix
- correct provider compatibility CI env var so contract tests run (`CECIL_RUN_COMPAT`)
- fix usage analytics cache-breaker aggregation to read schema field `category`

### test
- add workflow regression test to prevent provider-compat env var drift
- add usage analytics regression test for cache-breaker reporting
