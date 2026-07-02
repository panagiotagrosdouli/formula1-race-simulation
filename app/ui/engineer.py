"""AI race engineer command-center components."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        converted = pd.to_numeric(value, errors="coerce")
        if pd.isna(converted):
            return default
        return float(converted)
    except Exception:
        return default


def _bar(label: str, value: float, detail: str) -> str:
    pct = max(0, min(100, value))
    return f"""
    <div class="f1-engineer-row">
        <div class="f1-engineer-row-top">
            <span>{html.escape(label)}</span>
            <strong>{pct:.0f}%</strong>
        </div>
        <div class="f1-engineer-track"><div class="f1-engineer-fill" style="width:{pct:.0f}%"></div></div>
        <div class="f1-engineer-detail">{html.escape(detail)}</div>
    </div>
    """


def render_ai_engineer_console(
    lap: int,
    total_laps: int,
    leader: str,
    grip: str,
    rain_probability: float,
    pit_loss: float,
    lap_alerts: pd.DataFrame,
    lap_radio: pd.DataFrame,
) -> None:
    """Render a premium AI race engineer command console.

    This component does not claim to be a real race engineer. It summarizes the
    current simulated race state and exposes the assumptions behind the advice.
    """

    race_progress = (lap / max(total_laps, 1)) * 100
    weather_risk = rain_probability * 100
    traffic_risk = min(100.0, len(lap_alerts) * 18.0)
    strategy_pressure = min(100.0, max(10.0, race_progress * 0.55 + weather_risk * 0.25 + pit_loss))

    if weather_risk >= 55:
        recommendation = "Keep strategy flexible — weather volatility is high."
        call = "WAIT FOR WEATHER"
    elif strategy_pressure >= 62:
        recommendation = "Prepare the pit wall for an undercut or tyre-life decision window."
        call = "PREPARE BOX WINDOW"
    elif traffic_risk >= 30:
        recommendation = "Monitor DRS trains and avoid stopping into traffic."
        call = "WATCH TRAFFIC"
    else:
        recommendation = "Current race state is stable. Extend the stint unless degradation spikes."
        call = "HOLD STRATEGY"

    radio_note = "No radio message on this lap."
    if not lap_radio.empty:
        first = lap_radio.iloc[0]
        radio_note = f"{first.get('Driver', 'Radio')}: {first.get('Message', '')}"

    alerts_note = "No active DRS/overtake alert."
    if not lap_alerts.empty:
        first_alert = lap_alerts.iloc[0]
        alerts_note = str(first_alert.get("Message", "Active race alert."))

    st.markdown(
        f"""
        <div class="f1-ai-console">
            <div class="f1-ai-console-head">
                <div>
                    <div class="f1-label">AI Race Engineer</div>
                    <h3>{html.escape(call)}</h3>
                    <p>{html.escape(recommendation)}</p>
                </div>
                <div class="f1-ai-status">LIVE SIM</div>
            </div>
            <div class="f1-ai-grid">
                <div class="f1-ai-mini"><span>Lap</span><strong>{lap}/{total_laps}</strong></div>
                <div class="f1-ai-mini"><span>Leader</span><strong>{html.escape(str(leader))}</strong></div>
                <div class="f1-ai-mini"><span>Grip</span><strong>{html.escape(str(grip))}</strong></div>
                <div class="f1-ai-mini"><span>Pit Loss</span><strong>{pit_loss:.1f}s</strong></div>
            </div>
            {_bar('Race progress', race_progress, 'How far the simulation has progressed.')}
            {_bar('Weather risk', weather_risk, 'Rain probability drives strategy volatility.')}
            {_bar('Traffic / DRS pressure', traffic_risk, alerts_note)}
            {_bar('Strategy pressure', strategy_pressure, 'Higher values suggest closer pit-wall attention.')}
            <div class="f1-ai-radio"><b>Team radio context</b><br>{html.escape(radio_note)}</div>
            <div class="f1-ai-disclaimer">Decision-support only. This is a simulation summary, not a guarantee.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
