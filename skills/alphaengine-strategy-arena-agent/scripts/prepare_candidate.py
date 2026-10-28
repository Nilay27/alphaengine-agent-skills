#!/usr/bin/env python3
"""Prepare complete public API inputs or export an already complete tested input.

Offline, standard-library only. This checks public metadata, not private codecs,
cross-parameter strategy rules, scoring, authentication or submission acceptance.
"""

import argparse
import copy
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
import sys


class CandidateError(ValueError):
    """Stable local error code and field path; never parse exception messages."""

    def __init__(self, code, path):
        self.code = code
        self.path = path
        super().__init__(code)


def require(condition, code, path):
    if not condition:
        raise CandidateError(code, path)


def numeric(value):
    return type(value) in (int, float) and (
        type(value) is int or math.isfinite(value)
    )


def json_text(value):
    try:
        return json.dumps(value, sort_keys=True, allow_nan=False, indent=2) + "\n"
    except (ValueError, TypeError, OverflowError) as error:
        raise CandidateError("INVALID_JSON_VALUE", "$") from error


def response_data(value, path):
    if isinstance(value, dict):
        require(value.get("status") == "ok", "INVALID_RESPONSE", path)
        return value.get("data")
    return value


def complete_params(params, response, path):
    require(isinstance(params, dict), "INVALID_PARAMETERS", path)
    schema = response_data(response, path + ".schema")
    require(isinstance(schema, list), "INVALID_SCHEMA", path)
    definitions = {}
    for definition in schema:
        require(isinstance(definition, dict), "INVALID_SCHEMA", path)
        key = definition.get("key")
        require(isinstance(key, str) and bool(key), "INVALID_SCHEMA", path)
        require(key not in definitions, "DUPLICATE_SCHEMA_KEY", path + "." + key)
        definitions[key] = definition
    require(not (params.keys() - definitions.keys()), "UNKNOWN_PARAMETER", path)
    result = {}
    for key, definition in definitions.items():
        field = path + "." + key
        kind = definition.get("type")
        require(kind in ("integer", "number", "string"), "UNSUPPORTED_SCHEMA_TYPE", field)
        require(type(definition.get("required")) is bool, "INVALID_SCHEMA", field)
        constraints = definition.get("constraints")
        require(isinstance(constraints, dict), "INVALID_SCHEMA", field)
        require(
            not (constraints.keys() - {"min", "max", "enum"}),
            "UNSUPPORTED_SCHEMA_CONSTRAINT", field,
        )
        for bound in ("min", "max"):
            if bound in constraints:
                require(kind != "string" and numeric(constraints[bound]), "INVALID_SCHEMA", field)
        if "min" in constraints and "max" in constraints:
            require(constraints["min"] <= constraints["max"], "INVALID_SCHEMA", field)
        if "enum" in constraints:
            choices = constraints["enum"]
            require(
                kind == "string" and isinstance(choices, list)
                and all(isinstance(choice, str) for choice in choices),
                "INVALID_SCHEMA", field,
            )
        if key in params:
            value = params[key]
        else:
            require("defaultValue" in definition, "MISSING_PARAMETER", field)
            value = definition["defaultValue"]
        if kind == "integer":
            require(type(value) is int, "INVALID_PARAMETER_TYPE", field)
        elif kind == "number":
            require(numeric(value), "INVALID_PARAMETER_TYPE", field)
        else:
            require(isinstance(value, str), "INVALID_PARAMETER_TYPE", field)
        if "min" in constraints:
            require(value >= constraints["min"], "PARAMETER_OUT_OF_RANGE", field)
        if "max" in constraints:
            require(value <= constraints["max"], "PARAMETER_OUT_OF_RANGE", field)
        if "enum" in constraints:
            require(value in constraints["enum"], "INVALID_PARAMETER_ENUM", field)
        result[key] = value
    return result


