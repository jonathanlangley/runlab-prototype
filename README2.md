# RunLab.ai

**Turn your running data into clear training decisions.**

---

## 🧠 What is RunLab?

RunLab is an AI-assisted training analysis tool for self-coached runners.

Instead of showing more charts and metrics, RunLab identifies your **primary training limiter** and tells you **what to do next**.

It is designed for runners who want clarity, not complexity.

---

## 🎯 The Problem

Most running tools focus on data:

* distance
* pace
* heart rate
* training load

But they don’t answer the most important question:

> **What should I change in my training to improve?**

This leaves runners guessing, overtraining, or plateauing.

---

## 🚀 The RunLab Approach

RunLab focuses on **decisions, not dashboards**.

Every analysis follows a simple structure:

1. **Your limiter**
2. **Why this is your limiter**
3. **What to do next**
4. **Supporting evidence**
5. **Coach-style explanation**

---

## ⚙️ How it works

RunLab uses a structured pipeline:

```
Data → Metrics → Signals → Decision → AI Explanation
```

* **Metrics**
  Training volume, frequency, session types, trends

* **Signals**
  Consistency, volume progression, intensity balance, structure

* **Decision engine (deterministic)**
  Identifies the primary limiter and next training focus

* **AI explanation layer**
  Explains the decision in a clear, practical, coach-like way
  (AI does NOT make the decision)

---

## 🔍 Signals (under the hood)

RunLab derives structured signals from your training data, including:

* consistency (run frequency)
* weekly volume and trend
* training balance (easy vs quality vs long run)
* threshold and VO2 stimulus
* progression vs plateau patterns

These signals feed into the deterministic decision engine.

---

## 🧩 Example Output

**Limiter:** Aerobic volume
**Why:** Weekly volume is too low to support current intensity
**What to do next:** Increase easy running to 60–70km/week before adding more quality

This replaces guesswork with a clear next step.

---

## 📥 Input Data

RunLab works with running activity data in CSV format.

**Expected columns:**

* date
* distance_km
* duration_min
* avg_hr (optional)
* activity_type
* workout_type

**Example workout types:**

* easy
* threshold
* interval / vo2
* long run

If workout types are missing, RunLab can optionally classify sessions automatically.

---

## 📊 Features

* Upload your own training data (CSV)
* Built-in demo scenarios
* Automatic workout classification (optional)
* Training balance analysis (current vs ideal)
* Weekly structure breakdown
* Primary limiter detection
* Clear next-step recommendations
* Coach-style explanation
* Downloadable PDF report

---

## 🏗️ Tech Stack

* Python
* Streamlit
* Pandas
* Matplotlib
* ReportLab (PDF generation)
* OpenAI (explanation layer only)

---

## 🛠️ Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧪 Current Status

**Stage:** Early prototype / beta

* Functional Streamlit app
* End-to-end analysis pipeline
* Report generation working
* UI and onboarding still evolving

---

## 🔗 Try RunLab

* **Live demo:** https://prototype.runlab.ai
* **Landing page:** https://runlab.ai

---

## 🗺️ Roadmap

* Improve onboarding and first-time user flow
* Strava integration (automated data import)
* Expanded runner personas (beginner → competitive)
* AI-assisted training plan generation
* Calendar-style training log view
* Performance tracking and progression insights

---

## 💡 Philosophy

RunLab is built on a simple principle:

> **More data doesn’t improve performance. Better decisions do.**

The goal is to help runners train with clarity, consistency, and purpose.

---

## 🤝 Feedback

RunLab is currently in beta.

If you’re interested in testing or sharing feedback:
👉 https://runlab.ai/#beta

---

## 📌 Disclaimer

RunLab provides training guidance based on data patterns.
It is not a substitute for medical advice or professional coaching.

---

## 👤 Author

Built by a data analyst and sub-3 marathon runner, combining:

* 20+ years of analytics experience
* 6+ years of marathon training data
* a focus on turning insight into action

---
