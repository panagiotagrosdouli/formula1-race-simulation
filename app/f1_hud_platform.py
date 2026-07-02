import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.ai_presenter import build_full_ai_presentation
from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.driver_profile_dashboard import build_driver_profile, plot_driver_skill_radar, plot_driver_status_animation
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.live_broadcast import (
    build_driver_telemetry_snapshot,
    build_replay_event_stream,
    build_weather_radar,
    detect_drs_and_overtake_alerts,
    estimate_sector_times,
    generate_team_radio,
    generate_tv_commentary,
    plot_driver_telemetry_trace,
    plot_selected_lap_track_map,
    plot_track_map_animation,
    plot_weather_radar,
)
from src.f1predictor.race_director import (
    apply_director_time_penalties,
    build_steward_summary,
    generate_race_director_log,
    plot_race_director_timeline,
)
from src.f1predictor.simulation import lap_by_lap_race_simulation
from src.f1predictor.team_center import build_all_team_profiles, build_team_profile, plot_team_comparison, plot_team_radar
from src.f1predictor.visualization import plot_probabilities


FERRARI_RED = "#e10600"
FERRARI_RED_SOFT = "#ff2d2d"
CARBON_BLACK = "#020203"
PANEL_BG = "#0a0f16"
PANEL_BG_2 = "#111827"
TEXT = "#f8fafc"
MUTED = "#9ca3af"
GRID = "rgba(255,255,255,0.08)"
BORDER = "rgba(225,6,0,0.32)"
PLOT_PALETTE = [FERRARI_RED, "#ff4d4d", "#f97316", "#facc15", "#38bdf8", "#60a5fa", "#a78bfa"]

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = PLOT_PALETTE

