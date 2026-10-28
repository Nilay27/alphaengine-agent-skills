"""Offline regression coverage for complete simulation inputs and faithful export."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "skills" /
          "alphaengine-strategy-arena-agent" / "scripts" / "prepare_candidate.py")
SPEC = importlib.util.spec_from_file_location("prepare_candidate", SCRIPT)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


def parameter(key, kind, default, **constraints):
    return {"key": key, "type": kind, "required": False,
            "defaultValue": default, "constraints": constraints}


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.markets = {"status": "ok", "data": [
            {"marketId": 42, "marketKey": "fixture-market", "chainId": 42161,
             "marketAddress": "fixture-address"},
        ]}
        self.schemas = {"yield-bollinger": {"status": "ok", "data": [
            parameter("field", "string", "logYield", enum=["logYield", "close"]),
            parameter("window", "integer", 10, min=2, max=250),
            parameter("numStd", "number", 2, min=0, max=10),
        ]}}
        self.draft = {"marketId": 42, "timeframe": "hourly", "capital": "100000",
                      "components": [{"strategyId": "yield-bollinger", "weightBps": 10000,
                                      "strategyParams": {"window": 14}}]}

    def prepare(self):
        return helper.prepare_candidate(self.draft, self.schemas, self.markets)[0]

    def assert_code(self, code, operation=None):
        with self.assertRaises(helper.CandidateError) as caught:
            (operation or self.prepare)()
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(caught.exception.path)

    def test_omitted_num_std_is_materialized_before_testing(self):
        original = copy.deepcopy(self.draft)
        prepared = self.prepare()
        self.assertEqual(prepared["components"][0]["strategyParams"],
                         {"field": "logYield", "window": 14, "numStd": 2})
        self.assertEqual(self.draft, original)

    def test_zero_override_and_zero_default_are_retained(self):
        self.draft["components"][0]["strategyParams"]["numStd"] = 0
        self.assertEqual(self.prepare()["components"][0]["strategyParams"]["numStd"], 0)
        self.schemas["yield-bollinger"]["data"][2]["defaultValue"] = 0
        del self.draft["components"][0]["strategyParams"]["numStd"]
        self.assertEqual(self.prepare()["components"][0]["strategyParams"]["numStd"], 0)

    def test_missing_parameter_has_no_invented_default(self):
        del self.schemas["yield-bollinger"]["data"][2]["defaultValue"]
        self.schemas["yield-bollinger"]["data"][2]["required"] = True
        self.assert_code("MISSING_PARAMETER")

    def test_unknown_parameters_are_rejected(self):
        self.draft["components"][0]["strategyParams"]["typo"] = 3
        self.assert_code("UNKNOWN_PARAMETER")

    def test_actual_min_max_bounds_are_enforced(self):
        for invalid in (1, 251):
            with self.subTest(window=invalid):
                self.draft["components"][0]["strategyParams"]["window"] = invalid
                self.assert_code("PARAMETER_OUT_OF_RANGE")
        for boundary in (2, 250):
            self.draft["components"][0]["strategyParams"]["window"] = boundary
            self.prepare()

    def test_unknown_constraint_does_not_silently_skip_validation(self):
        self.schemas["yield-bollinger"]["data"][1]["constraints"] = {"minimum": 2}
        self.assert_code("UNSUPPORTED_SCHEMA_CONSTRAINT")

    def test_boolean_is_not_an_integer_and_no_numeric_string_coercion(self):
        for invalid in (True, "14", None):
            self.draft["components"][0]["strategyParams"]["window"] = invalid
            self.assert_code("INVALID_PARAMETER_TYPE")

    def test_enum_is_enforced(self):
        self.draft["components"][0]["strategyParams"]["field"] = "unknown"
        self.assert_code("INVALID_PARAMETER_ENUM")

    def test_nonfinite_inputs_are_rejected_including_optional_settings(self):
        for invalid in (float("nan"), float("inf"), -float("inf")):
            self.draft["metadata"] = {"invalid": invalid}
            self.assert_code("INVALID_JSON_VALUE")

    def test_schema_default_and_bound_must_be_finite(self):
        self.schemas["yield-bollinger"]["data"][2]["defaultValue"] = float("inf")
        self.assert_code("INVALID_PARAMETER_TYPE")
        self.schemas["yield-bollinger"]["data"][2]["defaultValue"] = 2
        self.schemas["yield-bollinger"]["data"][2]["constraints"]["max"] = float("nan")
        self.assert_code("INVALID_SCHEMA")

    def test_schema_response_and_duplicate_keys_are_validated(self):
        self.schemas["yield-bollinger"]["status"] = "error"
        self.assert_code("INVALID_RESPONSE")
        self.schemas["yield-bollinger"]["status"] = "ok"
        self.schemas["yield-bollinger"]["data"].append(self.schemas["yield-bollinger"]["data"][0])
        self.assert_code("DUPLICATE_SCHEMA_KEY")

    def test_unknown_strategy_stops_before_simulation(self):
        self.draft["components"][0]["strategyId"] = "unknown"
        self.assert_code("MISSING_SCHEMA")

    def test_positive_integer_weights_and_total(self):
        for invalid in (True, 0, -1, 10001):
            self.draft["components"][0]["weightBps"] = invalid
            self.assert_code("INVALID_WEIGHT")
        self.draft["components"][0]["weightBps"] = 9999
        self.assert_code("INVALID_WEIGHT_TOTAL")

    def test_positive_finite_string_capital(self):
        for invalid in (100000, "0", "-1", "NaN", "Infinity", "no"):
            self.draft["capital"] = invalid
            self.assert_code("INVALID_CAPITAL")

    def test_market_mapping_must_be_unique_and_timeframe_explicit(self):
        self.markets["data"].append(copy.deepcopy(self.markets["data"][0]))
        self.assert_code("MARKET_NOT_UNIQUE")
        self.markets["data"].pop()
        del self.draft["timeframe"]
        self.assert_code("INVALID_TIMEFRAME")

    def test_export_refuses_to_fill_defaults_after_testing(self):
        self.assert_code("INCOMPLETE_TESTED_REQUEST", lambda: helper.dashboard_candidate(
            self.draft, self.schemas, self.markets))

    def test_replay_and_export_preserve_complete_components_and_order(self):
        second = copy.deepcopy(self.draft["components"][0])
        self.draft["components"][0]["weightBps"] = 4000
        second["weightBps"] = 6000
        second["strategyParams"]["window"] = 21
        self.draft["components"].append(second)
        self.draft["timeframe"] = "daily"
        self.draft["deterministicSeed"] = "fixed"
        prepared = self.prepare()
        replay, _market = helper.prepare_candidate(prepared, self.schemas, self.markets)
        self.assertEqual(helper.json_text(prepared), helper.json_text(replay))
        exported = helper.dashboard_candidate(prepared, self.schemas, self.markets)
        self.assertEqual(exported, {"marketKey": "fixture-market", "timeframe": "daily",
                                    "components": prepared["components"]})
        self.assertEqual([c["strategyParams"]["window"] for c in exported["components"]], [14, 21])

    def test_export_rejects_component_settings_it_cannot_represent(self):
        prepared = self.prepare()
        prepared["components"][0]["componentId"] = "internal-only"
        self.assert_code("UNSUPPORTED_DASHBOARD_COMPONENT", lambda: helper.dashboard_candidate(
            prepared, self.schemas, self.markets))

    def test_cli_prepare_export_and_structured_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, value in (("draft", self.draft), ("schemas", self.schemas), ("markets", self.markets)):
                (root / (name + ".json")).write_text(json.dumps(value), encoding="utf-8")
            shared = ["--schemas", str(root / "schemas.json"), "--markets", str(root / "markets.json")]

            def run(mode, source, output):
                return subprocess.run([sys.executable, str(SCRIPT), mode, "--candidate", str(root / source),
                                       "--output", str(root / output), *shared], capture_output=True, text=True)

            success = run("prepare", "draft.json", "tested.json")
            self.assertEqual(success.returncode, 0, success.stderr)
            self.assertEqual(json.loads(success.stdout)["validation"], "public-parameter-metadata")
            self.assertEqual(run("export", "tested.json", "dashboard.json").returncode, 0)
            self.assertEqual(helper.read_json(root / "dashboard.json")["components"],
                             helper.read_json(root / "tested.json")["components"])
            failed = run("export", "draft.json", "invalid.json")
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(json.loads(failed.stderr)["error"]["code"], "INCOMPLETE_TESTED_REQUEST")
            self.assertFalse((root / "invalid.json").exists())
            protected = run("export", "tested.json", "tested.json")
            self.assertEqual(protected.returncode, 1)
            self.assertEqual(json.loads(protected.stderr)["error"]["code"], "OUTPUT_OVERWRITES_INPUT")
            self.assertIn("marketId", helper.read_json(root / "tested.json"))

    def test_json_reader_rejects_ambiguous_or_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for content, code in (("{\"a\": 1, \"a\": 2}", "DUPLICATE_JSON_KEY"),
                                  ("{\"a\": NaN}", "INVALID_JSON_VALUE"),
                                  ("not json", "INVALID_JSON")):
                path.write_text(content, encoding="utf-8")
                self.assert_code(code, lambda: helper.read_json(path))


if __name__ == "__main__":
    unittest.main()
