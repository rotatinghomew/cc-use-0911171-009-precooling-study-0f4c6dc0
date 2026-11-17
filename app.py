import argparse
import json
from pathlib import Path
from records import load, save


def inspect(data, as_of):
    from enrollment import enrollment
    from outcomes import descriptive
    from economics import ledger
    from transfers import observed_balances
    return {"observed_balances": observed_balances(data, as_of), "paid_records": data["paid_records"], "farms": len(enrollment(data, as_of)), "descriptive": descriptive(data, as_of),
            "cost_c1": ledger(data, as_of, "c1")[:8], "cost_c2": ledger(data, as_of, "c2")[:8]}



def main():
    parser = argparse.ArgumentParser(description="预冷批次分段交接、售后重量和经济账核对。")
    parser.add_argument("action", choices=["demo", "inspect"])
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "fixtures/data.json")
    parser.add_argument("--as-of", default="2026-11-01")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect(load(args.data), args.as_of)
    if args.output:
        save(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
