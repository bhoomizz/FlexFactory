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

### Handover instructions
Read `PROJECT_OVERVIEW.md`, `TASK_LOG.md`, and `docs/SCHEDULING_MODEL.md`. Inspect the existing implementation before making changes. Preserve working code and update the documentation after each completed task.
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
## Session 008 — 24 October 2026

### Task
Improve dashboard error handling.

### Changes
- Added a clearer message for scheduling and validation errors.
- Unexpected exceptions are directed to the terminal for technical details.
- Preserved existing dashboard features and optimizer logic.

### Verification
- Pending user verification of automated tests and dashboard launch.
## Session 009 — 24 October 2026

### Task
Add a reliability test for missing input files.

### Changes
- Added tests/test_data_loading.py.
- Verified that missing CSV files raise FileNotFoundError.
- Existing application and optimizer code left unchanged.

### Verification
- Pending test execution.
## Sustainability Dashboard Update
- Added estimated CO₂ emissions and an emissions comparison chart.
- Added a user-adjustable illustrative emissions factor.
- Fixed job-duration validation and removed duplicate tariff validation.
- Next: test locally, update documentation, and redeploy.
## Solar-Aware Scheduling
- Added an illustrative hourly solar availability profile in `data/solar_availability.csv`.
- Updated the optimizer to account for available solar energy when estimating grid electricity usage and scheduling production.
- Updated the application and baseline logic for the solar feature.
- Verified the test suite: **8 tests passed**.
- Solar values are simulated; actual savings and emissions reductions have not been measured.