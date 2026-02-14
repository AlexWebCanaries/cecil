# Cache Savings Model Assumptions

Computation:
- `estimated = cost_estimate_usd * similarity * savings_factor` when `similarity >= savings_min_similarity`
- `low = estimated * 0.6`
- `high = estimated * 1.2`
- confidence scales with similarity and is capped to `[0,1]`

Configuration:
- `CECIL_SAVINGS_FACTOR` (default `0.3`)
- `CECIL_SAVINGS_MIN_SIMILARITY` (default `0.15`)

Safety:
- Unknown model cost yields zero savings and zero confidence.
- Parameters are clamped to safe bounds.
