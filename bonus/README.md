# Bonus

Extra material beyond the nine core modules. Each topic lives in its **own
subfolder with its own isolated `.venv`**, so their very different dependency
stacks never mix (ML libraries vs. a browser engine vs. the LLM-testing env from
Modules 1–9).

## Contents

| Topic | Folder | What it covers |
|---|---|---|
| **Testing Classical ML Models** | [`ml-model-testing/`](ml-model-testing/) | What ML is, the types of ML, **regression vs classification**, how each is measured (MAE/RMSE/R² · accuracy/precision/recall/F1/confusion matrix), and how ML testing works (train/test split, overfitting, cross-validation, baselines). Pure `scikit-learn`, runs offline. |
| **Browser Testing with Playwright** | [`playwright/`](playwright/) | Driving a real browser to test what users see — locators, auto-waiting, web-first assertions. A live notebook, a `pytest` E2E suite, and a headed "watch-it-run" script. Runs against public demo sites. |

## Setup

Each topic is self-contained — `cd` into it and follow its own `README` / `requirements.txt`:

```bash
cd bonus/<topic>
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

*(More bonus topics will be added here.)*
