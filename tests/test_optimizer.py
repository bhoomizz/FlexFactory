
import unittest

from src.baseline import (
    load_data,
    validate_schedule,
    calculate_costs,
)
from src.optimizer import optimize_schedule


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

    def test_optimized_cost_is_not_higher(self):
        _, baseline_cost, _ = calculate_costs(
            self.jobs, self.prices, self.baseline
        )
        _, optimized_cost, _ = calculate_costs(
            self.jobs, self.prices, self.optimized
        )
        self.assertLessEqual(optimized_cost, baseline_cost)


if __name__ == "__main__":
    unittest.main()
