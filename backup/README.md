# RunLab Prototype

A lightweight end-to-end prototype for analysing running training data using Python, Streamlit, deterministic signals, and an optional AI explanation layer.

## What it does

- Upload running training data as CSV
- Clean and standardise the data
- Calculate weekly metrics
- Generate deterministic signals such as:
  - consistency
  - volume trend
  - threshold work gaps
  - plateau indicators
- Add an optional AI explanation layer

## Expected CSV columns

This prototype works best with the following columns:

- date
- distance_km
- duration_min
- avg_hr
- activity_type
- workout_type

Example workout_type values:
- easy
- threshold
- tempo
- interval
- long

Example activity_type values:
- run
- running
- trail run
- treadmill run

## Setup

1. Create and activate a virtual environment
2. Install dependencies

```bash
pip install -r requirements.txt