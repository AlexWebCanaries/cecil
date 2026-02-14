# Pricing Data Policy

Pricing catalog location:
- `shared/pricing/pricing_v1.json`

Stale-data policy:
- Catalog must include `updated_at`.
- Unknown model path is non-fatal and labeled `unknown_model`.
- Pricing refreshes should be done by updating the catalog artifact without changing estimator core logic.

Update workflow:
1. Edit `shared/pricing/pricing_v1.json`.
2. Run `make test`.
3. Update changelog with pricing update note.
