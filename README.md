# FlexFactory ⚡
### Energy-Aware Production Scheduling for Small Manufacturers

FlexFactory is a prototype that optimizes production job schedules to reduce electricity costs while respecting machine availability, job durations, and deadlines.

It uses **Google OR-Tools CP-SAT** to find a feasible, lower-cost production schedule and provides a Streamlit dashboard to compare the baseline schedule with the optimized result.

> **Important:** This prototype uses simulated factory data and electricity prices. Its results are illustrative and are not measured real-world savings.

## Features

- Baseline production schedule and electricity-cost calculation
- Production scheduling using Google OR-Tools
- Machine-conflict and deadline validation
- Electricity-cost and energy-consumption comparison
- Interactive Streamlit dashboard with charts
- Downloadable optimized schedule in CSV format
- Automated tests for the baseline calculator and optimizer

## Technology Stack

- Python
- Streamlit
- Google OR-Tools CP-SAT
- Pandas
- Plotly
- SQLite: Not currently used

## Project Structure

```text
FlexFactory/
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_OVERVIEW.md
├── TASK_LOG.md
├── src/
│   ├── baseline.py
│   └── optimizer.py
├── tests/
│   ├── test_baseline.py
│   └── test_optimizer.py
├── data/
│   ├── machines.csv
│   ├── jobs.csv
│   ├── electricity_prices.csv
│   ├── baseline_schedule.csv
│   └── optimized_schedule.csv
└── docs/
    └── SCHEDULING_MODEL.md
```

## Installation

**Requirements:** Python and pip installed on your computer.

1. Open a terminal in the project root folder.
2. Install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

## Run the Dashboard

From the project root, run:

```bash
streamlit run app.py
```

Streamlit should open the dashboard in your browser. If it does not, use the local URL printed in the terminal.

## Run the Optimizer

To generate an optimized schedule independently, run:

```bash
python -m src.optimizer
```

The optimizer validates the input baseline, searches for a lower-cost feasible schedule, and writes the result to `data/optimized_schedule.csv`.

## Run the Baseline Calculator

```bash
python -m src.baseline
```

This calculates baseline energy consumption and electricity costs and checks schedule feasibility.

## Run the Automated Tests

```bash
python -m unittest discover -s tests -v
```

The tests cover baseline validity, cost calculations, machine conflicts, solver output, optimized schedule feasibility, and comparison with baseline cost.

## Scheduling Model

The current prototype uses a 12-hour planning horizon with hourly scheduling decisions.

- Jobs have fixed durations and assigned machines.
- Jobs cannot start before their release hour.
- Jobs must finish by their deadlines.
- Each machine can process only one job at a time.
- Different machines can operate simultaneously.
- Jobs are non-preemptive: once started, a job runs for its full duration.
- Electricity costs vary by hour.

The optimizer minimizes the estimated electricity cost while respecting these constraints.

## Sustainability Impact

By shifting suitable production jobs toward lower-price electricity periods, FlexFactory demonstrates how scheduling decisions can potentially reduce electricity expenditure and support more energy-aware industrial operations.

Actual emissions reductions have **not** been calculated or verified. Real-world evaluation would require factory operating data, applicable electricity tariffs, and an appropriate emissions-intensity dataset.

## Current Limitations

- All supplied factory and tariff data are simulated.
- The prototype uses a fixed machine assignment for each job.
- The scheduling horizon and time resolution are limited.
- Real factory deployment, live electricity-tariff integration, and measured emissions validation are not implemented.

## Future Improvements

- Test the optimizer with real factory production data.
- Incorporate actual time-of-use electricity tariffs.
- Estimate emissions using a reliable electricity emissions factor.
- Add configurable production jobs and machines.
- Evaluate the system on larger scheduling problems.

## Project Theme

**Sustainable Sector — Industrial Decarbonisation and Pollution Control**

FlexFactory is an early-stage demonstration of how optimization can support more cost-aware and potentially energy-efficient industrial production.
