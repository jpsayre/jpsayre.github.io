# Solar Lead-Gen Project — Handoff

**Last updated:** 2026-04-21
**Primary branch:** `main`
**Owner:** Jeff S

---

## 1. What This Is

A lead-generation platform that ranks residential properties by their likelihood of installing solar in the next 12 months. Currently live for **Boulder County, CO**; **San Diego, CA** is in progress (see `configs/san_diego_ca.py`, `docs/san_diego_modeling_insights.md`).

Inputs per county:
- Regrid parcel export (paid)
- Municipal permit records (format varies per municipality — biggest integration cost)
- Google Sunroof Building Insights API (roof geometry, azimuth, sunshine)
- Census ACS 5-year demographics (via FCC geocoder → block groups)
- EIA electricity prices, FRED 30-year mortgage rates (shared across counties)

Output: a ranked list of homes (with addresses, owner names, roof scores, and model-predicted adoption probability) used by installers for outreach.

---

## 2. Repo Layout

```
configs/                  Per-county Python config dicts (boulder_co.py, san_diego_ca.py)
src/                      Pipeline stage scripts + parse_permits_features.py (classification)
data_science/             Walk-forward ML, survival analysis, hyperparameter tuning, plots
scripts/                  Standalone ops: Supabase uploads, permit validators
tests/                    pytest suite (~69 tests — config, transforms, golden permits, contracts)
docs/                     new_county_setup.md, san_diego_modeling_insights.md, filtering_strategy_plan.md
data/
  raw/                    Input CSVs (Regrid exports, permits, MORTGAGE30US, electricity)
  {county_id}/working/    Intermediate pipeline files
  {county_id}/final/      Final output files (the ranked lists live here)
solar-web/                Next.js 14 customer-facing app, Supabase backend (Explorer, Following, Auth)
Website/                  Marketing / about site (secondary Next.js app)
run_pipeline.py           Master pipeline runner
local_app/                Legacy Flask tooling (manual verification). Not in core flow.
```

**Do not touch:** `*_OLD.py` files in `src/` are legacy from the image-classification era (satellite download → GPT-4o-mini classifier → Flask verification). That flow is abandoned in favor of permit-based labels.

---

## 3. Pipeline (11 Stages)

Run end-to-end:

```bash
python run_pipeline.py boulder_co
python run_pipeline.py boulder_co --limit 10 --skip-api     # smoke test
python run_pipeline.py boulder_co --start-from 7            # resume after permit edits
python run_pipeline.py boulder_co --step 10                 # re-train only
python run_pipeline.py boulder_co --dry-run                 # see stage list
```

| # | Stage | Script | Key output |
|---|---|---|---|
| 1 | validate | `run_pipeline.py` | Creates `data/{county}/{working,final}/` |
| 2 | interest_rates | `src/interest_rates.py` | `final/avg_yearly_interest.csv` |
| 3 | filter_regrid_api | `src/InitialScript.py` + `SunroofBatchAPI.py` | `final/regrid_filtered.csv`, `working/sunroof_api_output.csv` |
| 4 | filter_solar | `src/Analyze_ProjectSunroof_Data.py` | `working/filtered_api_output.csv` |
| 5 | merge_regrid_api | `src/Combine_Regrid_ProjectSunroof_Data.py` | `working/regrid_joined_with_api.csv` (LEFT join — keeps all Regrid homes) |
| 6 | roof_score | `src/roof_score.py` | `final/roof_score.csv` |
| 7 | parse_permits | `src/parse_permits.py` + `parse_permits_features.py` | `final/parsed_permits.csv` (19 binary flags + `permit_type`) |
| 8 | census_enrichment | `src/enrich_census.py` | `final/strap_census_lookup.csv`, `strap_block_group_geocoded.csv` |
| 9 | permits_by_year | `src/create_data_science_input.py` | `working/data_science_input.csv` (strap × year panel, 180+ features) |
| 10 | walk_forward_model | `data_science/walk_forward_modeling.py` | `data_science/output/{county}/walk_forward/*.csv` |
| 11 | upload_scores | `scripts/upload_scores_to_supabase.py` | Upserts roof + model scores to Supabase |

Stage 11 replaced the old `combine_regrid_model_rank.py` — that script still exists but produces a local CSV nothing downstream consumes.

**Target variable** (stage 9): `solar_next_year` ∈ {0, 1, 2}: 0 = no install next year, 1 = installs next year, 2 = already has solar (excluded from training).

**Walk-forward validation**: expanding window 2012 → 2025. Models: LASSO LogReg, Random Forest, Gradient Boosting, LightGBM, Neural Net, StackedEnsemble. Sample weighting: exponential decay `0.85^years_old`. Metrics: lift @ 2/5/10/20%, capture rate, ROC-AUC.

---

## 4. Permit Classification (Critical for Modeling)

All logic lives in `src/parse_permits_features.py` — single source of truth.

```
raw permit → compute_features() → 19 binary flags → classify_permit_type() → permit_type string
```

Three layers:
1. Category matching (`permit_category` keywords)
2. Description regex (19 feature regexes on category+description)
3. Valuation floors (solar < $3k without strong keywords → rejected)

Multi-type support: `solar,battery` expands to two rows on Supabase upload with conflict key `(home_index, permit_number, permit_type)`.

**Validation tooling:**
- `scripts/validate_permits.py` — statistical report, category coverage, baseline drift detection
- `scripts/validate_permits_ai.py` — GPT-4o-mini cross-check on stratified sample
- `tests/fixtures/golden_permits.csv` + `tests/test_golden_permits.py` — manually verified edge cases

