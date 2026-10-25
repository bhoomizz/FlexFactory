# FlexFactory — Task Log

## Session 001 — Project Definition

**Date:** 24 October 2026  
**AI assistant:** ChatGPT  
**Milestone:** Initial project definition  
**Status:** In progress

### Objective

Establish the project concept, initial scope, documentation system, and development workflow.

### Completed

- Defined FlexFactory as an energy-aware production scheduling tool.
- Identified industrial decarbonisation and pollution control as the intended sustainability theme.
- Defined the core comparison between baseline and optimized schedules.
- Identified initial technology candidates: Python, Streamlit, OR-Tools, Pandas, and Plotly.
- Established the requirement to maintain a project overview and chronological task log.

### Files created

- PROJECT_OVERVIEW.md — initial project definition.
- TASK_LOG.md — initial session record.

### Implementation completed

No application code has been implemented yet.

### Testing

Not applicable. No application code exists yet.

### Decisions still required

- Exact scheduling objective and constraints.
- Job and machine data structure.
- Treatment of job interruptions and simultaneous machine operation.
- Baseline scheduling method.
- Electricity-price time-slot resolution.
- Appropriate method for emissions estimation.

### Next task

Define the mathematical scheduling model and design a small simulated factory dataset with three machines and five jobs.

### Handoff instructions

The next AI must read PROJECT_OVERVIEW.md and this task log before continuing. It should define the model and assumptions before generating application code. Preserve the current scope and update both documents when the next milestone is completed.

---

## Session Template — Duplicate for Future Sessions

**Date:**  
**AI assistant/tool:**  
**Milestone:**  
**Status:** In progress / Completed / Blocked

### Objective
[What are we trying to achieve?]

### Work completed
- 

### Files created
- 

### Files modified
- 

### Tests performed
- 

### Actual test results
- 

### Errors and fixes
- 

### Decisions made
- 

### Remaining issues
- 

### Next task
- 

### Overview updated?
- Yes / No

### Handoff ready?
- Yes / No

## Session 002 — 24 October 2026

### Task
Finalize the initial scheduling assumptions and design the simulated factory dataset.

### Decisions made
- Fixed machine assignment for each job in the first MVP.
- Three machines and five jobs.
- Twelve-hour planning horizon with one-hour time slots.
- Non-preemptive jobs.
- One job per machine at a time.
- Hard release-time and deadline constraints.
- Minimize electricity cost as the initial optimization objective.
- All initial data and electricity prices are simulated.

### Files created or updated
- `data/machines.csv` — simulated machine list.
- `data/jobs.csv` — job durations, power, assignments, release times, and deadlines.
- `data/electricity_prices.csv` — simulated hourly electricity prices.
- `data/baseline_schedule.csv` — original feasible schedule.
- `docs/SCHEDULING_MODEL.md` — finalized initial assumptions, formulas, constraints, and reference schedules.
- `PROJECT_OVERVIEW.md` — updated progress and next actions.

### Manual verification
- Total scheduled job energy: 23 kWh.
- Baseline electricity cost: ₹97.
- Candidate lower-cost schedule: ₹89.50.
- Candidate cost reduction: ₹7.50, approximately 7.73%.

These are manual calculations using simulated data. No Python implementation, automated test, or optimization solver has been run yet.

### Remaining work
- Create the baseline cost calculator.
- Implement and test schedule-feasibility checks.
- Validate the manual calculations programmatically.
- Implement the optimizer.
- Build the user interface after the core logic is tested.

### Next task
Implement a Python baseline-cost calculator and feasibility checker, then test them against the CSV files.

### Handover instructions
Before continuing, read `PROJECT_OVERVIEW.md`, this task log, and `docs/SCHEDULING_MODEL.md`. Inspect the actual CSV files and verify their contents. Do not assume the Python implementation exists until it has been created and tested.
## Session 003 — 24 October 2026

### Task
Implement and test the baseline electricity-cost calculator and schedule feasibility checker.

