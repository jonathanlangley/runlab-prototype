from __future__ import annotations

from textwrap import dedent

import streamlit as st


def render_css() -> None:
    st.markdown(
        dedent(
            """
            <style>

            /* ---------------- App Shell ---------------- */

            html, body, [data-testid="stAppViewContainer"] {
                background: #f7f8fb;
            }

            .block-container {
                width: 100%;
                max-width: 1320px;
                padding-top: 1.75rem;
                padding-bottom: 2.5rem;
            }

            section.main > div {
                max-width: 1320px;
            }

            section[data-testid="stSidebar"] {
                width: 292px !important;
                background: #f3f4f6;
                border-right: 1px solid #e5e7eb;
            }

            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3 {
                color: #111827;
            }

            /* ---------------- Streamlit Controls ---------------- */

            div[data-testid="stRadio"] label {
                font-size: 0.92rem;
            }

            div[data-testid="stSelectbox"] label,
            div[data-testid="stTextInput"] label,
            div[data-testid="stFileUploader"] label {
                font-size: 0.88rem;
                font-weight: 650;
                color: #374151;
            }

            button[kind="secondary"],
            button[kind="primary"] {
                border-radius: 999px !important;
                font-weight: 650 !important;
            }

            /* ---------------- Tabs ---------------- */

            div[data-testid="stTabs"] [data-baseweb="tab-list"] {
                gap: 0.5rem;
                border-bottom: none;
                margin-bottom: 1.15rem;
                flex-wrap: wrap;
            }

            div[data-testid="stTabs"] button {
                border: 1px solid #e5e7eb;
                border-radius: 999px;
                background: rgba(255,255,255,0.82);
                padding: 0.48rem 0.95rem;
                font-weight: 650;
                color: #374151;
                transition: all 0.15s ease-in-out;
            }

            div[data-testid="stTabs"] button:hover {
                background: #ffffff;
                border-color: #cbd5e1;
                color: #111827;
            }

            div[data-testid="stTabs"] button[aria-selected="true"] {
                background: #111827;
                border-color: #111827;
                color: #ffffff;
            }

            div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
                display: none;
            }

            /* ---------------- Cards ---------------- */

            .hero-card,
            .report-card,
            .action-card,
            .metric-card,
            .signal-card,
            .section-card,
            .locked-card,
            .trust-card {
                border: 1px solid rgba(229, 231, 235, 0.95);
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.92);
                padding: 1.15rem;
                margin-bottom: 1rem;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            }

            .hero-card {
                background:
                    radial-gradient(circle at top left, rgba(219, 234, 254, 0.75), transparent 32%),
                    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                padding: 1.55rem;
                border-color: #dbeafe;
            }

            .action-card {
                background: linear-gradient(180deg, #ecfdf5 0%, #ffffff 100%);
                border-color: #a7f3d0;
            }

            .locked-card {
                background: linear-gradient(180deg, #fffbeb 0%, #ffffff 100%);
                border-color: #fcd34d;
            }

            .section-card {
                background: #ffffff;
            }

            /* ---------------- Typography ---------------- */

            h1 {
                letter-spacing: -0.035em;
            }

            .kicker {
                font-size: 0.73rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #64748b;
                font-weight: 800;
                margin-bottom: 0.42rem;
            }

            .hero-title {
                font-size: 1.85rem;
                line-height: 1.15;
                font-weight: 850;
                color: #0f172a;
                letter-spacing: -0.035em;
                margin-bottom: 0.55rem;
            }

            .section-title {
                font-size: 1.05rem;
                font-weight: 780;
                color: #0f172a;
                letter-spacing: -0.015em;
                margin-bottom: 0.65rem;
            }

            .body-copy {
                font-size: 0.98rem;
                line-height: 1.58;
                color: #334155;
                margin-bottom: 0.8rem;
            }

            .small-note {
                font-size: 0.88rem;
                color: #64748b;
                line-height: 1.48;
            }

            /* ---------------- Support Boxes ---------------- */

            .step-box,
            .why-box,
            .support-box {
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                padding: 0.86rem 0.95rem;
                margin-bottom: 0.65rem;
                color: #334155;
                line-height: 1.48;
                background: #ffffff;
            }

            .step-box {
                border-color: #86efac;
                background: #f0fdf4;
                font-weight: 650;
                color: #065f46;
            }

            .why-box,
            .support-box {
                background: #f8fafc;
            }

            /* ---------------- Metrics ---------------- */

            .metric-card {
                background: #ffffff;
                padding: 1rem;
            }

            .metric-label {
                font-size: 0.72rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #64748b;
                font-weight: 760;
                margin-bottom: 0.32rem;
            }

            .metric-value {
                font-size: 1.05rem;
                color: #0f172a;
                font-weight: 760;
                letter-spacing: -0.015em;
            }

            /* ---------------- Pills and Badges ---------------- */

            .status-pill {
                display: inline-block;
                border: 1px solid #bfdbfe;
                background: #eff6ff;
                color: #1d4ed8;
                border-radius: 999px;
                padding: 0.25rem 0.68rem;
                font-size: 0.75rem;
                font-weight: 760;
                margin-bottom: 0.85rem;
            }

            /* ---------------- Flow ---------------- */

            .flow-strip {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 0.45rem;
                border: 1px solid #dbeafe;
                border-radius: 999px;
                background: #eff6ff;
                color: #1d4ed8;
                padding: 0.58rem 0.82rem;
                margin: 0.8rem 0 1.05rem 0;
                font-size: 0.88rem;
                font-weight: 760;
            }

            .flow-card {
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                background: #ffffff;
                padding: 0.95rem;
                min-height: 132px;
                margin-bottom: 0.75rem;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.035);
            }

            .flow-card.compact {
                min-height: 112px;
            }

            .flow-step {
                font-size: 0.72rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #2563eb;
                font-weight: 820;
                margin-bottom: 0.38rem;
            }

            .flow-title {
                font-size: 1rem;
                font-weight: 800;
                color: #0f172a;
                letter-spacing: -0.015em;
                margin-bottom: 0.35rem;
            }

            /* ---------------- Future Features ---------------- */

            .coming-soon-item {
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                padding: 0.78rem 0.9rem;
                background: #ffffff;
                color: #334155;
                margin-bottom: 0.6rem;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.035);
            }

            .trust-card {
                border-color: #bfdbfe;
                background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
            }

            /* ---------------- Tables and Expanders ---------------- */

            div[data-testid="stExpander"] {
                border-radius: 16px;
                overflow: hidden;
                border-color: #e5e7eb;
                background: #ffffff;
            }

            div[data-testid="stDataFrame"] {
                border-radius: 14px;
                overflow: hidden;
            }

            /* ---------------- Mobile ---------------- */

            @media (max-width: 640px) {

                .block-container {
                    padding-top: 1rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }

                .hero-title {
                    font-size: 1.38rem;
                }

                .hero-card,
                .report-card,
                .action-card,
                .metric-card,
                .signal-card,
                .section-card,
                .locked-card,
                .trust-card {
                    border-radius: 16px;
                    padding: 1rem;
                }

                .flow-strip {
                    border-radius: 16px;
                    align-items: flex-start;
                }

                .flow-card,
                .flow-card.compact {
                    min-height: auto;
                }

                section[data-testid="stSidebar"] {
                    width: 100% !important;
                }
            }

            </style>
            """
        ),
        unsafe_allow_html=True,
    )
