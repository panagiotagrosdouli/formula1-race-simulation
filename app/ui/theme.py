"""Base44-inspired F1 product design system for Streamlit.

This module centralizes brand tokens and CSS so the app can move away from
page-level styling and toward a reusable product UI layer.
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class ThemeTokens:
    """Shared visual tokens for the F1 Base44 Elite interface."""

    primary: str = "#e10600"
    primary_dark: str = "#8b0000"
    background: str = "#07080d"
    surface: str = "#111827"
    surface_strong: str = "#151f2e"
    text: str = "#f9fafb"
    muted: str = "#9ca3af"
    border: str = "rgba(255,255,255,.10)"
    grid: str = "rgba(255,255,255,.08)"

    @property
    def palette(self) -> list[str]:
        return [self.primary, "#ff4d4d", "#f97316", "#facc15", "#38bdf8", "#60a5fa", "#a78bfa"]


TOKENS = ThemeTokens()


def base_css(tokens: ThemeTokens = TOKENS) -> str:
    """Return the global CSS used by the product UI."""

    return f"""
<style>
:root {{
  --f1-primary: {tokens.primary};
  --f1-primary-dark: {tokens.primary_dark};
  --f1-bg: {tokens.background};
  --f1-surface: {tokens.surface};
  --f1-surface-strong: {tokens.surface_strong};
  --f1-text: {tokens.text};
  --f1-muted: {tokens.muted};
  --f1-border: {tokens.border};
}}
.stApp {{
  background: radial-gradient(circle at 50% -10%, rgba(225,6,0,.18), transparent 34%),
              linear-gradient(135deg, #030407 0%, var(--f1-bg) 46%, #0c111b 100%);
  color: var(--f1-text);
}}
[data-testid="stHeader"] {{
  background: rgba(7,8,13,.78);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(255,255,255,.06);
}}
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #07080d 0%, #0f172a 100%);
  border-right: 1px solid rgba(225,6,0,.28);
}}
.block-container {{ max-width: 1540px; padding-top: 1.1rem; padding-bottom: 2.4rem; }}
h1,h2,h3 {{ letter-spacing: -.04em; color: #fff; }}
.f1-hero {{
  border: 1px solid rgba(225,6,0,.34);
  border-radius: 30px;
  padding: 30px 34px;
  margin-bottom: 1.05rem;
  background: linear-gradient(135deg, rgba(225,6,0,.20), rgba(17,24,39,.96)),
              radial-gradient(circle at 90% 10%, rgba(225,6,0,.16), transparent 20rem);
  box-shadow: 0 28px 90px rgba(0,0,0,.36), inset 0 1px 0 rgba(255,255,255,.05);
}}
.f1-hero h1 {{ margin:0; font-size: clamp(2.35rem, 4vw, 4.1rem); font-weight: 950; line-height: 1; }}
.f1-hero p {{ margin:.8rem 0 0; color:#d1d5db; max-width:1120px; line-height:1.65; font-size:1.05rem; }}
.f1-badge {{
  display:inline-block; margin:.9rem .4rem 0 0; padding:.38rem .78rem;
  border-radius:999px; background:rgba(225,6,0,.15); border:1px solid rgba(255,100,95,.36);
  color:#fecaca; font-size:.76rem; font-weight:850; letter-spacing:.05em; text-transform:uppercase;
}}
.f1-card, .f1-driver-card {{
  background: linear-gradient(180deg, rgba(21,31,46,.96), rgba(16,23,34,.92));
  border:1px solid var(--f1-border); border-top:2px solid var(--f1-primary);
  border-radius:22px; padding:19px 20px; min-height:124px;
  box-shadow:0 18px 45px rgba(0,0,0,.26), inset 0 1px 0 rgba(255,255,255,.04);
}}
.f1-label {{ color:var(--f1-muted); font-size:.78rem; font-weight:850; letter-spacing:.07em; text-transform:uppercase; }}
.f1-value {{ color:#fff; font-size:2rem; font-weight:950; margin-top:.45rem; line-height:1.05; }}
.f1-sub {{ color:var(--f1-muted); font-size:.88rem; margin-top:.35rem; }}
.f1-panel {{
  border:1px solid var(--f1-border); border-left:4px solid var(--f1-primary); border-radius:20px;
  padding:18px 20px; background:rgba(17,24,39,.78); margin:.75rem 0 1rem;
}}
.f1-panel p {{ color:#d1d5db; line-height:1.58; margin-bottom:0; }}
.f1-feed {{
  background:rgba(16,23,34,.86); border:1px solid var(--f1-border); border-left:3px solid var(--f1-primary);
  border-radius:16px; padding:11px 13px; margin:8px 0; box-shadow:0 14px 34px rgba(0,0,0,.22);
}}
.f1-feed b {{ color:#fecaca; margin-right:.5rem; }}
.f1-prob-row {{ display:flex; gap:.45rem; flex-wrap:wrap; margin-top:.75rem; }}
.f1-prob-pill {{
  padding:.28rem .55rem; border-radius:999px; background:rgba(225,6,0,.14); color:#fecaca;
  border:1px solid rgba(225,6,0,.30); font-size:.78rem; font-weight:800;
}}
.f1-why {{ color:#d1d5db; line-height:1.45; margin-top:.75rem; font-size:.88rem; }}
.f1-ai-console {{
  border:1px solid rgba(225,6,0,.32); border-radius:24px; padding:22px 24px; margin:1rem 0;
  background:linear-gradient(180deg, rgba(21,31,46,.98), rgba(9,13,20,.96));
  box-shadow:0 24px 70px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.05);
}}
.f1-ai-console-head {{ display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; margin-bottom:1rem; }}
.f1-ai-console-head h3 {{ margin:.25rem 0 .4rem; font-size:1.65rem; }}
.f1-ai-console-head p {{ color:#d1d5db; margin:0; line-height:1.5; }}
.f1-ai-status {{ padding:.35rem .7rem; border-radius:999px; border:1px solid rgba(255,100,95,.4); color:#fecaca; font-weight:900; font-size:.74rem; }}
.f1-ai-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.75rem; margin:1rem 0; }}
.f1-ai-mini {{ border:1px solid var(--f1-border); border-radius:16px; padding:.85rem .9rem; background:rgba(16,23,34,.78); }}
.f1-ai-mini span {{ display:block; color:var(--f1-muted); font-size:.72rem; text-transform:uppercase; font-weight:850; letter-spacing:.06em; }}
.f1-ai-mini strong {{ color:#fff; font-size:1.1rem; }}
.f1-engineer-row {{ margin:.9rem 0; }}
.f1-engineer-row-top {{ display:flex; justify-content:space-between; color:#f9fafb; font-weight:850; margin-bottom:.35rem; }}
.f1-engineer-track {{ height:10px; border-radius:999px; background:rgba(255,255,255,.08); overflow:hidden; }}
.f1-engineer-fill {{ height:100%; border-radius:999px; background:linear-gradient(90deg, var(--f1-primary), #ff6b6b); box-shadow:0 0 18px rgba(225,6,0,.42); }}
.f1-engineer-detail {{ color:var(--f1-muted); font-size:.84rem; margin-top:.35rem; }}
.f1-ai-radio {{ margin-top:1rem; border:1px solid var(--f1-border); border-radius:16px; padding:1rem; background:rgba(7,8,13,.44); color:#d1d5db; }}
.f1-ai-radio b {{ color:#fecaca; }}
.f1-ai-disclaimer {{ color:var(--f1-muted); font-size:.8rem; margin-top:.8rem; }}
[data-testid="stDataFrame"] {{ border:1px solid var(--f1-border); border-radius:18px; overflow:hidden; background:rgba(16,23,34,.72); }}
.stButton>button,.stDownloadButton>button {{
  border-radius:999px; border:1px solid rgba(255,100,95,.50);
  background:linear-gradient(135deg,var(--f1-primary),var(--f1-primary-dark)); color:#fff; font-weight:900;
  box-shadow:0 12px 28px rgba(225,6,0,.20);
}}
.stButton>button:hover,.stDownloadButton>button:hover {{ border-color:rgba(255,160,155,.90); filter:brightness(1.08); }}
div[data-baseweb="select"]>div,input,textarea {{
  background-color:rgba(16,23,34,.96)!important; color:var(--f1-text)!important;
  border-color:rgba(255,255,255,.14)!important; border-radius:14px!important;
}}
section[data-testid="stTabs"] button {{ color:#f8fafc!important; font-weight:850!important; }}
.stAlert {{ border-radius:16px; }}
@media (max-width: 760px) {{
  .f1-hero {{ padding: 22px 20px; border-radius: 22px; }}
  .f1-hero h1 {{ font-size: 2.25rem; }}
  .f1-card, .f1-driver-card {{ min-height: auto; }}
  .f1-ai-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
}}
</style>
"""


def inject_theme() -> None:
    """Inject the product CSS into the current Streamlit page."""

    st.markdown(base_css(), unsafe_allow_html=True)