### Files created
- `src/baseline.py` — loads the CSV data, validates the schedule, and calculates energy and cost.
- `tests/test_baseline.py` — automated tests for baseline validity, expected totals, and machine-conflict detection.

### Verification results
- Baseline schedule validation: Passed.
- Total energy: 23 kWh.
- Baseline electricity cost: ₹97.
- Machine-conflict detection test: Passed.
- Total automated tests: 3 passed.

### Important limitation
The calculator and feasibility checker do not optimize schedules. The optimization engine and user interface remain unimplemented.

### Next task
Implement the constraint-based scheduling optimizer. Preserve the current calculator and tests, and verify the optimized schedule using the existing feasibility checker.

### Handover instructions
Read `PROJECT_OVERVIEW.md`, `docs/SCHEDULING_MODEL.md`, and this task log before continuing. Inspect existing code before modifying it. Do not claim the optimizer works until its output passes the feasibility checks and automated tests.
## Session 004 — 24 October 2026

### Task
Implement the constraint-based scheduling optimizer.

### File created
- `src/optimizer.py` — schedules jobs with OR-Tools CP-SAT, enforces machine non-overlap, validates the result, calculates savings, and exports `data/optimized_schedule.csv`.

### Verification
- Optimizer executed successfully.
- Solver returned a feasible or optimal schedule.
- Optimized schedule passed the existing feasibility checker.
- Baseline cost comparison and CSV export worked.
- User reported no errors.

### Limitations
- Results use simulated data and the current simplified scheduling model.
- Optimization-specific automated tests have not yet been added.
- No real-world factory or emissions data has been validated.

### Next task
Add automated tests for the optimizer and its cost-saving result before starting the Streamlit interface.
## Session 005 — 24 October 2026

### Task
Add automated tests for the optimization engine.

### Verification
- Solver solution test: Passed.
- Optimized schedule feasibility test: Passed.
- Optimized cost comparison test: Passed.
- Full test suite: 6 tests passed.

### Next task
Build a Streamlit interface for entering and viewing production schedules, comparing baseline and optimized electricity costs, and displaying savings. Preserve the tested calculation and optimization modules.
## Session 006 — 24 October 2026

### Task
Create the first Streamlit dashboard for FlexFactory.

### File created
- `requirements.txt` — project dependencies.
- `app.py` — dashboard displaying baseline and optimized schedules, energy and cost metrics, charts, and CSV download.

### Verification
- Dependencies installed successfully.
- Dashboard launched successfully in the browser.
- User reported that the dashboard was working correctly.

### Remaining work
- Re-run the full automated test suite after dashboard integration.
- Add reliability checks.
- Write README instructions.
- Prepare the competition demonstration and presentation.

### Next task
Re-run all six tests and confirm the existing core functionality remains intact before adding features.

---

## Session 007 — 25 October 2026

### Task
Resolve the optimizer regression and align the model to the canonical hourly solar profile.

### Work completed
- Verified the active terminal was inside a Python REPL during the earlier failure and restored the normal PowerShell prompt.
- Confirmed the repo uses `data/solar_availability.csv` as the canonical hourly solar source.
- Confirmed the optimizer objective minimizes grid electricity cost after solar use, while gross cost remains a separate metric.
- Replaced the outdated gross-cost assertion with tests for grid-cost improvement and hourly solar constraints.
- Updated project docs to document the actual solar-aware model, assumptions, and verified test status.

### Files modified
- `src/baseline.py` — shared helper for hourly solar-aware energy and grid metrics.
- `src/optimizer.py` — objective and variables aligned to grid-cost minimization after solar offset.
- `tests/test_optimizer.py` — meaningful grid-cost and solar-constraint checks.
- `PROJECT_OVERVIEW.md` — documented the solar-aware scheduling model and current implementation status.
- `TASK_LOG.md` — recorded the model correction and verification work.
- `docs/SCHEDULING_MODEL.md` — updated the scheduling assumptions to reflect the solar-aware objective.

### Tests performed
- `powershell -NoLogo -NoProfile -Command "Get-Location; python --version; python -m pytest -q"`

### Actual test results
- 9 passed in 2.86s.

### Decisions made
- Gross electricity cost and grid electricity cost are different metrics and are reported separately.
- Solar availability is constrained by both hourly solar availability and the total production load in each hour.
- The baseline and optimized schedules use the same solar CSV and the same energy-balance logic.

### Remaining issues
- None at the current verified state.

### Next task
- Prepare final handoff and keep the verified solar-aware model as the baseline for future work.

### Overview updated?
- Yes

### Handoff ready?
- Yes

---

## Session 009 — 25 October 2026

### Task
Align the Streamlit dashboard with the canonical solar-aware scheduling model.

### Work completed
- Confirmed the dashboard generates its optimized schedule by calling the current optimizer with submitted form values; it does not read `data/optimized_schedule.csv` for display.
- Added shared baseline/optimized comparison metrics for gross cost, grid cost, grid energy, solar energy, and grid-cost reduction.
- Updated the dashboard to show those metrics together and label its data and cost reduction as simulated.
- Kept the canonical solar profile and submitted tariff rows flowing into both optimizer and shared metric calculations.
- Added coverage showing solar is applied once against aggregate load when multiple machines run simultaneously.
- Added metric consistency tests and updated project documentation.

### Files changed
- `app.py`
- `src/baseline.py`
- `tests/test_baseline.py`
- `tests/test_optimizer.py`
- `README.md`
- `PROJECT_OVERVIEW.md`
- `docs/SCHEDULING_MODEL.md`
- `TASK_LOG.md`

### Tests performed
- Focused tests: `python -m pytest tests/test_baseline.py tests/test_optimizer.py -q`
- Full suite: `python -m pytest -q`

### Actual test results
- Focused tests: 12 passed in 4.80s.
- Full suite: 13 passed in 3.09s.

### Decisions made
- The dashboard compares the automatically generated earliest-start baseline with the fresh optimized schedule using grid electricity cost for the reduction metric.
- Gross cost is shown separately because it can rise even when grid cost falls due to solar use.
- The shared hourly energy helper aggregates all jobs before applying each hour's available solar once.

### Remaining issues
- None identified in the requested dashboard calculations; all supplied factory, solar, and tariff inputs remain simulated.

### Handoff ready?
- Yes

---

## Session 008 — 25 October 2026

### Task
Make the optimized schedule CSV reproducible and prevent invalid exports.

### Work completed
- Confirmed `data/optimized_schedule.csv` is an optimizer-generated output documented by the README, not a manually maintained example.
- Routed optimizer solar loading through the shared canonical solar-profile loader.
- Configured the CP-SAT solver to use one worker and a fixed random seed for repeatable output with the same inputs and solver version.
- Added validation inside `save_schedule()` before the output file is opened, so an invalid schedule cannot replace the existing export.
- Added tests that compare the regenerated CSV with a fresh optimizer result and confirm invalid schedules do not overwrite an existing file.
- Regenerated `data/optimized_schedule.csv` using `python -m src.optimizer`.
- Updated README and model/project documentation with the verified simulated comparison and caveat that it is not real-world savings.

### Files changed
- `src/optimizer.py`
- `tests/test_optimizer.py`
- `data/optimized_schedule.csv`
- `README.md`
- `PROJECT_OVERVIEW.md`
- `docs/SCHEDULING_MODEL.md`
- `TASK_LOG.md`

### Verified simulated metrics
## Session 007 — 24 October 2026

### Task
Verify the core implementation after dashboard integration and document the project.

### Verification
- User confirmed the full automated test suite ran successfully.
- Baseline calculator and optimizer tests passed.
- Streamlit dashboard had previously launched successfully.

### Documentation
- Created README.md with project overview, setup, run commands, tests, scheduling assumptions, and limitations.
- Clearly documented that the current dataset is simulated and that real-world savings and emissions reductions have not been verified.

