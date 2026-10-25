# FlexFactory — Project Overview

**Project:** FlexFactory  
**Challenge:** Seva Innovation Challenge  
**Theme:** Sustainable Sector — Industrial Decarbonisation and Pollution Control  
**Project type:** Software-based energy-aware production scheduling tool  
**Project status:** Prototype
**Last updated:** 25 October 2026

---

## 1. Project Vision

FlexFactory helps small manufacturers plan production around electricity prices and, where suitable data is available, electricity-related emissions.

The software compares a factory's original production schedule with an optimized schedule. It aims to reduce electricity costs and potentially emissions while respecting production deadlines, machine constraints, and other operational requirements.

**Core principle:** FlexFactory must make an actual scheduling decision. It must not be merely an energy-monitoring dashboard.

## 2. Problem Statement

Small manufacturers may run production according to fixed schedules without considering variations in electricity prices or emissions intensity over time.

Some production jobs can potentially be shifted to more favourable time slots. However, those shifts must not violate deadlines, machine availability, processing requirements, or other factory constraints.

FlexFactory will demonstrate how optimization can help make these decisions.

## 3. Intended Users

- Small and medium-sized manufacturers
- Factory production planners
- Energy managers
- Industrial sustainability teams

## 4. Planned Features

### Essential features — MVP

1. Input or load factory data.
2. Represent machines, production jobs, processing durations, power requirements, and deadlines.
3. Represent electricity prices across time slots.
4. Calculate the baseline schedule's energy consumption and electricity cost.
5. Generate an optimized production schedule.
6. Enforce machine and job constraints.
7. Check the feasibility of the optimized schedule.
8. Compare the baseline and optimized schedules using charts and numerical results.
9. Display the cost difference and percentage savings.

### Additional features — after MVP

- Emissions estimation using appropriate emissions-intensity data.
- CSV upload and downloadable results.
- Machine availability and maintenance windows.
- Different scheduling objectives.
- Scenario comparison and sensitivity analysis.

Optional features must not delay the working MVP.

## 5. Initial Technology Plan

- Language: Python
- Interface: Streamlit
- Optimization: Google OR-Tools, subject to suitability
- Data processing: Pandas
- Charts: Plotly
- Initial input: CSV and sample data
- Testing: Python tests and feasibility checks
- Version control: Git and GitHub

These are proposed choices, not yet implemented or verified.

## 6. Scheduling Model

The implemented model specifies:

- Job processing duration and power requirements
- Eligible machines for each job
- Machine capacity and non-overlap requirements
- Job release times, if applicable
- Production deadlines
- Electricity prices for each time slot
- Whether jobs can be interrupted or must run continuously
- Whether jobs may run simultaneously on different machines
- Any restrictions on shifting production

The first version should use a small, clearly documented example factory with three machines and five jobs.

## 7. Calculation Rules

Energy consumption must be calculated from power and operating duration, using consistent units.

Electricity cost must be calculated using the applicable time-slot prices.

The optimizer must produce a feasible schedule before its results are presented as valid.

Emissions savings must only be estimated when appropriate emissions-intensity data and a consistent calculation method are available.

All demonstration data must be clearly labelled as simulated. Do not present simulated results as real factory measurements.

## 8. Project Structure

FlexFactory/
- PROJECT_OVERVIEW.md
- TASK_LOG.md
- README.md
- src/
- tests/
- data/
- docs/

Expand this structure as implementation needs become clear.

## 9. Current Progress

Project concept and sustainability theme: Defined

Simulated dataset and baseline schedule: Created

Baseline calculator and feasibility checker: Implemented and tested

OR-Tools scheduling optimizer: Implemented and tested

Solar-aware grid-cost objective: Implemented and validated

Automated tests: 13 passing in the verified test run

Optimized schedule CSV export: Implemented

Streamlit dashboard: Implemented and launched successfully

Schedule comparison and cost-savings metrics: Implemented

Charts and CSV download: Implemented

README and final setup documentation: Complete

Automated tests after dashboard integration: Passed

Additional dashboard reliability checks: Pending


## 10. Constraints and Working Rules

- Prefer free and open-source tools.
- Avoid paid APIs unless explicitly approved.
- Keep the code and documentation in the project folder.
- Build incrementally and test each milestone.
- Do not replace working code without understanding the consequences.
- Never claim that untested functionality works.
- Keep secrets and credentials out of source control.
- Preserve enough project context for another AI to continue the work.

## 11. Instructions for Any AI

Before working:
1. Read this overview and the latest task log.
2. Inspect relevant existing files.
3. Confirm the current state without assuming previous AI-generated code is correct.
4. Work on one agreed task at a time.
5. Explain which files will be created or changed.
6. Provide exact commands for running and testing.
7. Report actual test results, failures, and unresolved issues.
8. Prepare updates to this overview and the task log after the work.

Do not restart the project from scratch unless explicitly requested.

## 12. Solar-Aware Scheduling

FlexFactory uses the hourly solar profile in `data/solar_availability.csv` as the canonical simulated source for solar availability. The optimizer and the shared energy-analysis helpers use the same solar data and the same hourly energy-balance rule:

- `load_kwh[h]` = production energy scheduled in hour h
- `solar_used_kwh[h]` = min(`load_kwh[h]`, `solar_available_kwh[h]`)
- `grid_energy_kwh[h]` = max(`load_kwh[h] - solar_used_kwh[h]`, 0)
- `grid_cost[h]` = `grid_energy_kwh[h] * electricity_price[h]`

The CP-SAT optimization objective is therefore to minimize total grid electricity cost after solar use, while the gross cost remains a separate reporting metric. Gross cost and grid cost are intentionally reported as different measurements.

Solar availability is illustrative sample data, not a live weather forecast. Actual energy savings and emissions reductions have not been measured.

### Current implementation status

- Canonical solar profile from `data/solar_availability.csv` is used consistently across planning, validation, and dashboard metrics.
- The optimizer minimizes grid electricity cost after solar offset, with integer-compatible scaling used for hourly energy values.
- The shared helper `calculate_schedule_energy_metrics()` calculates total energy, gross cost, solar used, grid energy, grid cost, and emissions using one aggregate hourly load across all active machines.
- The dashboard computes the schedule directly from the current form values, then uses `calculate_schedule_comparison_metrics()` for both baseline and optimized metrics. It does not read the optimized CSV as its displayed schedule.
- Automated tests cover baseline feasibility, solar-usage constraints, dashboard comparison consistency, and aggregate solar-use limits when machines run simultaneously.
- `data/optimized_schedule.csv` is generated by `python -m src.optimizer`; the schedule is validated before the file is written. Solver search is configured for repeatable output for the same inputs and OR-Tools version.

### Verified simulated comparison

Using the current sample schedules, tariff CSV, and canonical solar CSV, the baseline has gross cost ₹97.00, solar use 0.00 kWh, grid energy 23.00 kWh, and grid cost ₹97.00. The optimized schedule has gross cost ₹121.00, solar use 11.50 kWh, grid energy 11.50 kWh, and grid cost ₹42.00. These are simulated model results, not real-world savings.

The full test suite most recently passed with 13 tests (`python -m pytest -q`).

## 13. Immediate Next Actions

- Keep the verified solar-aware optimization model as the working baseline.
- Continue with any additional dashboard or presentation refinements only after the core scheduling logic remains stable.
- Evaluate appropriate real-world tariff and emissions data sources for future model expansion.