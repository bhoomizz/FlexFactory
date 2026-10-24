
import csv

from ortools.sat.python import cp_model

from src.baseline import (
    DATA,
    HORIZON,
    load_data,
    validate_schedule,
    calculate_costs,
)


def optimize_schedule(machines, jobs, prices):
    model = cp_model.CpModel()
    price_map = {int(p["start_hour"]): int(p["price_per_kwh"])
                 for p in prices}

    starts = {}
    intervals = {}
    job_costs = {}
    machine_intervals = {m["machine_id"]: [] for m in machines}

    for job in jobs:
        job_id = job["job_id"]
        machine_id = job["machine_id"]
        duration = int(job["duration_hours"])
        power = job["power_kw"]
        release = int(job["release_hour"])
        deadline = int(job["deadline_hour"])

        earliest = max(0, release)
        latest = min(HORIZON - duration, deadline - duration)

        if earliest > latest:
            raise ValueError(f"No feasible start time for {job_id}")

        start = model.NewIntVar(earliest, latest, f"start_{job_id}")
        end = model.NewIntVar(earliest + duration,
                              latest + duration, f"end_{job_id}")

        model.Add(end == start + duration)

        interval = model.NewIntervalVar(
            start, duration, end, f"interval_{job_id}"
        )

        starts[job_id] = start
        intervals[job_id] = interval
        machine_intervals[machine_id].append(interval)

        # Scale costs by 2 so half-rupee costs become integers.
        possible_costs = []

        for start_hour in range(earliest, latest + 1):
            cost = sum(
                power * price_map[hour]
                for hour in range(start_hour, start_hour + duration)
            )
            possible_costs.append(round(cost * 2))

        cost_var = model.NewIntVar(
            min(possible_costs), max(possible_costs),
            f"cost_{job_id}"
        )

        model.AddElement(
            start - earliest, possible_costs, cost_var
        )
        job_costs[job_id] = cost_var

    # Each machine can handle only one job at a time.
    for machine_id, machine_jobs in machine_intervals.items():
        model.AddNoOverlap(machine_jobs)

    model.Minimize(sum(job_costs.values()))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(
            f"No feasible schedule found. Solver status: "
            f"{solver.StatusName(status)}"
        )

    schedule = []

    for job in jobs:
        job_id = job["job_id"]
        start_hour = solver.Value(starts[job_id])
        duration = int(job["duration_hours"])

        schedule.append({
            "job_id": job_id,
            "start_hour": start_hour,
            "end_hour": start_hour + duration,
        })

    return schedule, solver.StatusName(status)


def save_schedule(schedule):
    output_path = DATA / "optimized_schedule.csv"

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["job_id", "start_hour", "end_hour"]
        )
        writer.writeheader()
        writer.writerows(schedule)

    return output_path


def main():
    machines, jobs, prices, baseline = load_data()

    baseline_errors = validate_schedule(
        machines, jobs, prices, baseline
    )
    if baseline_errors:
        raise ValueError(
            "Baseline is invalid: " + "; ".join(baseline_errors)
        )

    _, baseline_cost, _ = calculate_costs(jobs, prices, baseline)

    optimized, status = optimize_schedule(machines, jobs, prices)

    errors = validate_schedule(
        machines, jobs, prices, optimized
    )
    if errors:
        raise ValueError(
            "Optimizer produced an invalid schedule: "
            + "; ".join(errors)
        )

    energy, optimized_cost, details = calculate_costs(
        jobs, prices, optimized
    )

    output_path = save_schedule(optimized)
    savings = baseline_cost - optimized_cost
    savings_percent = (
        savings / baseline_cost * 100 if baseline_cost else 0
    )

    print(f"Solver status: {status}")
    print("\nOptimized schedule:")
    for row in sorted(optimized, key=lambda r: (r["start_hour"], r["job_id"])):
        print(
            f"{row['job_id']}: "
            f"{row['start_hour']}–{row['end_hour']}"
        )

    print(f"\nSchedule validation: PASSED")
    print(f"Baseline cost: Rs {baseline_cost:.2f}")
    print(f"Optimized cost: Rs {optimized_cost:.2f}")
    print(f"Cost savings: Rs {savings:.2f} ({savings_percent:.2f}%)")
    print(f"Optimized energy: {energy:.2f} kWh")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