st.set_page_config(
    page_title="F1 Race Engineering HUD",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

HUD_CSS = f"""
<style>
:root {{
    --f1-red: {FERRARI_RED};
    --f1-red-soft: {FERRARI_RED_SOFT};
    --carbon: {CARBON_BLACK};
    --panel: {PANEL_BG};
    --panel2: {PANEL_BG_2};
    --text: {TEXT};
    --muted: {MUTED};
    --border: {BORDER};
}}

.stApp {{
    background:
        radial-gradient(circle at 52% 0%, rgba(225, 6, 0, 0.18), transparent 34%),
        radial-gradient(circle at 85% 22%, rgba(255, 45, 45, 0.08), transparent 26%),
        linear-gradient(135deg, #010101 0%, #05070d 45%, #0b0f14 100%);
    color: var(--text);
}}

[data-testid="stHeader"] {{
    background: rgba(1, 1, 1, 0.52);
    backdrop-filter: blur(14px);
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #050505, #0a0d12 52%, #050505);
    border-right: 1px solid rgba(225, 6, 0, 0.36);
}}

.block-container {{
    padding-top: 1rem;
    padding-bottom: 2.25rem;
    max-width: 1820px;
}}

h1, h2, h3 {{
    letter-spacing: -0.035em;
    color: #ffffff;
}}

.hud-title {{
    border: 1px solid rgba(225, 6, 0, 0.62);
    background:
        linear-gradient(135deg, rgba(225, 6, 0, 0.26), rgba(12, 16, 22, 0.96)),
        radial-gradient(circle at 88% 10%, rgba(255, 45, 45, 0.16), transparent 18rem);
    box-shadow: 0 24px 80px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.06);
    border-radius: 22px;
    padding: 26px 30px;
    margin-bottom: 18px;
}}

.hud-title h1 {{
    margin: 0;
    font-size: clamp(2.0rem, 3.1vw, 3.0rem);
    color: #ffffff;
}}

.hud-title p {{
    margin: 10px 0 0 0;
    color: #ff6b66;
    font-weight: 700;
    letter-spacing: 0.02em;
}}

.hud-title .hud-caption {{
    color: #d1d5db;
    font-size: 0.96rem;
    font-weight: 500;
    max-width: 1100px;
    margin-top: 0.45rem;
}}

.hud-card {{
    background:
        linear-gradient(180deg, rgba(17, 24, 39, 0.96), rgba(5, 8, 12, 0.98));
    border: 1px solid rgba(255,255,255,0.10);
    border-top: 2px solid var(--f1-red);
    border-radius: 18px;
    padding: 18px 18px;
    min-height: 112px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.04);
}}

.hud-card h3 {{
    margin: 0 0 10px 0;
    color: #e5e7eb;
    font-size: 0.84rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.hud-value {{
    color: #ffffff;
    font-size: 1.9rem;
    font-weight: 900;
    line-height: 1.1;
}}

.hud-sub {{
    color: var(--muted);
    font-size: 0.86rem;
    margin-top: 0.35rem;
}}

.hud-feed {{
    background: rgba(5, 8, 12, 0.74);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid var(--f1-red);
    padding: 10px 12px;
    margin: 8px 0;
    border-radius: 10px;
    color: #f7f7f7;
    box-shadow: 0 10px 24px rgba(0,0,0,0.20);
}}

.hud-badge {{
    display: inline-block;
    padding: 4px 9px;
    background: rgba(225,6,0,0.18);
    border: 1px solid rgba(225,6,0,0.55);
    border-radius: 999px;
    color: #ff6b66;
    font-size: 0.72rem;
    font-weight: 800;
    margin-right: 8px;
    letter-spacing: 0.04em;
}}

.replay-panel {{
    border: 1px solid rgba(225,6,0,0.45);
    background: rgba(5, 8, 12, 0.78);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
}}

section[data-testid="stTabs"] button {{
    color: #f5f5f5;
    font-weight: 700;
}}

.stDataFrame, [data-testid="stMetric"] {{
    background: rgba(10, 14, 18, 0.78);
    border-radius: 14px;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    overflow: hidden;
}}

.stButton > button {{
    border-radius: 999px;
    border: 1px solid rgba(255, 94, 90, 0.55);
    background: linear-gradient(135deg, var(--f1-red), #991b1b);
    color: white;
    font-weight: 900;
    letter-spacing: 0.02em;
    box-shadow: 0 12px 28px rgba(225, 6, 0, 0.22);
}}

.stButton > button:hover {{
    border-color: rgba(255, 160, 155, 0.90);
    filter: brightness(1.08);
}}

div[data-baseweb="select"] > div,
input {{
    background-color: rgba(10, 14, 18, 0.96) !important;
    color: var(--text) !important;
    border-color: rgba(255,255,255,0.12) !important;
}}

hr {{
    border-color: rgba(225, 6, 0, 0.22);
}}
</style>
"""
st.markdown(HUD_CSS, unsafe_allow_html=True)

RACES_2026 = [
    "Australian Grand Prix 2026", "Chinese Grand Prix 2026", "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026", "Saudi Arabian Grand Prix 2026", "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026", "Canadian Grand Prix 2026", "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026", "British Grand Prix 2026", "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026", "Italian Grand Prix 2026", "Singapore Grand Prix 2026",
    "United States Grand Prix 2026", "Mexico City Grand Prix 2026", "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026", "Qatar Grand Prix 2026", "Abu Dhabi Grand Prix 2026",
]


def theme_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(5, 7, 13, 0)",
        plot_bgcolor="rgba(7, 10, 16, 0.96)",
        font={"color": TEXT, "family": "Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 18, "r": 18, "t": 50, "b": 34},
        colorway=PLOT_PALETTE,
        legend={"bgcolor": "rgba(7, 10, 16, 0.55)", "bordercolor": "rgba(255,255,255,0.10)", "borderwidth": 1},
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    return fig


def hud_chart(fig):
    st.plotly_chart(theme_fig(fig), use_container_width=True)


@st.cache_data(show_spinner=False)
def demo_data():
    return build_demo_dataset()


@st.cache_data(show_spinner=True)
def build_hud_state(race_name: str, total_laps: int, pit_loss: float, rain_probability: float, seed: int):
    forecast_result = forecast_future_race(
        history_df=demo_data(),
        race_name=race_name,
        year=2026,
        round_no=12,
        n_simulations=2500,
        noise_std=2.0,
        use_2026_grid=True,
    )
    forecast = forecast_result["forecast"]
    simulation = forecast_result["simulation"]
    weather = forecast_result["weather"]

    replay = lap_by_lap_race_simulation(
        forecast,
        total_laps=total_laps,
        pit_loss=pit_loss,
        rain_probability=rain_probability,
        random_state=seed,
    )
    timeline = replay["timeline"]
    final_order = replay["final_order"]
    events = replay["events"]
    pitstops = replay["pitstops"]
    sectors = estimate_sector_times(timeline)
    alerts = detect_drs_and_overtake_alerts(timeline)
    radar = build_weather_radar(timeline, base_rain_probability=rain_probability)
    radio = generate_team_radio(timeline, pitstops, alerts)
    commentary = generate_tv_commentary(timeline, alerts, pitstops)
    director_log = generate_race_director_log(timeline, random_state=seed + 77)
    adjusted_final = apply_director_time_penalties(final_order, director_log)
    team_profiles = build_all_team_profiles(timeline)

    return {
        "forecast": forecast,
        "simulation": simulation,
        "weather": weather,
        "timeline": timeline,
        "final_order": final_order,
        "events": events,
        "pitstops": pitstops,
        "sectors": sectors,
        "alerts": alerts,
        "weather_radar": radar,
        "radio": radio,
        "commentary": commentary,
        "director_log": director_log,
        "adjusted_final": adjusted_final,
        "team_profiles": team_profiles,
    }


def card(title: str, value: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="hud-card">
            <h3>{title}</h3>
            <div class="hud-value">{value}</div>
            <div class="hud-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feed_line(label: str, text: str):
    st.markdown(f"<div class='hud-feed'><span class='hud-badge'>{label}</span>{text}</div>", unsafe_allow_html=True)


def clamp_lap(value: int, total_laps: int) -> int:
    return max(1, min(int(total_laps), int(value)))


st.markdown(
    """
    <div class="hud-title">
        <h1>F1 Race Engineering Command Center</h1>
        <p>Live Race Control • Strategy Intelligence • Telemetry • Weather Radar • Replay Pro</p>
        <div class="hud-caption">
            A professional HUD for simulated race-state analysis: leaderboard, track map, weather evolution,
            team radio, race director decisions, driver telemetry and AI race briefing in one cockpit.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Race Control Console")
    race_name = st.selectbox("Grand Prix", RACES_2026, index=11)
    total_laps = st.slider("Race distance", 10, 78, 53)
    pit_loss = st.slider("Pit-lane time loss", 15.0, 35.0, 22.5, step=0.5)
    rain_probability = st.slider("Rain probability", 0.0, 1.0, 0.20, step=0.05)
    seed = st.number_input("Simulation seed", min_value=1, max_value=99999, value=42)
    build = st.button("Build race state", type="primary")
    st.divider()
    st.caption("Use the lap selector to scrub the race state. Replay Pro gives frame-by-frame race-control review.")

if build or "hud_state" not in st.session_state:
    with st.spinner("Building F1 race-engineering state..."):
        st.session_state["hud_state"] = build_hud_state(race_name, int(total_laps), float(pit_loss), float(rain_probability), int(seed))
        st.session_state["hud_lap"] = 1
        st.session_state["replay_lap"] = 1

state = st.session_state["hud_state"]
timeline = state["timeline"]
final_order = state["final_order"]
adjusted_final = state["adjusted_final"]
weather_radar = state["weather_radar"]
alerts = state["alerts"]
radio = state["radio"]
commentary = state["commentary"]
director_log = state["director_log"]
sectors = state["sectors"]
events = state["events"]
pitstops = state["pitstops"]

st.session_state["hud_lap"] = clamp_lap(st.session_state.get("hud_lap", 1), total_laps)
current_lap = st.slider("Live lap selector", 1, int(total_laps), int(st.session_state["hud_lap"]))
st.session_state["hud_lap"] = current_lap

lap_df = timeline[timeline["Lap"] == current_lap].sort_values("RacePosition")
lap_weather = weather_radar[weather_radar["Lap"] == current_lap]
lap_alerts = alerts[alerts["Lap"] == current_lap] if not alerts.empty else pd.DataFrame()
lap_radio = radio[radio["Lap"] == current_lap] if not radio.empty else pd.DataFrame()
lap_commentary = commentary[commentary["Lap"] == current_lap] if not commentary.empty else pd.DataFrame()

leader = lap_df.iloc[0]["Driver"] if not lap_df.empty else "N/A"
track_grip = f"{float(lap_weather.iloc[0]['TrackGrip']) * 100:.0f}%" if not lap_weather.empty else "N/A"

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    card("Grand Prix", race_name.replace(" Grand Prix 2026", ""), "2026 simulation")
with m2:
    card("Lap", f"{current_lap}/{total_laps}", "current race state")
with m3:
    card("Leader", str(leader), "track position P1")
with m4:
    card("Track Grip", track_grip, "weather-adjusted")
with m5:
    card("DRS / Alerts", str(len(lap_alerts)), "current lap signals")

race_control_tab, replay_pro_tab = st.tabs(["🏁 Race Control", "🎮 Replay Pro"])

with race_control_tab:
    left, center, right = st.columns([1.05, 1.55, 1.05])

    with left:
        st.markdown("### Championship / Race Order")
        order_cols = ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "PitStops"]
        order_cols = [c for c in order_cols if c in lap_df.columns]
        st.dataframe(lap_df[order_cols].head(12), use_container_width=True, hide_index=True)

        st.markdown("### Monte Carlo Win Probability")
        sim = state["simulation"].head(8)
        if "WinProbability" in sim.columns:
            hud_chart(plot_probabilities(sim, "WinProbability"))

        st.markdown("### Race Director")
        summary = build_steward_summary(director_log)
        st.dataframe(summary, use_container_width=True, hide_index=True)
        if not director_log.empty:
            for _, row in director_log.sort_values("Lap").head(4).iterrows():
                feed_line(f"LAP {int(row['Lap'])}", row["Message"])

    with center:
        st.markdown("### Live Track Map")
        hud_chart(plot_track_map_animation(timeline))

        st.markdown("### Live Timing")
        hud_chart(
            px.bar(
                lap_df.sort_values("RacePosition"),
                x="Driver",
                y="GapToLeader",
                color="Compound",
                hover_data=["Team", "RacePosition", "TyreAge", "PitStops", "DNF"],
                title=f"Gap to Leader — Lap {current_lap}",
            )
        )

    with right:
        st.markdown("### Weather Radar")
        hud_chart(plot_weather_radar(weather_radar[weather_radar["Lap"] <= current_lap]))

        st.markdown("### Team Radio")
        if lap_radio.empty:
            feed_line("RADIO", "No team-radio message this lap.")
        else:
            for _, msg in lap_radio.head(6).iterrows():
                feed_line(str(msg["Driver"]), f"{msg['Channel']}: {msg['Message']}")

        st.markdown("### TV Broadcast")
        if lap_commentary.empty:
            feed_line("TV", "No broadcast line this lap.")
        else:
            for _, line in lap_commentary.head(5).iterrows():
                feed_line("LIVE", line["Commentary"])

        st.markdown("### DRS / Overtake Center")
        if lap_alerts.empty:
            feed_line("DRS", "No current DRS or overtake alert.")
        else:
            for _, alert in lap_alerts.head(5).iterrows():
                feed_line(str(alert["Type"]), str(alert["Message"]))

    bottom1, bottom2, bottom3 = st.columns([1.1, 1.1, 1.1])

    with bottom1:
        st.markdown("### Driver HUD")
        drivers = sorted(timeline["Driver"].unique())
        selected_driver = st.selectbox("Select driver", drivers, key="race_control_driver")
        profile = build_driver_profile(selected_driver, timeline)
        st.dataframe(profile, use_container_width=True, hide_index=True)
        hud_chart(plot_driver_skill_radar(selected_driver))
        hud_chart(plot_driver_status_animation(timeline, selected_driver))

    with bottom2:
        st.markdown("### Team Command Center")
        teams = sorted(timeline["Team"].dropna().unique())
        selected_team = st.selectbox("Select team", teams, key="race_control_team")
        team_profile = build_team_profile(selected_team, timeline)
        st.dataframe(team_profile, use_container_width=True, hide_index=True)
        hud_chart(plot_team_radar(selected_team))
        if not state["team_profiles"].empty:
            hud_chart(plot_team_comparison(state["team_profiles"]))

    with bottom3:
        st.markdown("### AI Presenter")
        scripts = build_full_ai_presentation(
            state,
            race_name=race_name,
            lap=current_lap,
            driver=selected_driver,
            team=selected_team,
        )
        for title, script in scripts.items():
            feed_line(title.upper(), script)

    st.markdown("### Final Classification After Steward Review")
    st.dataframe(adjusted_final, use_container_width=True, hide_index=True)

    st.markdown("### Full Race Director Timeline")
    hud_chart(plot_race_director_timeline(director_log))

with replay_pro_tab:
    st.markdown("<div class='replay-panel'>", unsafe_allow_html=True)
    st.markdown("### 🎮 Replay Pro Controls")
    if "replay_lap" not in st.session_state:
        st.session_state["replay_lap"] = current_lap

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        if st.button("⏮ Start", use_container_width=True):
            st.session_state["replay_lap"] = 1
    with c2:
        if st.button("⏪ -5 laps", use_container_width=True):
            st.session_state["replay_lap"] = clamp_lap(st.session_state["replay_lap"] - 5, total_laps)
    with c3:
        if st.button("◀ Previous", use_container_width=True):
            st.session_state["replay_lap"] = clamp_lap(st.session_state["replay_lap"] - 1, total_laps)
    with c4:
        if st.button("Next ▶", use_container_width=True):
            st.session_state["replay_lap"] = clamp_lap(st.session_state["replay_lap"] + 1, total_laps)
    with c5:
        if st.button("+5 laps ⏩", use_container_width=True):
            st.session_state["replay_lap"] = clamp_lap(st.session_state["replay_lap"] + 5, total_laps)
    with c6:
        if st.button("Finish ⏭", use_container_width=True):
            st.session_state["replay_lap"] = int(total_laps)

    replay_lap = st.slider("Replay lap", 1, int(total_laps), int(st.session_state["replay_lap"]), key="replay_lap_slider")
    st.session_state["replay_lap"] = replay_lap
    st.markdown("</div>", unsafe_allow_html=True)

    replay_lap_df = timeline[timeline["Lap"] == replay_lap].sort_values("RacePosition")
    replay_weather = weather_radar[weather_radar["Lap"] == replay_lap]
    replay_events = events[events["Lap"] == replay_lap] if not events.empty else pd.DataFrame()
    sc_active = "SC" in set(replay_lap_df["Event"].astype(str)) if not replay_lap_df.empty else False
    vsc_active = "VSC" in set(replay_lap_df["Event"].astype(str)) if not replay_lap_df.empty else False
    rain_active = "RAIN" in set(replay_lap_df["Event"].astype(str)) if not replay_lap_df.empty else False
    dnf_count = int(replay_lap_df["DNF"].sum()) if "DNF" in replay_lap_df else 0
    replay_grip = f"{float(replay_weather.iloc[0]['TrackGrip']) * 100:.0f}%" if not replay_weather.empty else "N/A"

    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        card("Replay Lap", f"{replay_lap}/{total_laps}", "scrubbed state")
    with s2:
        card("Safety Car", "ACTIVE" if sc_active else "CLEAR", "SC phase marker")
    with s3:
        card("VSC", "ACTIVE" if vsc_active else "CLEAR", "virtual safety car")
    with s4:
        card("Rain", "YES" if rain_active else "NO", f"grip {replay_grip}")
    with s5:
        card("DNF Count", str(dnf_count), "cars out")

    replay_left, replay_center, replay_right = st.columns([1.05, 1.55, 1.05])

    with replay_left:
        st.markdown("### 🏁 Replay Leaderboard")
        replay_cols = ["RacePosition", "Driver", "Team", "GapToLeader", "Compound", "TyreAge", "PitStops", "DNF"]
        replay_cols = [c for c in replay_cols if c in replay_lap_df.columns]
        st.dataframe(replay_lap_df[replay_cols].head(20), use_container_width=True, hide_index=True)

        st.markdown("### 📰 Replay Event Feed")
        event_stream = build_replay_event_stream(timeline, pitstops, events, alerts, replay_lap, window=3)
        if event_stream.empty:
            feed_line("REPLAY", "No notable events in the current replay window.")
        else:
            st.dataframe(event_stream, use_container_width=True, hide_index=True)

    with replay_center:
        st.markdown("### 🗺 Enhanced Replay Map")
        hud_chart(plot_selected_lap_track_map(timeline, replay_lap))

        st.markdown("### 📺 Broadcast Replay Window")
        replay_commentary = commentary[commentary["Lap"] == replay_lap] if not commentary.empty else pd.DataFrame()
        replay_alerts = alerts[alerts["Lap"] == replay_lap] if not alerts.empty else pd.DataFrame()
        if replay_commentary.empty and replay_alerts.empty:
            feed_line("BROADCAST", "Quiet lap. Field order is stable.")
        else:
            for _, row in replay_commentary.head(4).iterrows():
                feed_line("LIVE", row["Commentary"])
            for _, row in replay_alerts.head(4).iterrows():
                feed_line(str(row["Type"]).upper(), str(row["Message"]))

    with replay_right:
        st.markdown("### 📡 Driver Telemetry Center")
        replay_drivers = sorted(timeline["Driver"].unique())
        replay_driver = st.selectbox("Replay driver", replay_drivers, key="replay_driver")
        telemetry_snapshot = build_driver_telemetry_snapshot(replay_driver, timeline, sectors, replay_lap)
        st.dataframe(telemetry_snapshot, use_container_width=True, hide_index=True)
        hud_chart(plot_driver_telemetry_trace(sectors, timeline, replay_driver, replay_lap))

        st.markdown("### 🚨 Safety Car / Race Control Center")
        if replay_events.empty:
            feed_line("RACE CONTROL", "Green-flag running on this replay lap.")
        else:
            for _, row in replay_events.iterrows():
                feed_line("RACE CONTROL", f"{row.get('Event', 'EVENT')} logged on lap {int(row['Lap'])}.")

    st.markdown("### 🎥 Broadcast Mode Summary")
    b1, b2 = st.columns([1.2, 1.8])
    with b1:
        replay_summary_cols = [c for c in ["RacePosition", "Driver", "GapToLeader", "Compound", "DNF"] if c in replay_lap_df.columns]
        st.dataframe(replay_lap_df[replay_summary_cols].head(10), use_container_width=True, hide_index=True)
    with b2:
        scripts = build_full_ai_presentation(
            state,
            race_name=race_name,
            lap=replay_lap,
            driver=replay_driver,
            team=replay_lap_df.iloc[0]["Team"] if not replay_lap_df.empty and "Team" in replay_lap_df.columns else "Race Control",
        )
        for title, script in scripts.items():
            feed_line(title.upper(), script)
