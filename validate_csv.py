#!/usr/bin/env python3
import sys, argparse, pandas as pd

REQUIRED_MIN = ["uid", "time_iso"]
RECOMMENDED  = ["pm25","pm10","o3","no2","so2","co","temp","humidity","wind","pressure","aqi"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--mode", choices=["strict","soft"], default="soft")
    args = ap.parse_args()

    try:
        df = pd.read_csv(args.path)
    except Exception as e:
        print(f"❌ Cannot read CSV: {e}")
        sys.exit(1 if args.mode=='strict' else 0)

    if df.empty:
        msg = "CSV is empty"
        print(("❌ "+msg) if args.mode=='strict' else ("⚠ "+msg))
        sys.exit(1 if args.mode=='strict' else 0)

    missing_min = [c for c in REQUIRED_MIN if c not in df.columns]
    if missing_min:
        msg = f"Missing required minimal columns: {missing_min}"
        print(("❌ "+msg) if args.mode=='strict' else ("⚠ "+msg))
        sys.exit(1 if args.mode=='strict' else 0)

    missing_rec = [c for c in RECOMMENDED if c not in df.columns]
    if missing_rec:
        print(f"⚠ Recommended columns missing: {missing_rec}")

    if "time" in df.columns and df["time"].isna().sum() > 0:
        print("⚠ 'time' contains NaN values")

    print(f"✅ CSV validation passed (mode: {args.mode})")
    sys.exit(0)

if __name__ == "__main__":
    main()
