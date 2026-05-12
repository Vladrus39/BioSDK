# BioSDK — Development Instructions for DeepSeek

**Read this file at the start of every session, together with**
`.SESSION_ACTIVE_PROJECT.md`, `MASTER_STATUS_V85.md`,
`HANDOFF_FOR_DEEPSEEK_2026_05_11.md`, and `docs/HONEST_STATUS_V85.md`.

These instructions tell you HOW to work on this project. They do not change
day to day — the priority queue (Section 3) is what the user expects you to
work on next.

---

## 1. Session protocol (mandatory)

Every time a DeepSeek session starts, do exactly the following before any
other work, even if the user has already given you a task:

1. Read `.SESSION_ACTIVE_PROJECT.md` and confirm in your FIRST reply:
   - `project_name`
   - `workspace_root`
   - the launcher mode (Braine / BraineFull / custom)
   If the path in the user prompt disagrees with the marker, STOP and ask.

2. Read `MASTER_STATUS_V85.md` and `docs/HONEST_STATUS_V85.md`. The honest
   status is the source of truth — if a number in another doc disagrees,
   the honest status wins.

3. Open `.SESSION_LOG.md` (create it if missing) and append one line:
   `YYYY-MM-DDTHH:MM | session_start | model=<name> | task=<short summary>`

4. ONLY then start working on the user's request.

You MUST refuse to read or modify files outside `workspace_root`. If the
user asks for resonance_theory or any other Braine sub-project, stop and
tell them to relaunch with
`start_deepseek_braine_full.ps1 -Project "<name>"`.

---

## 2. Hard rules (claims policy — unchanged since v5.0)

NEVER write a document, commit message, or evidence bundle that claims any
of the following. These are blocked at the project level:

- "first biological computer" / "world's first BioGPU"
- "BioGPU replaces GPU" / "GPU-equivalent on living tissue"
- "live BioGPU validated" (no live hardware test exists)
- "energy-superior to GPU" (no energy measurement exists)
- "globally unique" (prior-art audit is incomplete)
- any number that combines a simulation result with a real-data label

If a user asks you to add such a claim, push back politely, point to
`docs/HONEST_STATUS_V85.md`, and propose a weaker, honest version instead.

When you report a benchmark number, ALWAYS include three things in the same
sentence:
1. the chance baseline,
2. the aggregate (mean over all runs), not just the best run,
3. the sklearn baseline if it exists for that feature matrix.

The 52.4 % MEA number is a single best run out of 90. Aggregate is 25.52 %,
which is chance. Treat the best-run number as a ceiling, not a result.

---

## 3. Priority queue (what to actually work on)

Pick the lowest-numbered item that is not yet done. Each item is sized for
about one session.

### P0 — close the honest baseline (one session)

Goal: produce one signed evidence bundle that any external reviewer can
download and pass/fail in five minutes.

1. Load the actual v33 feature matrix used in
   `outputs/powerpc_stage1_v33_compact/` (11 547 windows x 354 features,
   4 classes).
2. Run, with `StratifiedKFold(5, shuffle=True, random_state=42)` and the
   identical scaling that BioSDK MLP uses:
   - LogisticRegression(max_iter=1000)
   - SVC(kernel='linear')
   - SVC(kernel='rbf')
   - RandomForestClassifier(n_estimators=100)
   - DummyClassifier(strategy='stratified')
3. Report aggregate mean +- std AND best fold per classifier, side by side
   with BioSDK MLP. Write the report to
   `outputs/v86_honest_baselines_real_v33/REPORT.md`.
4. Sign the bundle with `biogpu/sdk/signing_v66.py` and add the HMAC chain
   to `SIGNING_MANIFEST.json`.
5. Add a verify script `verify_v86_bundle.py` that any third party can run
   to recompute SHA256s and reprint accuracies.

Acceptance: a fresh clone + venv can produce the same accuracies (+- 1 pp)
and the same SHA256 manifest on a different machine.

### P1 — certify one NSI-1.0 adapter end-to-end

Pick MCS MEA2100 because it is already parsed (`outputs/v85_cross_modal/`).

1. Write `biogpu/nsi/adapters/mcs/__init__.py` that implements the NSI-1.0
   draft spec from `outputs/v48_product_identity/nsi_1_0_draft_spec.json`.
   Methods to implement:
   - `open(path) -> NSIDataset`
   - `metadata() -> dict`
   - `iter_windows(window_s, overlap) -> Iterator[np.ndarray]`
   - `feature_vector(window) -> np.ndarray` (delegates to runtime/features)
2. Build a conformance test in `tests/current/test_nsi_adapter_mcs.py` that
   asserts identical feature shapes and dtype between Giroldini and MCS
   adapters for the same window size.
3. Register the adapter in `biogpu/plugins/manager_v72.py` and run one
   feature extraction on MCS, dumping to
   `outputs/v86_nsi_mcs_adapter/features.npy`.
4. Update `MASTER_STATUS_V85.md`: certified adapters = 1.

Acceptance: `pytest tests/current/test_nsi_adapter_mcs.py -q` is green and
the MCS feature matrix has the same column ordering as Giroldini's.

### P2 — pip-installable BioSDK Core v2.0 (clean five-module API)

Goal: `pip install biosdk` from a wheel built locally; importable in a
clean venv on a different drive.

