# Supply Chain Analytics — Streamlit App

Interactive analytics application for the APL Logistics supply-chain dataset.

## Dashboard modules

- Revenue & Profit Overview
- Customer Value Dashboard
- Product & Category Performance
- Discount Impact Analyzer
- What-if discount scenarios

## Important

The dataset is **not bundled with the application**. This avoids GitHub/Streamlit repository file-size problems.

When the app starts, upload:

`APL_Logistics_cleaned.csv`

The app validates the required columns before loading the dashboard.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Push only:

- `app.py`
- `requirements.txt`
- `README.md`

to GitHub and deploy the repository using Streamlit Community Cloud.

Do not upload the large CSV to the repository.

## Data note

The supplied dataset has no usable order-date field, so the app does not fabricate monthly revenue or margin trends.

The discount scenario analyzer is an analytical what-if estimate, not a financial forecast.
