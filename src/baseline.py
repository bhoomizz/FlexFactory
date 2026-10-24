
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


def main():
    machines, jobs, prices, schedule = load_data()
    errors = validate_schedule(machines, jobs, prices, schedule)

    if errors:
        print("SCHEDULE INVALID")
        for error in errors:
            print("-", error)
        return

    energy, cost, details = calculate_costs(jobs, prices, schedule)

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


if __name__ == "__main__":
    main()
