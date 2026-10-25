
import csv
import tempfile
import unittest
from pathlib import Path

from src.baseline import (
    load_data,
    validate_schedule,
    calculate_costs,
    calculate_schedule_energy_metrics,
    calculate_schedule_comparison_metrics,
    load_solar_profile,
)
from src.optimizer import generate_and_save_schedule, optimize_schedule, save_schedule


class OptimizerTests(unittest.TestCase):

    def setUp(self):
        self.machines, self.jobs, self.prices, self.baseline = load_data()
        self.optimized, self.status = optimize_schedule(
            self.machines, self.jobs, self.prices
        )

    def test_solver_finds_solution(self):
        self.assertIn(self.status, ("OPTIMAL", "FEASIBLE"))

    def test_optimized_schedule_is_valid(self):
        errors = validate_schedule(
            self.machines, self.jobs, self.prices, self.optimized
        )
        self.assertEqual(errors, [])

    def test_optimized_grid_cost_is_not_higher(self):
        solar_profile = load_solar_profile()
        baseline_metrics = calculate_schedule_energy_metrics(
            self.baseline,
            self.jobs,
            self.prices,
            solar_profile,
        )
        optimized_metrics = calculate_schedule_energy_metrics(
            self.optimized,
            self.jobs,
            self.prices,
            solar_profile,
        )

        self.assertGreaterEqual(optimized_metrics["grid_energy_kwh"], 0.0)
        self.assertLessEqual(
            optimized_metrics["grid_cost_rupees"],
            baseline_metrics["grid_cost_rupees"] + 1e-9,
        )

    def test_dashboard_comparison_metrics_match_shared_calculations(self):
        solar_profile = load_solar_profile()
        comparison = calculate_schedule_comparison_metrics(
            self.baseline,
            self.optimized,
            self.jobs,
            self.prices,
            solar_profile,
        )
        baseline_metrics = calculate_schedule_energy_metrics(
            self.baseline,
            self.jobs,
            self.prices,
            solar_profile,
        )
        optimized_metrics = calculate_schedule_energy_metrics(
            self.optimized,
            self.jobs,
            self.prices,
            solar_profile,
        )

        self.assertEqual(comparison["baseline"], baseline_metrics)
        self.assertEqual(comparison["optimized"], optimized_metrics)
        self.assertAlmostEqual(
            comparison["grid_cost_reduction_rupees"],
            baseline_metrics["grid_cost_rupees"]
            - optimized_metrics["grid_cost_rupees"],
        )

    def test_hourly_solar_constraints_are_respected(self):
        solar_profile = load_solar_profile()
        metrics = calculate_schedule_energy_metrics(
            self.optimized,
            self.jobs,
            self.prices,
            solar_profile,
        )

        for hour in range(len(solar_profile)):
            self.assertLessEqual(
                metrics["hourly_solar_used_kwh"][hour],
                solar_profile[hour],
            )
            self.assertLessEqual(
                metrics["hourly_solar_used_kwh"][hour],
                metrics["hourly_load_kwh"][hour],
            )
            self.assertAlmostEqual(
                metrics["hourly_grid_energy_kwh"][hour],
                max(metrics["hourly_load_kwh"][hour] - metrics["hourly_solar_used_kwh"][hour], 0.0),
            )

    def test_export_matches_fresh_optimizer_result(self):
        exported_schedule, status, output_path = generate_and_save_schedule(
            self.machines,
            self.jobs,
            self.prices,
        )

        with open(output_path, newline="", encoding="utf-8") as file:
            saved_schedule = [
                {
                    "job_id": row["job_id"],
                    "start_hour": int(row["start_hour"]),
                    "end_hour": int(row["end_hour"]),
                }
                for row in csv.DictReader(file)
            ]

        self.assertIn(status, ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(exported_schedule, self.optimized)
        self.assertEqual(saved_schedule, exported_schedule)
        self.assertEqual(
            validate_schedule(
                self.machines,
                self.jobs,
                self.prices,
                saved_schedule,
            ),
            [],
        )

    def test_invalid_schedule_is_not_written(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            output_path = Path(temp_directory) / "optimized_schedule.csv"
            output_path.write_text("existing export\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Refusing to save"):
                save_schedule(
                    [{"job_id": "J1", "start_hour": 0, "end_hour": 1}],
                    self.machines,
                    self.jobs,
                    self.prices,
                    output_path,
                )

            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "existing export\n",
            )


if __name__ == "__main__":
    unittest.main()
