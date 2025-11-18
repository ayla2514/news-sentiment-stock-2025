import argparse, sys, json, time
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import requests


def ymd_to_gdelt(dt_str):
    # '2025-01-01' -> '20250101000000'
    return datetime.strptime(dt_str, "%Y-%m-%d").strftime("%Y%m%d%H%M%S")

def fetch_gdelt_docs(query, start, end, maxrecords=250):
    # Doc API: https://api.gdeltproject.org/api/v2/doc/doc
    url = (
        "https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query={quote_plus(query)}"
        f"&mode=ArtList&format=json&maxrecords={maxrecords}"
        f"&startdatetime={ymd_to_gdelt(start)}"
        f"&enddatetime={ymd_to_gdelt(end)}"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help='예: "Tesla OR TSLA"')
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--out", required=True, help="저장 경로 .json")
    ap.add_argument("--maxrecords", type=int, default=250)
    args = ap.parse_args()

    data = fetch_gdelt_docs(args.query, args.start, args.end, args.maxrecords)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] saved -> {args.out}")

if __name__ == "__main__":
    sys.exit(main())