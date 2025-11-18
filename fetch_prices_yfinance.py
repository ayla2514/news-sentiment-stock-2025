import argparse, sys
from datetime import datetime
import pandas as pd
import yfinance as yf

def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--tickers", nargs="+", required=True, help="예: TSLA F GM TM")
    p.add_argument("--start", type=str, required=True, help="YYYY-MM-DD")
    p.add_argument("--end", type=str, required=True, help="YYYY-MM-DD")
    p.add_argument("--out", type=str, default="data/raw/prices.csv")
    return p.parse_args()

def main():
    args = parse()
    start = args.start
    end = args.end
    tickers = args.tickers
    df = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    # 멀티컬럼(Adj Close 등)에서 'Close'만 선택
    if isinstance(df.columns, pd.MultiIndex):
        close = df["Close"].copy()
    else:
        close = df[["Close"]].copy()
    close.columns = [c if isinstance(c, str) else c[0] for c in close.columns]
    close.reset_index().to_csv(args.out, index=False)
    print(f"[OK] saved -> {args.out}  (shape={close.shape})")

if __name__ == "__main__":
    sys.exit(main())