Historical note: a rewrite of `upload_permits_to_supabase.py` moved solar permit counts from ~1,834 (binary-flag csv) to ~5,336 (raw text classification). `ENERGY EFFICIENT SYSTEM` no longer defaults to solar — only unambiguous keywords (solar, photovoltaic, pv, grid-tied) classify as such.

---

## 5. Web Apps

### `solar-web/` — Customer App
- Next.js 14 + Supabase. Pages: `/homes` (explorer with map), `/homes/[index]` (detail), `/following`, `/follows`, `/alerts`, `/login`, `/signup`, `/about`.
- Spec of record: `solar-web/SPEC.md` — check before every UI change.
- Tests: `cd solar-web && npm test` (vitest, 43 tests across `cardData`, `mapPoints`, `urlParams`, `imagePath`).
- **Known test debt:** `mapPoints.test.ts` and `urlParams.test.ts` reimplement logic inline instead of importing from source. If the real code in `app/homes/page.tsx` diverges, tests still pass but the app breaks. Fix = extract into `lib/mapPoints.ts` and `lib/urlParams.ts`. ~30 min, highest-value quick win.
- Coverage is ~15% of frontend logic. Zero tests on pages, HomeMap, ListingCard, ReportIssueModal, auth middleware, Supabase calls.
- Post-demo plan: `memory/post_demo_testing_plan.md` — Playwright E2E for the demo flow is the next priority.

### `Website/` — Marketing Site
- Next.js 14. Pages: `about`, `contact`, `faq`, `purchase`.
- Pricing page was removed from the deployed site (commit `b45dd73`) but the code is still in `Website/app/purchase/` and `Website/purchase.md`.

---

## 6. Environment Variables

Required for core pipeline:
- `GOOGLE_SUNROOF_API_KEY` (stage 3) — also seen as `GOOGLE_SOLAR_API_KEY` in older scripts
- `CENSUS_API_KEY` (stage 8, free, recommended to avoid rate limits)

Required for Supabase upload + web:
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Optional / feature-flagged:
- `OPEN_AI_API_KEY` (AI permit cross-check)
- `PDL_API_KEY` (email enrichment via People Data Labs — used for outreach demo)
- `GOOGLE_MAPS_API_KEY` (legacy, only for deprecated image pipeline)
- `EIA_DEVELOPER_API_KEY` (refreshing electricity prices)
- `DATABASE_SOLAR_INTEL_URL` (optional Postgres fallback for roof score)
- `ADMIN_SECRET` / `FLASK_ADMIN_SECRET` (legacy Flask tools)

Never log or print API keys.

---

## 7. Business Context

- **Customer demo** was the week of 2026-03-16 (memory indicates it happened; verify current status with Jeff).
- **Pricing** (per `Website/purchase.md`): $800 per expected sale. Tier 1 (top 5%) = 25 homes / $800. Tier 2 = 30 homes. Tier 3 = 40 homes. Packages are exclusive to the buyer for 90 days.
- **Installer pricing hypothesis** (from `remainingWork.md`): $50/seat/month SaaS. Team of 20 = $12k/year/county. Not yet validated.
- Positioning claim: "top 10% of homes by adoption likelihood" — see decile chart on the About page (commit `ae2fb48`).

---

## 8. Open Work & Known Issues

### Deferred (post-demo)
- **Filtering fix** (`docs/filtering_strategy_plan.md`): replace `saleprice >= 100k` filter with `totalactualval >= 200k OR saleprice >= 100k`. Recovers ~19,500 homes (28,861 → ~48,500) currently dropped because of `saleprice = 0` (quit claims, trust transfers, inherited — median assessed value $807k). Also adds `area_building` fallback when `mainfloorsf = 0`. Requires ~19.5k new Sunroof API calls (~$195). Zero homes lost.
- **Test extraction** in solar-web (see §5).
- **Playwright E2E** for the demo flow (`/homes` → filter → map click → detail → follow → /following → back).

### Pipeline TODOs noted in `remainingWork.md`
- Partial re-runs for Sunroof API calls
- Mobile: field click zooms unexpectedly; search doesn't override map dots; map zoom error
- Data backups plan
- Future CRM consideration: keep homes available after solar install but hide from other orgs

### County-specific hardcoding
- Many older scripts have "Boulder" in filenames and logic — the refactor to `run(config)` entry points and `data/{county_id}/` folders is done, but audit needed when onboarding a third county. See `docs/new_county_setup.md`.
- Regrid column names are consistent across counties (good). Permit formats vary by municipality (bad) — each city needs its own entry in `config.permit_sources` with column mappings.

---

## 9. How to Verify the Pipeline is Healthy

```bash
# unit tests
python -m pytest tests/ -v                        # pipeline (~69 tests)
cd solar-web && npm test                          # web (43 tests)

# smoke test pipeline without API calls or writes
python run_pipeline.py boulder_co --limit 10 --skip-api --dry-run

# permit classification drift
python scripts/validate_permits.py --config boulder_co
python scripts/validate_permits_ai.py --config boulder_co --sample-size 50
```

---

## 10. Starter Tasks for a New Contributor

1. Read `README.md`, then this doc, then `solar-web/SPEC.md`.
2. Run `python run_pipeline.py boulder_co --dry-run` — confirms config loads.
3. Run `python -m pytest tests/ -v` — confirms env is set up.
4. Walk through stage 7 (`parse_permits.py` + `parse_permits_features.py`) — highest-leverage file in the pipeline; most onboarding friction for new counties lives here.
5. Pull up `solar-web` locally (`cd solar-web && npm install && npm run dev`) and click through `/homes`. Confirm map + cards render against production Supabase.
6. Pick up one of: extract `lib/mapPoints.ts` / `lib/urlParams.ts` (quick win), or work through `docs/filtering_strategy_plan.md` (bigger win, needs pipeline re-run).
