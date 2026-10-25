# FlexFactory — Project Overview

**Project:** FlexFactory  
**Challenge:** Seva Innovation Challenge  
**Theme:** Sustainable Sector — Industrial Decarbonisation and Pollution Control  
**Project type:** Software-based energy-aware production scheduling tool  
**Project status:** Planning  
**Last updated:** 24 October 2026

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

## 6. Scheduling Model — To Be Defined

The model must specify:

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
## Project concept and sustainability theme: Defined

Simulated dataset and baseline schedule: Created

Baseline calculator and feasibility checker: Implemented and tested

OR-Tools scheduling optimizer: Implemented and tested

Automated tests: 6 passing in the last reported test run

Optimized schedule CSV export: Implemented

Streamlit dashboard: Implemented and launched successfully

Schedule comparison and cost-savings metrics: Implemented

Charts and CSV download: Implemented
- README and final setup documentation: Complete
- Automated tests after dashboard integration: Passed
- Additional dashboard reliability checks: Pending


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

## 12. Immediate Next Actions

Re-run the complete test suite after dashboard integration.

Add basic input-data and dashboard reliability checks.

Write README setup and demonstration instructions.

Improve the dashboard presentation and explain the optimization results.

Prepare the competition PPT and project demonstration.

Evaluate appropriate real-world tariff and emissions data sources.
