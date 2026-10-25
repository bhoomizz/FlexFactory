
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HORIZON = 12


def read_csv(filename):
    with open(DATA / filename, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_data():
    machines = read_csv("machines.csv")
    jobs = read_csv("jobs.csv")
    prices = read_csv("electricity_prices.csv")
    schedule = read_csv("baseline_schedule.csv")

    for job in jobs:
        for key in ("duration_hours", "power_kw",
                    "release_hour", "deadline_hour"):
            job[key] = float(job[key])

    for row in schedule:
        row["start_hour"] = int(row["start_hour"])
        row["end_hour"] = int(row["end_hour"])

    for price in prices:
        for key in ("start_hour", "end_hour", "price_per_kwh"):
            price[key] = float(price[key])

    return machines, jobs, prices, schedule


def validate_schedule(machines, jobs, prices, schedule):
    errors = []
    machine_ids = {m["machine_id"] for m in machines}
    job_map = {j["job_id"]: j for j in jobs}
    price_map = {int(p["start_hour"]): p for p in prices}
    schedule_ids = [s["job_id"] for s in schedule]

    # Check price coverage and hourly slots.
    for hour in range(HORIZON):
        p = price_map.get(hour)
        if p is None or p["end_hour"] != hour + 1:
            errors.append(f"Missing or invalid electricity price at hour {hour}.")

    # Every job must appear exactly once.
    for job_id in job_map:
        if schedule_ids.count(job_id) != 1:
            errors.append(f"{job_id} must appear exactly once.")

    for row in schedule:
        job_id = row["job_id"]

        if job_id not in job_map:
            errors.append(f"Unknown job: {job_id}.")
            continue

        job = job_map[job_id]
        start, end = row["start_hour"], row["end_hour"]

        if job["machine_id"] not in machine_ids:
            errors.append(f"{job_id} has an unknown machine.")

        if end - start != job["duration_hours"]:
            errors.append(f"{job_id} has an incorrect duration.")

        if start < job["release_hour"]:
            errors.append(f"{job_id} starts before its release time.")

        if end > job["deadline_hour"]:
            errors.append(f"{job_id} misses its deadline.")

        if start < 0 or end > HORIZON or end <= start:
            errors.append(f"{job_id} is outside the planning horizon.")

    # No two jobs may overlap on the same machine.
    for i, first in enumerate(schedule):
        if first["job_id"] not in job_map:
            continue

        machine = job_map[first["job_id"]]["machine_id"]

        for second in schedule[i + 1:]:
            if second["job_id"] not in job_map:
                continue

            other_machine = job_map[second["job_id"]]["machine_id"]

            if machine == other_machine:
                overlap = (
                    first["start_hour"] < second["end_hour"]
                    and second["start_hour"] < first["end_hour"]
                )
                if overlap:
                    errors.append(
                        f"Machine conflict: {first['job_id']} and "
                        f"{second['job_id']} overlap on {machine}."
                    )

    return errors


def calculate_costs(jobs, prices, schedule):
    job_map = {j["job_id"]: j for j in jobs}
    price_map = {int(p["start_hour"]): p for p in prices}

    total_energy = 0.0
    total_cost = 0.0
    details = []

    for row in schedule:
        job = job_map[row["job_id"]]
        start, end = row["start_hour"], row["end_hour"]
        power = job["power_kw"]
        energy = power * (end - start)
        cost = 0.0

        for hour in range(start, end):
            price = price_map[hour]["price_per_kwh"]
            cost += power * price

        total_energy += energy
        total_cost += cost

        details.append({
            "job_id": row["job_id"],
            "energy_kwh": energy,
            "cost_rupees": cost,
        })

    return total_energy, total_cost, details


def load_solar_profile():
    """Load the canonical simulated solar profile from the project CSV file."""
    path = DATA / "solar_availability.csv"

    with open(path, newline="", encoding="utf-8-sig") as file:
        profile = {
            int(row["hour"]): float(row["solar_available_kwh"])
            for row in csv.DictReader(file)
        }

    if any(value < 0 for value in profile.values()):
        raise ValueError("Solar availability cannot be negative.")

    if set(profile) != set(range(HORIZON)):
        raise ValueError(
            f"Solar profile must contain every hour from 0 to {HORIZON - 1}."
        )

    return profile


def _solar_map(solar_profile):
    if isinstance(solar_profile, dict):
        return {int(hour): float(value) for hour, value in solar_profile.items()}

    return {
        int(row["hour"]): float(
            row.get("solar_available_kwh", row.get("availability", 0.0))
        )
        for row in solar_profile
    }


def build_solar_profile():
    """Return the canonical hourly solar profile in a tabular format."""
    profile = load_solar_profile()
    return [
        {
            "hour": hour,
            "start_hour": hour,
            "end_hour": hour + 1,
            "solar_available_kwh": profile[hour],
            "availability": profile[hour],
        }
        for hour in range(HORIZON)
    ]


def calculate_schedule_energy_metrics(
    schedule,
    jobs,
    prices,
    solar_profile,
    emissions_factor=0.45,
):
    """Calculate production, solar-use, grid-energy, and emissions metrics."""
    job_map = {job["job_id"]: job for job in jobs}
    price_map = {int(p["start_hour"]): float(p["price_per_kwh"]) for p in prices}
    solar_map = _solar_map(solar_profile)
    hourly_load = {hour: 0.0 for hour in range(HORIZON)}

    for row in schedule:
        job = job_map[row["job_id"]]
        power = float(job["power_kw"])
        for hour in range(int(row["start_hour"]), int(row["end_hour"])):
            hourly_load[hour] += power

    hourly_solar_used = {
        hour: min(hourly_load[hour], solar_map.get(hour, 0.0))
        for hour in range(HORIZON)
    }
    hourly_grid = {
        hour: max(hourly_load[hour] - hourly_solar_used[hour], 0.0)
        for hour in range(HORIZON)
    }

    total_energy = sum(hourly_load.values())
    total_solar = sum(hourly_solar_used.values())
    total_grid = sum(hourly_grid.values())
    gross_cost = sum(
        hourly_load[hour] * price_map.get(hour, 0.0)
        for hour in range(HORIZON)
    )
    grid_cost = sum(
        hourly_grid[hour] * price_map.get(hour, 0.0)
        for hour in range(HORIZON)
    )
    estimated_emissions = total_grid * float(emissions_factor)
    solar_share = total_solar / total_energy if total_energy else 0.0

    return {
        "total_energy_kwh": total_energy,
        "gross_cost_rupees": gross_cost,
        "solar_used_kwh": total_solar,
        "grid_energy_kwh": total_grid,
        "grid_cost_rupees": grid_cost,
        "estimated_emissions_kg": estimated_emissions,
        "solar_share": solar_share,
        "hourly_load_kwh": hourly_load,
        "hourly_solar_used_kwh": hourly_solar_used,
        "hourly_grid_energy_kwh": hourly_grid,
    }


def calculate_schedule_comparison_metrics(
    baseline_schedule,
    optimized_schedule,
    jobs,
    prices,
    solar_profile,
    emissions_factor=0.45,
):
    """Calculate comparable solar-aware metrics for two schedules."""
    baseline_metrics = calculate_schedule_energy_metrics(
        baseline_schedule,
        jobs,
        prices,
        solar_profile,
        emissions_factor=emissions_factor,
    )
    optimized_metrics = calculate_schedule_energy_metrics(
        optimized_schedule,
        jobs,
        prices,
        solar_profile,
        emissions_factor=emissions_factor,
    )
    baseline_grid_cost = baseline_metrics["grid_cost_rupees"]
    grid_cost_reduction = (
        baseline_grid_cost - optimized_metrics["grid_cost_rupees"]
    )

    return {
        "baseline": baseline_metrics,
        "optimized": optimized_metrics,
        "grid_cost_reduction_rupees": grid_cost_reduction,
        "grid_cost_reduction_percent": (
            grid_cost_reduction / baseline_grid_cost * 100
            if baseline_grid_cost
            else None
        ),
    }


def estimate_solar_coincidence(schedule, jobs, solar_profile):
    """Return the amount of scheduled production energy aligned with solar."""
    metrics = calculate_schedule_energy_metrics(schedule, jobs, [], solar_profile)
    return metrics["solar_used_kwh"]


def estimate_grid_energy_and_emissions(schedule, jobs, solar_profile, emissions_factor=0.45):
    """Return solar-aligned energy, grid energy, emissions, and solar-share metrics."""
    metrics = calculate_schedule_energy_metrics(
        schedule,
        jobs,
        [{"start_hour": hour, "end_hour": hour + 1, "price_per_kwh": 0.0} for hour in range(HORIZON)],
        solar_profile,
        emissions_factor=emissions_factor,
    )
    return (
        metrics["solar_used_kwh"],
        metrics["grid_energy_kwh"],
        metrics["estimated_emissions_kg"],
        metrics["solar_share"],
    )


def main():
    machines, jobs, prices, schedule = load_data()
    errors = validate_schedule(machines, jobs, prices, schedule)

    if errors:
        print("SCHEDULE INVALID")
        for error in errors:
            print("-", error)
        return

    energy, cost, details = calculate_costs(jobs, prices, schedule)
    solar_profile = build_solar_profile()
    solar_match, grid_energy, emissions, solar_share = estimate_grid_energy_and_emissions(
        schedule, jobs, solar_profile
    )

    print("BASELINE SCHEDULE: VALID")
    print("\nJob-wise results:")
    for item in details:
        print(
            f"{item['job_id']}: "
            f"{item['energy_kwh']:.2f} kWh, "
            f"Rs {item['cost_rupees']:.2f}"
        )

    print(f"\nTotal energy: {energy:.2f} kWh")
    print(f"Total electricity cost: Rs {cost:.2f}")
    print(f"Solar-coincident energy: {solar_match:.2f} kWh")
    print(f"Grid energy: {grid_energy:.2f} kWh")
    print(f"Estimated grid emissions: {emissions:.2f} kg CO₂")
    print(f"Solar share: {solar_share * 100:.1f}%")


if __name__ == "__main__":
    main()
