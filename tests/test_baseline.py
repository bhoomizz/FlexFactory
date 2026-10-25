
import unittest

from src.baseline import (
    load_data,
    validate_schedule,
    calculate_costs,
    build_solar_profile,
    estimate_solar_coincidence,
    estimate_grid_energy_and_emissions,
)


class BaselineTests(unittest.TestCase):

    def setUp(self):
        self.machines, self.jobs, self.prices, self.schedule = load_data()

    def test_baseline_is_valid(self):
        errors = validate_schedule(
            self.machines, self.jobs, self.prices, self.schedule
        )
        self.assertEqual(errors, [])

    def test_baseline_totals(self):
        energy, cost, _ = calculate_costs(
            self.jobs, self.prices, self.schedule
        )
        self.assertAlmostEqual(energy, 23.0)
        self.assertAlmostEqual(cost, 97.0)

    def test_machine_conflict_is_detected(self):
        broken_schedule = [dict(row) for row in self.schedule]

        # Move J3 into J1's time on M1.
        j3 = next(row for row in broken_schedule if row["job_id"] == "J3")
        j3["start_hour"] = 1
        j3["end_hour"] = 3

        errors = validate_schedule(
            self.machines, self.jobs, self.prices, broken_schedule
        )
        self.assertTrue(any("Machine conflict" in e for e in errors))

    def test_solar_profile_and_grid_analysis(self):
        profile = build_solar_profile()
        self.assertEqual(len(profile), 12)
        self.assertTrue(all(0.0 <= row["availability"] <= 1.0 for row in profile))
        self.assertGreater(sum(row["availability"] for row in profile), 0.0)

        solar_match, grid_energy, emissions, solar_share = (
            estimate_grid_energy_and_emissions(
                self.schedule, self.jobs, profile, emissions_factor=0.45
            )
        )

        self.assertGreaterEqual(solar_match, 0.0)
        self.assertGreaterEqual(grid_energy, 0.0)
        self.assertGreaterEqual(emissions, 0.0)
        self.assertGreaterEqual(solar_share, 0.0)
        self.assertLessEqual(solar_share, 1.0)
        self.assertGreaterEqual(solar_match + grid_energy, 23.0 - 1e-9)

        coincident = estimate_solar_coincidence(self.schedule, self.jobs, profile)
        self.assertAlmostEqual(coincident, solar_match)


if __name__ == "__main__":
    unittest.main()
