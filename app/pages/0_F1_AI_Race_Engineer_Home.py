import streamlit as st

st.set_page_config(page_title="F1 AI Race Engineer", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #2a0505 0%, #090909 42%, #050505 100%);
    }
    .hero-shell {
        padding: 3rem 2.6rem;
        border-radius: 2rem;
        background: linear-gradient(135deg, rgba(120,0,0,0.94), rgba(12,12,12,0.98));
        border: 1px solid rgba(255, 78, 78, 0.42);
        box-shadow: 0 24px 80px rgba(0,0,0,0.45), 0 0 45px rgba(255,0,0,0.10);
        margin-bottom: 1.2rem;
    }
    .hero-eyebrow {
        color: #ffb3b3;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-size: 0.84rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    .hero-title {
        color: white;
        font-size: 4.2rem;
        line-height: 0.95;
        font-weight: 900;
        margin-bottom: 1rem;
    }
    .hero-copy {
        color: #f2dada;
        font-size: 1.18rem;
        line-height: 1.75;
        max-width: 920px;
    }
    .pill-row {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-top: 1.4rem;
    }
    .pill {
        padding: 0.48rem 0.86rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.16);
        color: #fff2f2;
        font-size: 0.9rem;
    }
    .glass-card {
        padding: 1.3rem;
        border-radius: 1.3rem;
        background: rgba(18,18,18,0.82);
        border: 1px solid rgba(255,255,255,0.10);
        min-height: 180px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.24);
    }
    .glass-card h3 {
        color: #ff5555;
        margin-bottom: 0.45rem;
    }
    .glass-card p {
        color: #e8e8e8;
        line-height: 1.55;
    }
    .section-title {
        color: #ffffff;
        margin-top: 2rem;
        margin-bottom: 0.8rem;
    }
    .workflow-step {
        padding: 1rem 1.1rem;
        border-left: 4px solid #ff3b3b;
        background: rgba(255,255,255,0.055);
        border-radius: 0.8rem;
        margin-bottom: 0.75rem;
        color: #f1f1f1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-shell">
        <div class="hero-eyebrow">AI motorsport engineering platform</div>
        <div class="hero-title">F1 AI Race Engineer</div>
        <div class="hero-copy">
            A premium Formula 1 forecasting cockpit built with machine learning, Monte Carlo simulation,
            weather intelligence, race-risk modeling, telemetry insights, tire degradation analysis, and
            AI-generated engineering reports. Designed to feel like a serious decision-support product,
            not a simple academic dashboard.
        </div>
        <div class="pill-row">
            <span class="pill">Machine Learning</span>
            <span class="pill">Monte Carlo</span>
            <span class="pill">Weather Risk</span>
            <span class="pill">Telemetry</span>
            <span class="pill">Race Strategy</span>
            <span class="pill">AI Analyst</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Forecast engine", "ML + simulation")
m2.metric("Race outputs", "Win / Podium / Top 10")
m3.metric("Risk layer", "Weather + DNF + SC")
m4.metric("Product style", "Base44-like UX")

st.markdown('<h2 class="section-title">What the app does</h2>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🏁 Race Forecasting</h3>
            <p>Predict finishing order using pace, grid position, driver form, team strength, and race-specific context.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🎲 Probabilistic Simulation</h3>
            <p>Run repeated stochastic race scenarios to estimate expected finish, win probability, podium probability, and top-10 probability.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🧠 AI Race Analyst</h3>
            <p>Transform model outputs into a professional race-engineering briefing with strategy, risk, uncertainty, and limitations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🌦️ Weather Intelligence</h3>
            <p>Account for rain probability, air temperature, humidity, wind, and changing race volatility.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        """
        <div class="glass-card">
            <h3>📡 Telemetry Thinking</h3>
            <p>Compare speed traces, driver controls, tire degradation, and performance signatures from real racing data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c6:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🏆 Championship Projection</h3>
            <p>Extend single-race forecasting into season-level driver and constructor title probability estimates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<h2 class="section-title">Engineering workflow</h2>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="workflow-step"><b>1. Ingest race context</b> — event, grid, pace, weather, driver/team strength, and historical form.</div>
    <div class="workflow-step"><b>2. Predict baseline race order</b> — supervised ML estimates finishing-position strength.</div>
    <div class="workflow-step"><b>3. Simulate uncertainty</b> — Monte Carlo scenarios propagate race randomness, reliability, and volatility.</div>
    <div class="workflow-step"><b>4. Interpret like an engineer</b> — explain risk, strategy, tires, safety cars, and probability limits.</div>
    <div class="workflow-step"><b>5. Present like a product</b> — turn the analysis into a polished technical demo for recruiters, professors, and motorsport engineers.</div>
    """,
    unsafe_allow_html=True,
)

st.divider()

left, right = st.columns([1.2, 0.8])
with left:
    st.subheader("Why it feels like a real AI product")
    st.write(
        "The interface is organized around user outcomes: run forecasts, inspect probabilities, "
        "understand risk, generate an analyst report, and explain methodology. It keeps the model honest "
        "by presenting predictions as probabilistic rather than guaranteed."
    )
with right:
    st.info(
        "Open the main dashboard to run forecasts, then use the AI Race Engineer Lab to generate a polished explanation of the results."
    )

st.success("Built as a Streamlit app with a Base44-style product experience, without depending on Base44.")
