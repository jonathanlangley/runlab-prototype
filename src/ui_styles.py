from __future__ import annotations

from textwrap import dedent

import streamlit as st


def render_css() -> None:
    st.markdown(
        dedent(
            """
            <style>
            .block-container {
                max-width: 1120px;
                padding-top: 1.5rem;
                padding-bottom: 1.5rem;
            }

            .hero-card,
            .report-card,
            .action-card,
            .metric-card,
            .signal-card,
            .section-card,
            .locked-card {
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                background: #ffffff;
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .hero-card {
                background: #f8fafc;
                padding: 1.25rem;
            }

            .action-card {
                background: #ecfdf5;
                border-color: #a7f3d0;
            }

            .locked-card {
                background: #fffbeb;
                border-color: #fcd34d;
            }

            .kicker {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #6b7280;
                font-weight: 750;
                margin-bottom: 0.35rem;
            }

            .hero-title {
                font-size: 1.65rem;
                line-height: 1.22;
                font-weight: 820;
                color: #111827;
                margin-bottom: 0.45rem;
            }

            .section-title {
                font-size: 1.08rem;
                font-weight: 760;
                color: #111827;
                margin-bottom: 0.65rem;
            }

            .body-copy {
                font-size: 1rem;
                line-height: 1.5;
                color: #374151;
                margin-bottom: 0.75rem;
            }

            .small-note {
                font-size: 0.9rem;
                color: #6b7280;
                line-height: 1.45;
            }

            .step-box,
            .why-box,
            .support-box {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 0.82rem 0.9rem;
                margin-bottom: 0.6rem;
                color: #374151;
                line-height: 1.45;
                background: #ffffff;
            }

            .step-box {
                border-color: #a7f3d0;
                background: rgba(255,255,255,0.96);
                font-weight: 650;
                color: #064e3b;
            }

            .support-box {
                background: #f9fafb;
            }

            .metric-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                color: #6b7280;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }

            .metric-value {
                font-size: 1rem;
                color: #111827;
                font-weight: 650;
            }

            .status-pill {
                display: inline-block;
                border: 1px solid #dbeafe;
                background: #eff6ff;
                color: #1d4ed8;
                border-radius: 999px;
                padding: 0.22rem 0.62rem;
                font-size: 0.78rem;
                font-weight: 700;
                margin-bottom: 0.75rem;
            }

            .flow-card {
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                background: #ffffff;
                padding: 0.9rem;
                min-height: 140px;
                margin-bottom: 0.7rem;
            }

            .flow-step {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #2563eb;
                font-weight: 800;
                margin-bottom: 0.35rem;
            }

            .flow-title {
                font-size: 1rem;
                font-weight: 780;
                color: #111827;
                margin-bottom: 0.35rem;
            }

            .coming-soon-item {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 0.75rem 0.85rem;
                background: #f9fafb;
                color: #374151;
                margin-bottom: 0.55rem;
            }

            .trust-card {
                border: 1px solid #bfdbfe;
                border-radius: 16px;
                background: #eff6ff;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )
