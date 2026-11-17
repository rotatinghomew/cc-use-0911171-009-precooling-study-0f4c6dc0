import copy
import json
import unittest
from pathlib import Path
from app import inspect
from records import load


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(load(Path(__file__).parents[1] / "fixtures/data.json"))
        self.day = "2026-11-01"

    def test_end_to_end_inspection_is_json_and_repeatable(self):
        before = copy.deepcopy(self.data)
        first = inspect(self.data, self.day)
        self.assertEqual(first, inspect(self.data, self.day))
        self.assertEqual(before, self.data)
        self.assertTrue(json.dumps(first, ensure_ascii=False, allow_nan=False))

    def test_enrollment_is_not_treatment(self):
        from outcomes import batches
        self.assertTrue(any(row["enrolled"] and not row["precooled"] for row in batches(self.data, self.day)))

    def test_missing_followup_remains_unknown(self):
        from outcomes import batches
        rows = [row for row in batches(self.data, self.day) if not row["followed"]]
        self.assertTrue(rows)
        self.assertTrue(all(row["loss_rate"] is None for row in rows))

    def test_cost_change_does_not_change_observed_loss(self):
        from outcomes import descriptive
        from economics import ledger
        before = descriptive(self.data, self.day)
        first = ledger(self.data, self.day, "c1")
        second = ledger(self.data, self.day, "c2")
        self.assertEqual([row["batch_id"] for row in first], [row["batch_id"] for row in second])
        self.assertEqual(before, descriptive(self.data, self.day))
        self.assertNotEqual(first[0]["transport_cents"], second[0]["transport_cents"])

    def test_subsidy_requires_enrollment_and_treatment(self):
        from economics import ledger
        from outcomes import batches
        states = {row["batch_id"]: row for row in batches(self.data, self.day)}
        for row in ledger(self.data, self.day, "c1"):
            if row["subsidy_cents"]:
                self.assertTrue(states[row["batch_id"]]["enrolled"] and states[row["batch_id"]]["precooled"])

    def test_unknown_cost_version_rejected(self):
        from economics import ledger
        with self.assertRaises(ValueError):
            ledger(self.data, self.day, "missing")

    def test_followup_mass_is_checked(self):
        from outcomes import batches
        self.data["followups"][0]["lost_kg"] = 200
        with self.assertRaises(ValueError):
            batches(self.data, self.day)

    def test_shared_weighing_remains_linked(self):
        from transfers import observed_balances
        groups = observed_balances(self.data, self.day)
        shared = [row for stages in groups.values() for rows in stages.values() for row in rows if row["transfer_id"] == "shared-inbound"]
        self.assertEqual(len(shared), 2)
        self.assertEqual(len({row["calibration_group"] for row in shared}), 1)

    def test_invalid_shared_weights_rejected(self):
        from transfers import visible
        self.data["transfers"][-1]["batch_shares"] = {"B1-0": .1}
        with self.assertRaises(ValueError):
            visible(self.data, self.day)
