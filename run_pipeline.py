import argparse, json, sys, os
from datetime import datetime
import pandas as pd, numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def load_gdelt_articles(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    arts = data.get("articles") or data.get("documents") or data.get("artList") or []
    analyzer = SentimentIntensityAnalyzer()
    rows = []
    for a in arts:
        title = a.get("title") or a.get("DocumentTitle") or ""
        date_str = a.get("seendate") or a.get("date") or a.get("SQLDATE")
        if not title or not date_str:
            continue
        try:
            dt = pd.to_datetime(date_str).date()
        except Exception:
            continue
        score = analyzer.polarity_scores(title)["compound"]
        rows.append({"date": dt, "title": title, "sentiment": score})
    return pd.DataFrame(rows)

def daily_sentiment(df):
    if df.empty:
        return pd.DataFrame(columns=["date","sentiment","sent_roll3"])
    daily = df.groupby("date")["sentiment"].mean().reset_index()
    daily["sent_roll3"] = daily["sentiment"].rolling(3, min_periods=1).mean()
    return daily

def load_prices(prices_csv):
    df = pd.read_csv(prices_csv, parse_dates=["Date"])
    df = df.rename(columns={"Date":"date"}).set_index("date")
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"].copy()
        df.columns = [c if isinstance(c, str) else c[0] for c in df.columns]
    return df

def compute_returns(df):
    ret = df.pct_change().dropna()
    ret = ret.stack().rename("ret").reset_index().rename(columns={"level_1":"ticker"})
    return ret

def align_and_analyze(ticker, news_path, prices_path, figs_dir):
    arts = load_gdelt_articles(news_path)
    sent = daily_sentiment(arts)
    prices = load_prices(prices_path)
    ret = compute_returns(prices)
    ret_t = ret[ret["ticker"]==ticker].copy()

    sent["date_t1"] = pd.to_datetime(sent["date"]) + pd.Timedelta(days=1)
    sent_shift = sent.rename(columns={"date_t1":"date"})[["date","sent_roll3"]].copy()
    sent_shift["date"] = pd.to_datetime(sent_shift["date"])
    ret_t["date"] = pd.to_datetime(ret_t["date"])
    merged = pd.merge(ret_t, sent_shift, on="date", how="inner").dropna()

    corr = merged["sent_roll3"].corr(merged["ret"])
    lr = LinearRegression().fit(merged[["sent_roll3"]], merged["ret"])
    beta = float(lr.coef_[0])
    intercept = float(lr.intercept_)

    os.makedirs(figs_dir, exist_ok=True)

    plt.figure()
    plt.plot(merged["date"], merged["sent_roll3"], label="Sentiment (roll-3)")
    plt.plot(merged["date"], merged["ret"], label="Next-Day Return")
    plt.title(f"{ticker}: Sentiment vs Next-Day Return")
    plt.xlabel("Date"); plt.ylabel("Value"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(figs_dir, f"{ticker.lower()}_timeseries.png")); plt.close()

    plt.figure()
    plt.scatter(merged["sent_roll3"], merged["ret"])
    plt.title(f"{ticker}: Sentiment(roll-3) vs Next-Day Return")
    plt.xlabel("Sentiment"); plt.ylabel("Return"); plt.tight_layout()
    plt.savefig(os.path.join(figs_dir, f"{ticker.lower()}_scatter.png")); plt.close()

    return {
        "ticker": ticker,
        "n_obs": len(merged),
        "corr_sent_roll3_ret_t1": float(corr) if corr is not None else None,
        "beta": beta,
        "intercept": intercept
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", default="data/raw/prices.csv")
    ap.add_argument("--tsla_news", default="data/raw/news_tsla_2025.json")
    ap.add_argument("--f_news", default="data/raw/news_ford_2025.json")
    ap.add_argument("--figs_dir", default="figures")
    ap.add_argument("--out_csv", default="reports/key_results.csv")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    results = []
    if os.path.exists(args.tsla_news):
        results.append(align_and_analyze("TSLA", args.tsla_news, args.prices, args.figs_dir))
    if os.path.exists(args.f_news):
        results.append(align_and_analyze("F", args.f_news, args.prices, args.figs_dir))

    pd.DataFrame(results).to_csv(args.out_csv, index=False)
    print(f"[OK] saved key results -> {args.out_csv}")

if __name__ == "__main__":
    sys.exit(main())
