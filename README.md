# SatyaDrishti 👁️

A truth-filtering search engine that prioritizes reliable information during emergencies.

## Tech Stack

**Frontend & Backend:** Python + Streamlit (full-stack web framework)

**Search Algorithm:** TF-IDF with Cosine Similarity (scikit-learn)

**Data Processing:** Pandas, NumPy

## Features

- **Standard Mode** - General search with relevance-based ranking
- **Emergency Mode** - Activated for disaster keywords, prioritizes:
  - High-trust sources (≥0.7 trust score)
  - Fresh/recent information
  - Low sensationalism content
  
## Project Structure

```
SatyaDrishti/
├── app.py                 # Main Streamlit application
├── data.json              # Dataset (180 entries: 90 disaster + 90 non-disaster)
├── requirements.txt       # Python dependencies
└── src/
    ├── data_loader.py     # JSON to DataFrame loader
    ├── search_engine.py   # TF-IDF + Cosine Similarity search
    ├── emergency_detector.py  # Emergency keyword detection
    ├── feedback_loop.py   # User interaction tracking
    ├── styles.py          # CSS styles for UI
    ├── audio_utils.py     # Emergency siren generator
    └── views.py           # UI components
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Search Algorithm

| Mode | Relevance | Freshness | Trust | Sensationalism Penalty |
|------|-----------|-----------|-------|------------------------|
| Standard | 85% | - | 15% | - |
| Emergency | 35% | 30% | 35% | -40% |
