# FlexFactory Scheduling Model

## Status
Scheduling assumptions are finalized. The baseline calculator, feasibility checker, and solar-aware CP-SAT optimizer are implemented and tested. The optimizer writes a validated schedule to `data/optimized_schedule.csv` when run with `python -m src.optimizer`.

The current dashboard and optimizer use the shared scheduling and energy-analysis helpers. The full test suite covers baseline validity, optimizer validity, export behavior, dashboard comparison metrics, and solar accounting.

## 1. Objective
Minimize grid electricity cost after hourly solar use, while respecting job deadlines and machine constraints. Gross electricity cost is reported separately and is not the solar-aware solver objective.

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

## 9. Historical gross-cost reference schedule
A historically documented feasible schedule has gross electricity cost ₹89.50:

| Job | Start | End |
|---|---:|---:|
| J1 | 0 | 2 |
| J2 | 0 | 3 |
| J3 | 2 | 4 |
| J4 | 10 | 12 |
| J5 | 11 | 12 |

This is a gross-cost reference only. It is not the current solar-aware optimizer result and should not be interpreted as a grid-cost comparison.

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

## 12. Solar-aware objective and validation
The optimizer now minimizes grid electricity cost after subtracting usable solar energy.

For each hour h:
- `load_kwh[h]` = scheduled production energy in that hour
- `solar_used_kwh[h]` = min(load_kwh[h], solar_available_kwh[h])
- `grid_energy_kwh[h]` = max(load_kwh[h] - solar_used_kwh[h], 0)
- `grid_cost[h]` = `grid_energy_kwh[h] * electricity_price[h]`

The optimization objective is therefore:

`sum(grid_energy_kwh[h] * electricity_price[h])`

with integer-compatible scaling for the CP-SAT model. Gross electricity cost is still tracked separately as a reporting metric, but it is not the solver objective for the solar-aware version.

The solar usage variables are bounded by both the available solar energy in that hour and the total production load in that same hour. This avoids double counting and keeps the energy balance physically consistent.

## 13. Verified implementation status
The current implementation uses `data/solar_availability.csv` and `data/electricity_prices.csv` as canonical simulated inputs. For each hour, solar used is bounded by both available solar and scheduled load; grid energy is the remaining load. The schedule is checked for job coverage, duration, release times, deadlines, planning horizon, and machine conflicts before export.

The current simulated comparison, using the earliest-start baseline and a fresh optimizer result, is:

| Metric | Baseline | Optimized |
|---|---:|---:|
| Gross electricity cost | ₹97.00 | ₹121.00 |
| Solar energy used | 0.00 kWh | 11.50 kWh |
| Grid energy consumed | 23.00 kWh | 11.50 kWh |
| Grid electricity cost | ₹97.00 | ₹42.00 |

The dashboard calculates both schedules from the currently submitted job and tariff inputs and uses the canonical solar profile for both. Solar availability is applied once per hour to the aggregate load across all simultaneously running jobs, so it cannot be counted once per machine. The displayed optimized schedule is the result returned by the current optimizer run, not a schedule loaded from `data/optimized_schedule.csv`.

These values come from the provided simulated schedules and inputs. They are not measured real-world savings. The full automated suite passed: `python -m pytest -q` — 13 passed in 3.09s.
