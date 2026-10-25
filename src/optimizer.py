
import csv
from pathlib import Path

from ortools.sat.python import cp_model

from src.baseline import (
    DATA,
    HORIZON,
    load_data,
    validate_schedule,
    calculate_costs,
    calculate_schedule_energy_metrics,
    load_solar_profile,
)


def optimize_schedule(machines, jobs, prices):
    model = cp_model.CpModel()
    solar_profile = load_solar_profile()
    scale = 10

    price_map = {
        int(p["start_hour"]): float(p["price_per_kwh"])
        for p in prices
    }

    if any(price < 0 for price in price_map.values()):
        raise ValueError("Electricity prices cannot be negative.")

    if set(price_map) != set(range(HORIZON)):
        raise ValueError("Electricity prices must cover the full horizon.")

    starts = {}
    machine_intervals = {
        machine["machine_id"]: [] for machine in machines
    }
    hourly_load = {hour: [] for hour in range(HORIZON)}

    for job in jobs:
        job_id = job["job_id"]
        machine_id = job["machine_id"]
        duration = int(job["duration_hours"])
        power = float(job["power_kw"])
        release = int(job["release_hour"])
        deadline = int(job["deadline_hour"])

        if duration <= 0 or power < 0:
            raise ValueError(
                f"Job {job_id} must have positive duration and non-negative power."
            )

        if machine_id not in machine_intervals:
            raise ValueError(
                f"Unknown machine {machine_id} for job {job_id}."
            )

        earliest = max(0, release)
        latest = min(HORIZON - duration, deadline - duration)

        if earliest > latest:
            raise ValueError(f"No feasible start time for {job_id}.")

        start = model.NewIntVar(earliest, latest, f"start_{job_id}")
        end = model.NewIntVar(
            earliest + duration,
            latest + duration,
            f"end_{job_id}",
        )
        model.Add(end == start + duration)

        interval = model.NewIntervalVar(
            start, duration, end, f"interval_{job_id}"
        )

        starts[job_id] = start
        machine_intervals[machine_id].append(interval)

        power_scaled = int(round(power * scale))

        for hour in range(HORIZON):
            active = model.NewBoolVar(f"active_{job_id}_{hour}")
            allowed = []
            for start_time in range(earliest, latest + 1):
                active_value = 1 if start_time <= hour < start_time + duration else 0
                allowed.append((start_time, active_value))
            model.AddAllowedAssignments([start, active], allowed)
            hourly_load[hour].append(power_scaled * active)

    for machine_jobs in machine_intervals.values():
        model.AddNoOverlap(machine_jobs)

    solar_used = {}
    grid_energy = {}
    for hour in range(HORIZON):
        total_load = sum(hourly_load[hour])
        solar_available = int(round(solar_profile[hour] * scale))

        solar_used[hour] = model.NewIntVar(
            0,
            solar_available,
            f"solar_used_{hour}",
        )
        model.Add(solar_used[hour] <= total_load)

        grid_energy[hour] = model.NewIntVar(
            0,
            sum(int(round(float(job["power_kw"]) * scale)) for job in jobs),
            f"grid_energy_{hour}",
        )
        model.Add(grid_energy[hour] == total_load - solar_used[hour])

    objective = sum(
        grid_energy[hour] * int(round(price_map[hour]))
        for hour in range(HORIZON)
    )
    model.Minimize(objective)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(
            "No feasible schedule found. Solver status: "
            + solver.StatusName(status)
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


def save_schedule(schedule, machines, jobs, prices, output_path=None):
    errors = validate_schedule(machines, jobs, prices, schedule)
    if errors:
        raise ValueError(
            "Refusing to save an invalid schedule: " + "; ".join(errors)
        )

    if output_path is None:
        output_path = DATA / "optimized_schedule.csv"
    else:
        output_path = Path(output_path)

    with open(
        output_path, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["job_id", "start_hour", "end_hour"],
        )
        writer.writeheader()
        writer.writerows(schedule)

    return output_path


def generate_and_save_schedule(machines, jobs, prices):
    schedule, status = optimize_schedule(machines, jobs, prices)
    output_path = save_schedule(schedule, machines, jobs, prices)
    return schedule, status, output_path


def main():
    machines, jobs, prices, baseline = load_data()

    baseline_errors = validate_schedule(
        machines, jobs, prices, baseline
    )
    if baseline_errors:
        raise ValueError(
            "Baseline is invalid: " + "; ".join(baseline_errors)
        )

    _, baseline_cost, _ = calculate_costs(
        jobs, prices, baseline
    )

    optimized, status, output_path = generate_and_save_schedule(
        machines, jobs, prices
    )

    energy, optimized_cost, _ = calculate_costs(
        jobs, prices, optimized
    )

    savings = baseline_cost - optimized_cost
    savings_percent = (
        savings / baseline_cost * 100 if baseline_cost else 0
    )

    print(f"Solver status: {status}")
    print("\nOptimized schedule:")

    for row in sorted(
        optimized,
        key=lambda r: (r["start_hour"], r["job_id"]),
    ):
        print(
            f"{row['job_id']}: "
            f"{row['start_hour']}–{row['end_hour']}"
        )

    print("\nSchedule validation: PASSED")
    print(f"Baseline cost: Rs {baseline_cost:.2f}")
    print(f"Optimized gross cost: Rs {optimized_cost:.2f}")
    print(
        f"Gross cost difference: Rs {savings:.2f} "
        f"({savings_percent:.2f}%)"
    )
    print(f"Optimized energy: {energy:.2f} kWh")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
