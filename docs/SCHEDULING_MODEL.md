# FlexFactory Scheduling Model

## Status
Scheduling assumptions finalized. Simulated dataset created. Baseline calculator and feasibility checker implemented and tested with three passing tests. Optimization engine not yet implemented.

Implementation verification

The Python baseline calculator reports:

Total energy: 23 kWh

Baseline electricity cost: ₹97

Baseline schedule: Valid

The automated tests cover baseline validity, expected energy and cost totals, and machine-conflict detection.

## 1. Objective
Minimize total electricity cost by shifting production jobs to cheaper hourly slots while respecting job deadlines and machine constraints.

## 2. Planning horizon
- Horizon: hour 0 through hour 12.
- Time-slot length: 1 hour.
- Job start and end times: integer hours in the initial MVP.
- A job ending at hour 12 is within the planning horizon.
- All prices and job data are simulated.

## 3. Machines and job assignments
The example factory contains three machines:
- M1: Cutting
- M2: Drilling
- M3: Finishing

Each job is assigned to one fixed machine. Jobs cannot switch machines in the initial MVP.

## 4. Processing assumptions
- Jobs are non-preemptive: once started, a job runs continuously until it finishes.
- Each machine can process at most one job at a time.
- Different machines may operate simultaneously.
- Every job must be scheduled exactly once.
- Each job must start at or after its release time.
- Each job must finish at or before its deadline.
- Every job must finish within the planning horizon.

## 5. Initial job data

| Job | Machine | Duration (hours) | Power (kW) | Release | Deadline |
|---|---|---:|---:|---:|---:|
| J1 | M1 | 2 | 3.0 | 0 | 10 |
| J2 | M2 | 3 | 2.0 | 0 | 12 |
| J3 | M1 | 2 | 3.0 | 0 | 12 |
| J4 | M3 | 2 | 1.5 | 0 | 12 |
| J5 | M2 | 1 | 2.0 | 0 | 12 |

## 6. Electricity prices
The hourly prices are stored in `data/electricity_prices.csv`. They are illustrative simulated values, not real tariff data.

## 7. Energy and cost calculation
For a job whose power is constant during processing:

Energy (kWh) = Power (kW) × Duration (hours).

Electricity cost must account for the price of every hour in which the job runs. For each occupied hour, multiply the job's power by that hour's price per kWh, then sum the hourly costs.

Total energy for the initial dataset is 23 kWh when every job is scheduled once.

## 8. Baseline schedule
The baseline is stored in `data/baseline_schedule.csv`.

| Job | Start | End |
|---|---:|---:|
| J1 | 0 | 2 |
| J2 | 0 | 3 |
| J3 | 2 | 4 |
| J4 | 0 | 2 |
| J5 | 3 | 4 |

The baseline is feasible under the defined constraints. Its calculated electricity cost is ₹97.

## 9. Lower-cost reference schedule
A candidate lower-cost feasible schedule for later testing is:

| Job | Start | End |
|---|---:|---:|
| J1 | 0 | 2 |
| J2 | 0 | 3 |
| J3 | 2 | 4 |
| J4 | 10 | 12 |
| J5 | 11 | 12 |

Its calculated electricity cost is ₹89.50, a reduction of ₹7.50 (approximately 7.73%) compared with the baseline. This is a reference schedule, not yet a result produced or verified by the optimization engine. The solver may find an equal or better schedule.

## 10. Validation requirements
The implementation must check:
1. Every input job is scheduled exactly once.
2. Start and end times match the required processing duration.
3. The selected machine matches each job's fixed assignment.
4. No two jobs overlap on the same machine.
5. Release times and deadlines are respected.
6. All jobs fit within the planning horizon.
7. Energy and electricity costs are calculated consistently.
8. Reported savings are calculated against the baseline using the same input data.

## 11. Scope limitations
- The initial model uses simulated data.
- Machine power is represented by each job's power requirement.
- Startup energy, standby consumption, maintenance, setup times, and real-world production dependencies are excluded.
- Emissions are not optimized in the first implementation. Any future emissions estimate requires a suitable emissions-intensity dataset and a documented calculation method.

## 12. Next task
Implement a constraint-based optimizer that minimizes electricity cost while respecting fixed machine assignments, job durations, release times, deadlines, the planning horizon, and machine non-overlap constraints. Validate its output using the existing feasibility checker.
