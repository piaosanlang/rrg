# 📊 Relative Rotation Graph (RRG) – Automated Sector Rotation Tool

This project is a **fully automated Relative Rotation Graph (RRG)** built to track **sector rotation in the US equity market** using a Python data pipeline and a lightweight web app.

It provides a **daily-updated visual of sector strength and momentum**, helping identify where capital is flowing — and where it’s going next.

---

# 🚀 What This Does

This system automatically:

1. Pulls market data (daily)
2. Computes Relative Strength (RS) and Momentum
3. Builds RRG-compatible data
4. Updates JSON data files
5. Rebuilds the frontend app
6. Deploys to GitHub Pages

👉 No manual work required.

---

# 🔁 Automation Flow

### ⏰ Runs automatically every weekday:
- **Time:** 4:15 PM PST (after market close)

### ⚙️ Pipeline:

Python (yfinance)
↓
Generate RS + Momentum
↓
Update JSON files
↓
Commit to repo
↓
Build frontend (Vite)
↓
Deploy via GitHub Pages


---

# 📁 Key Files

### Data
- `public/raw-data.json` → Raw price data
- `public/rrg-data.json` → Processed RRG data (used by app)

### Script
- `scripts/update_rrg.py` → Fetches data + computes RS/Momentum

### Frontend
- Built using Vite
- Outputs to `/dist` for deployment

### Workflow
- `.github/workflows/update-data.yml`
  - Handles data update + build + deploy

---

# 🌐 Live App

👉 https://friedjalapeno.github.io/rrg/

---

# 📈 What the Chart Shows

Each sector ETF (SPDR):

- XLK – Technology  
- XLF – Financials  
- XLE – Energy  
- XLI – Industrials  
- XLB – Materials  
- XLU – Utilities  
- XLP – Staples  
- XLY – Discretionary  
- XLV – Healthcare  
- XLRE – Real Estate  
- XLC – Communication  

---

# 🧭 Quadrants Explained

| Quadrant     | Meaning |
|--------------|--------|
| 🟢 Leading    | Strong RS + rising momentum |
| 🟡 Weakening  | Strong RS, but losing momentum |
| 🔴 Lagging    | Weak RS + weak momentum |
| 🔵 Improving  | Weak RS, but gaining momentum |

---

# 🧠 How to Use This

This tool is designed for **top-down analysis**:

### Step 1: Identify sector rotation
- Watch sectors moving from:
  - **Improving → Leading**

### Step 2: Focus your trades
- Only scan stocks inside:
  - Leading sectors
  - Improving sectors (early moves)

### Step 3: Execute using your strategy
- Supply/Demand
- Structure
- Momentum confirmation

---

# ⚠️ Notes

- Data is based on **weekly aggregation**
- Updated once per trading day
- Uses `yfinance` (subject to occasional API hiccups)
- If a workflow fails, last successful data remains live

---

# 🛠️ Tech Stack

- Python (yfinance, pandas)
- GitHub Actions (automation)
- Vite (frontend build)
- GitHub Pages (hosting)

---

# 🔮 Future Improvements

- Alerts for quadrant transitions
- Sector ranking / scoring
- Stock-level scanner integration
- Momentum velocity tracking
- Intraday update option

---

# 💡 Why This Matters

Most traders react to price.

This tool helps you:

👉 Track **where money is rotating BEFORE the move fully develops**

It’s not about predicting —  
it’s about positioning early.

---

# ⚠️ Disclaimer

This project is for **educational and informational purposes only**.

It does not constitute financial advice, investment recommendations, or a solicitation to buy or sell any securities.

All market data is sourced from third-party providers and may be delayed or inaccurate. Always do your own research and consult with a qualified financial professional before making investment decisions.

Use at your own risk.
