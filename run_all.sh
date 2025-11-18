#!/usr/bin/env bash
set -e

START="2025-01-01"
END="2025-11-17"

echo "[1/4] Installing dependencies"
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon

echo "[2/4] Fetching stock prices"
python src/fetch_prices_yfinance.py --tickers TSLA F --start ${START} --end ${END}

echo "[3/4] Fetching news from GDELT"
python src/fetch_news_gdelt.py --query "Tesla OR TSLA" --start ${START} --end ${END} --out data/raw/news_tsla_2025.json
python src/fetch_news_gdelt.py --query "Ford OR F" --start ${START} --end ${END} --out data/raw/news_ford_2025.json

echo "[4/4] Running pipeline (align + correlation + plots)"
python run_pipeline.py \
  --prices data/raw/prices.csv \
  --tsla_news data/raw/news_tsla_2025.json \
  --f_news data/raw/news_ford_2025.json \
  --figs_dir figures \
  --out_csv reports/key_results.csv

echo "✅ Done! Check 'figures/' and 'reports/key_results.csv'"
