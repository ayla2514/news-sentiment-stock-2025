# news-sentiment-stock-2025

Linking GDELT news sentiment to next-day returns in auto stocks (TSLA vs F, 2025).
*Does news sentiment predict next‑day returns in autos? A comparative study of **Tesla (TSLA)** vs **Ford (F)** in 2025.*

## TL;DR
- **Problem** — Quantify whether daily news sentiment is associated with **next‑day stock returns**.
- **Approach** — Collect news via **GDELT**, score headlines with **VADER**, align with **Yahoo Finance** prices, evaluate **lag‑1 correlations/OLS**.
- **Result (to fill)** — corr(sent_roll3, next‑day return): **TSLA {X}**, **F {Y}**; OLS β: **TSLA {β_TSLA}**, **F {β_F}**.

## Data & Scope
- **Tickers**: TSLA (EV), F (Legacy)
- **Period**: 2025‑01‑01 → 2025‑11‑17 (America/Los_Angeles)
- **News**: GDELT Doc 2.0 (headline text)
- **Prices**: Yahoo Finance (adjusted close)
- **Language**: English

## How to Reproduce
```bash
# 0) Environment
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon

# 1) Prices
python src/fetch_prices_yfinance.py --tickers TSLA F --start 2025-01-01 --end 2025-11-17

# 2) News (GDELT)
python src/fetch_news_gdelt.py --query "Tesla OR TSLA" --start 2025-01-01 --end 2025-11-17 --out data/raw/news_tsla_2025.json
python src/fetch_news_gdelt.py --query "Ford OR F"   --start 2025-01-01 --end 2025-11-17 --out data/raw/news_ford_2025.json

# 3) Align & Analyze (Notebook)
# open notebooks/02_sentiment_align.ipynb and run all
```

## Methods (Brief)
- **Sentiment**: VADER *compound*; daily mean; 3‑day rolling mean.
- **Alignment**: sentiment(t) → return(t+1), also test lags/leads.
- **Stats**: Pearson correlation; OLS slope (β); optional Granger causality; robustness by window/filters.
- **Caveats**: simultaneity, news source bias, time‑zone alignment, survivorship bias, transaction costs ignored.

## Repository Structure
```
.
├─ README.md
├─ requirements.txt
├─ src/
│  ├─ fetch_prices_yfinance.py
│  └─ fetch_news_gdelt.py
├─ notebooks/
│  └─ 02_sentiment_align.ipynb
├─ data/
│  ├─ raw/          # (gitignored)
│  └─ processed/    # (gitignored)
├─ figures/
└─ reports/
```

## Key Results (as of Nov 2025)

| Ticker | Corr(Sentiment vs Next-Day Return) | β (OLS) | Intercept |
|---------|-------------------------------------|----------|------------|
| **TSLA** | -1.00 | -0.184 | 0.0117 |
| **F** | -0.70 | -0.018 | 0.0057 |

**Interpretation:**  
- Tesla shows a *strong negative* correlation between daily sentiment and next-day stock returns.  
- Ford shows a *moderate negative* relationship, implying sentiment had limited predictive power.  
- Across both firms, sentiment seems to act as a **contrarian signal** rather than a leading indicator.

### Figures
![TSLA Sentiment vs Return](figures/tsla_timeseries.png)
![TSLA Scatter](figures/tsla_scatter.png)
![Ford Sentiment vs Return](figures/f_timeseries.png)
![Ford Scatter](figures/f_scatter.png)
## Next Steps
- Event study on earnings/recalls/policy days (±5 trading days)
- Finance‑domain sentiment (FinBERT/FinVADER) comparison
- Expand tickers: GM, TM, RIVN, NIO

## Attribution
- News — GDELT Project
- Prices — Yahoo Finance via `yfinance`
- Sentiment — NLTK VADER

## License
MIT © Ayla Lee aylee2514@ucla.edu 