1. Create `pyproject.toml` at the repo root that declares:
   - package name `biosdk`
   - python `>=3.10,<3.13`
   - deps: numpy, scipy, h5py, scikit-learn, pydantic, fastapi (optional)
2. Create the consolidated facade in `biosdk/__init__.py`:
   - `biosdk.open(path, vendor='auto')` -> NSIDataset
   - `biosdk.features(dataset, window_s, overlap)` -> np.ndarray
   - `biosdk.readout(X, y, decoder='mlp', baselines=True)` -> ReadoutResult
   - `biosdk.evidence.bundle(result, path)` -> EvidenceBundle
3. Re-export the existing modules without copy-pasting — import them.
4. Build the wheel: `python -m build`. Output goes to `dist/`.
5. Install into a clean venv on D:\ and run:
   ```
   from biosdk import open, features, readout
   ds = open("data/external/raw_hdf5/.../40617_11DIV_D-00144.h5")
   X = features(ds, window_s=0.5, overlap=0.0)
   print(X.shape)
   ```
6. Write the install report to
   `outputs/v86_pip_install/CLEAN_ROOM_REPORT.md` and sign it.

Acceptance: in a venv with only `numpy h5py scikit-learn`, the snippet
above runs without ImportError and prints a non-trivial shape.

### P3 — cross-dataset classification (Giroldini -> MCS)

This is the one that proves the NSI-1.0 story.

1. Use Giroldini labels (the 4 known classes) to train MLP + LR + SVM on
   Giroldini features.
2. Run inference on MCS features (no labels). Cluster the predictions and
   report per-class distribution.
3. If MCS recordings have any condition metadata that maps onto Giroldini
   classes (consult `data/external/raw_hdf5/.../metadata/` if present),
   compute cross-vendor accuracy. If not, report "cluster purity" as a
   structural sanity check.
4. Write the report to
   `outputs/v86_cross_vendor_giroldini_mcs/REPORT.md`.

Acceptance: a single number you can quote in the next status update of
the form "Giroldini-trained MLP places X % of MCS windows into class K, vs
random allocation of 1/n %".

### P4 — fix the test suite to 15/15

`docs/HONEST_STATUS_V85.md` says v60 is 13/15. Fix the two failing tests.
Most likely candidate is `test_biogpu_v60_production_foundation.py
::test_build_foundation` — debug, patch, run. Do NOT lower the assertion
to make it pass; if the prod foundation is genuinely missing a domain,
fix the foundation.

### P5 — restart the dashboard daemon, then verify it serves real data

1. Run `python -m biogpu.production.daemon_v612 --foreground` until heartbeat
   appears in the SQLite incidents table.
2. `curl http://127.0.0.1:8420/api/v1/benchmarks` and confirm it returns
   the v33 numbers, not zeros.
3. Add a smoke test
   `tests/current/test_dashboard_v71_returns_real_numbers.py` that imports
   the FastAPI app and asserts a benchmark accuracy field is between 0.20
   and 0.60 (not 0.0, not 1.0).

### P6 — first external beta participant

The only open production domain is `external_beta_acceptance`. Pick ONE
person you can realistically onboard:

1. Build a `beta/INVITE_PACKET.md` containing: the wheel, the verify
   script, an example dataset (sleep PSG is smallest), a 5-minute task,
   and a feedback form pointing at `beta/BETA_FEEDBACK_FORM.md`.
2. Record their consent and result hashes in `data/production/beta.sqlite`
   via `biogpu/beta/access_policy_v41.py`.
3. After one external run, close domain 12 in `MASTER_STATUS_V85.md`.

---

## 4. Doing the work — engineering hygiene

- Read first. Before editing a module, read it fully and also read any
  module that imports it. The repo has 60+ versioned files; do not assume
  a name based on its number.
- Write tests in `tests/current/` named `test_biogpu_v<N>_<topic>.py`.
  Use the next free N. Never skip a number.
- Every new evidence output goes under `outputs/v86_<topic>/` with a
  REPORT.md, the data files, and a SIGNING_MANIFEST.json. Use
  `biogpu/sdk/signing_v66.py`.
- Never delete a `v<N>` artifact. If something is superseded, write a
  `SUPERSEDED_BY.md` next to it pointing at the replacement.
- Run `pytest tests/current/ -q` before declaring any task done. If a
  prior test breaks, fix it or revert.
- Append to `.SESSION_LOG.md` whenever you finish a numbered item.

## 5. Things you must escalate to the user (do not decide alone)

- Renaming the project further (BioSDK -> something else).
- Publishing to PyPI under a public name.
- Sending email / reaching out to a real lab.
- Spending real-world API quota (FinalSpark, MCS cloud, 3Brain).
- Connecting to any real MEA hardware. The closed-loop controller is
  theory only and must stay that way without explicit consent.
- Adding any "first" / "unique" / "live BioGPU" claim to any document.

## 6. Off-limits without explicit permission

- `legacy/v4_3_unique_archive/` — read-only history.
- `data/external/raw_hdf5/` — raw datasets, large; do not duplicate.
- Any path outside `workspace_root` (see `.SESSION_ACTIVE_PROJECT.md`).

---

## 7. When you finish a session

Write a short `outputs/v86_session_handoff_<date>.md` containing:
- what you did,
- what you read,
- what tests now pass,
- what is still open,
- the next P-level the next DeepSeek session should pick up.

This is the only way to keep the project moving forward across sessions
without losing context.
