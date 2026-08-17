# RainFall — India environmental intelligence

A proactive dashboard for Indian districts. It answers four questions from live data and local models, then explains the numbers in English, Hindi, or Bengali.

1. **What is happening?** — current weather, soil, ET₀  
2. **Why is it happening?** — anomalies vs NASA POWER climatology + IMD warnings  
3. **What is likely next?** — 3-day rain / discharge  
4. **What should we do now?** — irrigation, flood, heat, drought actions  

The LLM (**Ollama `qwen2.5`**) never computes forecasts, risk scores, or liters saved. It only narrates tool JSON. Questions in any language are translated to English before the model; the English draft is translated back to Hindi, Bengali, or the user's language. Numbers and source names are locked.

## What is live today (no keys)

| Source | Role |
|---|---|
| **IMD CAP** (`cap-sources.s3.amazonaws.com/in-imd-en/rss.xml`) | Official India Meteorological Department warnings |
| **Open-Meteo** | Hourly/daily weather, soil moisture, ET₀, GloFAS flood, air quality |
| **NASA POWER** | 16-day agromet climatology for anomalies |
| **Local ML** | Weighted XAI risk cards + irrigation liter math |
| **Ollama qwen2.5** | English briefing (optional; templates still work if Ollama is down) |

### IMD REST (`api.imd.gov.in`)

The documented JSON API currently returns **401 Unauthorized** unless your IP is [whitelisted](https://api.imd.gov.in/public/index.php). The app already contains an IMD REST client. After whitelist (or if you receive a key), set `IMD_API_KEY` in `backend/.env`. Until then the official **CAP alert feed** is used for warnings and Open-Meteo fills quantitative forecast/soil.

## Keys you can inject later

Copy `backend/.env.example` → `backend/.env`.

| Variable | Unlocks |
|---|---|
| `AIKOSH_API_KEY` | AIKosh datasets (Kisan Call Centre, agro-climatic zones) |
| `DATA_GOV_IN_API_KEY` | data.gov.in — live CPCB NAQI + Agmarknet mandi (set in local `.env`; not committed) |
| `IMD_API_KEY` | Official IMD station/district JSON after whitelist |
| `MOSDAC_*` / `NASA_EARTHDATA_*` | True satellite soil / NDVI |

## Hardware (this laptop)

Designed for **16 GB RAM + RTX 3060 6 GB**. Use the already-installed `qwen2.5` model. Do **not** load Mixtral or a second large model next to it.

```
ollama serve
# qwen2.5 is already pulled
```

## Run

```powershell
# backend
cd backend
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000

# frontend (other terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — light **neumorphic** UI with tabs: Overview, Map (square, layers, nearby), Forecast (plots + 7-day outlook + compare), XAI Risks, Market, Advisor (LLM tool agent).

### Tests

```powershell
cd backend
python -m pytest -q
```

## Ask this in the chat dock (Bengali)

> আগামী তিন দিনে আমার এলাকায় বৃষ্টির সম্ভাবনা কেমন? এখন সেচ দেওয়া উচিত কি?

The dashboard should update rainfall, flood XAI factors, and a “do not irrigate” action with an 800–1200 L band when rain is coming.
