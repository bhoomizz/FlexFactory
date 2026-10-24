
import unittest

from src.baseline import (
    load_data,
    validate_schedule,
    calculate_costs,
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


if __name__ == "__main__":
    unittest.main()