def prepare_candidate(candidate, schemas, markets):
    json_text(candidate)  # Reject non-finite values even in retained optional settings.
    require(isinstance(candidate, dict), "INVALID_CANDIDATE", "$")
    require(isinstance(schemas, dict), "INVALID_SCHEMA", "schemas")
    market_id = candidate.get("marketId")
    require(type(market_id) is int, "INVALID_MARKET", "marketId")
    catalog = response_data(markets, "markets")
    require(
        isinstance(catalog, list) and all(isinstance(market, dict) for market in catalog),
        "INVALID_MARKET_CATALOG", "markets",
    )
    matches = [market for market in catalog if market.get("marketId") == market_id]
    require(len(matches) == 1, "MARKET_NOT_UNIQUE", "marketId")
    market = matches[0]
    require(
        isinstance(market.get("marketKey"), str) and bool(market["marketKey"]),
        "INVALID_MARKET_CATALOG", "marketKey",
    )
    require(candidate.get("timeframe") in ("hourly", "daily"), "INVALID_TIMEFRAME", "timeframe")
    capital = candidate.get("capital")
    require(isinstance(capital, str), "INVALID_CAPITAL", "capital")
    try:
        amount = Decimal(capital)
    except InvalidOperation as error:
        raise CandidateError("INVALID_CAPITAL", "capital") from error
    require(amount.is_finite() and amount > 0, "INVALID_CAPITAL", "capital")
    components = candidate.get("components")
    require(isinstance(components, list) and bool(components), "INVALID_COMPONENTS", "components")
    prepared = copy.deepcopy(candidate)
    total_weight = 0
    for index, component in enumerate(prepared["components"]):
        path = "components[" + str(index) + "]"
        require(isinstance(component, dict), "INVALID_COMPONENT", path)
        strategy_id = component.get("strategyId")
        require(isinstance(strategy_id, str) and strategy_id in schemas, "MISSING_SCHEMA", path)
        weight = component.get("weightBps")
        require(type(weight) is int and 0 < weight <= 10000, "INVALID_WEIGHT", path + ".weightBps")
        total_weight += weight
        component["strategyParams"] = complete_params(
            component.get("strategyParams"), schemas[strategy_id], path + ".strategyParams",
        )
    require(total_weight == 10000, "INVALID_WEIGHT_TOTAL", "components")
    return prepared, market


def dashboard_candidate(tested_request, schemas, markets):
    prepared, market = prepare_candidate(tested_request, schemas, markets)
    # Export must not introduce defaults after testing or discard request-only
    # component settings that the dashboard shape cannot faithfully reproduce.
    require(prepared == tested_request, "INCOMPLETE_TESTED_REQUEST", "components")
    for component in prepared["components"]:
        require(
            set(component) == {"strategyId", "strategyParams", "weightBps"},
            "UNSUPPORTED_DASHBOARD_COMPONENT", "components",
        )
    return {
        "marketKey": market["marketKey"],
        "timeframe": prepared["timeframe"],
        "components": prepared["components"],
    }


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "DUPLICATE_JSON_KEY", str(path))
            result[key] = value
        return result

    def constant(_value):
        raise CandidateError("INVALID_JSON_VALUE", str(path))

    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise CandidateError("INVALID_JSON", str(path)) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "export"))
    parser.add_argument("--candidate", type=Path, required=True, help="Draft or saved tested API request")
    parser.add_argument("--schemas", type=Path, required=True, help="Map strategy IDs to cached /parameters responses")
    parser.add_argument("--markets", type=Path, required=True, help="Cached router /markets response")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        require(
            args.output.resolve() not in {
                path.resolve() for path in (args.candidate, args.schemas, args.markets)
            },
            "OUTPUT_OVERWRITES_INPUT", "output",
        )
        candidate, schemas, markets = (read_json(path) for path in (args.candidate, args.schemas, args.markets))
        if args.mode == "prepare":
            output, _market = prepare_candidate(candidate, schemas, markets)
        else:
            output = dashboard_candidate(candidate, schemas, markets)
        args.output.write_text(json_text(output), encoding="utf-8")
    except CandidateError as error:
        print(json.dumps({"status": "error", "error": {"code": error.code, "path": error.path}}), file=sys.stderr)
        return 1
    except OSError:
        print(json.dumps({"status": "error", "error": {"code": "FILE_IO_ERROR"}}), file=sys.stderr)
        return 1
    print(json.dumps({"status": "ok", "validation": "public-parameter-metadata", "mode": args.mode}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