### Next task
Review dashboard reliability and prepare the competition demonstration.

---

## Session 008 — 24 October 2026

### Task
Improve dashboard error handling.

### Changes
- Added clearer messages for scheduling and validation errors.
- Preserved existing dashboard features and optimizer logic.

### Verification
- Pending user verification of automated tests and dashboard launch at that time.

---

## Session 009 — 24 October 2026

### Task
Add a reliability test for missing input files.

### Changes
- Added `tests/test_data_loading.py`.
- Verified missing CSV files raise `FileNotFoundError`.
- Existing application and optimizer code were left unchanged for this task.

### Verification
- Test execution was pending when this entry was recorded.

---

## Historical Update — Date Not Recorded: Sustainability Dashboard

- Added estimated CO₂ emissions and an emissions comparison chart.
- Added a user-adjustable illustrative emissions factor.
- Fixed job-duration validation and removed duplicate tariff validation.
- No verification result was recorded with this note.

## Historical Update — Date Not Recorded: Solar-Aware Scheduling

- Added the simulated hourly solar profile in `data/solar_availability.csv`.
- Updated optimizer, application, and baseline calculations to account for solar availability.
- The suite was reported as passing with 8 tests at that point in the project history.
- Solar values are simulated; actual savings and emissions reductions have not been measured.

---

## Session 010 — 25 October 2026

### Task
Resolve the optimizer regression and align the model to the canonical hourly solar profile.

### Work completed
- Confirmed `data/solar_availability.csv` is the canonical hourly solar source.
- Aligned the optimizer objective with grid electricity cost after solar use.
- Replaced the outdated gross-cost assertion with grid-cost and hourly solar-bound checks.
- Updated the model and project documentation.

### Verified result
- Full suite: 9 passed in 2.86s.
- Gross electricity cost and grid electricity cost are reported separately.
- Solar use is limited by hourly availability and aggregate production load.

---

## Session 011 — 25 October 2026

### Task
Make optimized schedule export reproducible and validation-gated.

### Work completed
- Confirmed `data/optimized_schedule.csv` is generated output, not a manually maintained example.
- Reused the canonical solar-profile loader and configured a single-worker seeded solver.
- Added validation before writing the export and tests for fresh-export parity and invalid-write protection.
- Regenerated the CSV and documented the simulated comparison.

### Verified simulated metrics
- Baseline: gross cost ₹97.00, solar used 0.00 kWh, grid energy 23.00 kWh, grid cost ₹97.00.
- Optimized: gross cost ₹121.00, solar used 11.50 kWh, grid energy 11.50 kWh, grid cost ₹42.00.
- Solver status: OPTIMAL; exported schedule validation passed.
- These are simulated results, not real-world savings.

### Tests
- Full suite: 11 passed in 1.62s.

---

## Session 012 — 25 October 2026

### Task
Align dashboard metrics with the canonical solar-aware scheduling model.

### Work completed
- Confirmed the displayed optimized schedule comes from the current solver run, not a stale export CSV.
- Added shared baseline/optimized gross-cost, grid-cost, grid-energy, solar-use, and grid-cost-reduction metrics.
- Labeled costs and reductions as simulated and added metric-consistency and simultaneous-machine solar tests.
- Updated README and model/project documentation.

### Verified results
- Full suite: 13 passed in 3.28s.
- Grid-cost reduction is baseline grid cost minus optimized grid cost; gross cost remains separate.
- Hourly solar is applied once to aggregate load across active jobs.

---

## Session 013 — 25 October 2026

### Task
Pre-commit history and schedule-section cleanup.

### Changes
- Removed the duplicated solar-regression task-log entry and ordered recorded milestones chronologically with unique session numbers.
- Corrected duplicate production-schedule section numbering in `app.py` without changing dashboard behavior.

### Verification
- `python -m pytest -q`: 13 passed in 4.16s.
- `git diff --check`: passed.