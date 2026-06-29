import streamlit as st

st.set_page_config(page_title="AI Race Engineer Lab", layout="wide")

st.markdown(
    """
    <style>
    .hero {
        padding: 2.2rem;
        border-radius: 1.5rem;
        background: linear-gradient(135deg, #120000 0%, #2b0505 45%, #111111 100%);
        border: 1px solid rgba(255, 60, 60, 0.35);
        box-shadow: 0 0 38px rgba(255, 0, 0, 0.12);
    }
    .hero h1 {
        color: #ffffff;
        font-size: 3rem;
        margin-bottom: 0.4rem;
    }
    .hero p {
        color: #f4d7d7;
        font-size: 1.1rem;
        line-height: 1.65;
    }
    .metric-card {
        padding: 1.1rem;
        border-radius: 1rem;
        background: #151515;
        border: 1px solid #343434;
        min-height: 130px;
    }
    .metric-card h3 {
        color: #ff4b4b;
        margin-bottom: 0.4rem;
    }
    .metric-card p {
        color: #e8e8e8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🏎️ AI Race Engineer Lab</h1>
        <p>
        A premium prompt-engineering cockpit for Formula 1 forecasting: machine learning,
        Monte Carlo simulation, weather intelligence, race risk, tire strategy, and executive-level
        motorsport storytelling in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="metric-card"><h3>ML Core</h3><p>Race outcome prediction using pace, grid, form, driver strength, and team strength.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card"><h3>Monte Carlo</h3><p>Thousands of simulated race futures to estimate uncertainty, podium odds, and risk.</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card"><h3>Race Strategy</h3><p>Interprets weather, safety cars, DNFs, tire degradation, and pit-stop trade-offs.</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="metric-card"><h3>Presentation</h3><p>Turns technical results into a polished engineering story for demos and interviews.</p></div>', unsafe_allow_html=True)

st.divider()

st.subheader("🎯 Build a world-class F1 analysis prompt")

left, right = st.columns([1, 1])
with left:
    race_name = st.text_input("Race focus", "Belgian Grand Prix 2026")
    audience = st.selectbox(
        "Audience",
        [
            "Formula 1 engineering team",
            "University professor",
            "Motorsport data science recruiter",
            "Portfolio reviewer",
            "Technical interview panel",
        ],
    )
    tone = st.selectbox(
        "Tone",
        [
            "Elite engineering presentation",
            "Scientific university explanation",
            "Executive technical demo",
            "Race strategist briefing",
        ],
    )

with right:
    focus = st.multiselect(
        "Analysis modules",
        [
            "machine learning model",
            "Monte Carlo uncertainty",
            "weather impact",
            "safety-car and DNF risk",
            "tire degradation",
            "pit strategy",
            "championship projection",
            "model limitations",
        ],
        default=[
            "machine learning model",
            "Monte Carlo uncertainty",
            "weather impact",
            "safety-car and DNF risk",
            "tire degradation",
            "model limitations",
        ],
    )
    ambition = st.text_area(
        "What should the final answer prove?",
        "This project is not just a dashboard. It is a serious AI engineering system that connects motorsport domain knowledge, statistical simulation, machine learning, and clear decision support.",
        height=120,
    )

modules = ", ".join(focus)

prompt = f"""You are a senior Formula 1 race engineer, motorsport data scientist, and AI systems evaluator.

Prepare a premium analysis of the F1 AI Forecasting Platform for this audience: {audience}.
Use this tone: {tone}.
Race focus: {race_name}.

Project context:
The platform predicts Formula 1 race outcomes using machine learning, driver and team performance features, weather intelligence, safety-car risk, DNF risk, tire degradation concepts, Monte Carlo simulation, and championship projection.

The analysis must focus on: {modules}.

Main message to communicate:
{ambition}

Write the response with the quality expected from a top motorsport engineering environment.

Required structure:
1. Start with a powerful one-paragraph introduction that makes the project sound technically ambitious and credible.
2. Explain the machine-learning pipeline: data, features, target variable, model output, and ranking interpretation.
3. Explain Monte Carlo simulation scientifically: repeated stochastic scenarios, uncertainty propagation, expected finish, win probability, podium probability, and top-10 probability.
4. Explain how race engineering factors change predictions: weather, tire degradation, safety cars, reliability, pit strategy, and driver/team form.
5. Add an "Engineering Value" section showing why this system helps decision-making instead of only showing charts.
6. Add a "Scientific Limitations" section: probabilistic output, data quality, feature leakage risk, calibration, and need for validation on historical races.
7. Finish with a polished closing paragraph that sounds suitable for a university presentation, internship interview, or motorsport AI portfolio.

Style constraints:
- Be impressive but honest.
- Do not claim certainty.
- Use clear technical vocabulary.
- Avoid generic AI hype.
- Make the author sound like someone who understands both data science and Formula 1 engineering.
"""

st.subheader("🔥 Copy-ready prompt")
st.code(prompt, language="markdown")

st.download_button(
    "Download prompt",
    data=prompt,
    file_name="ai_race_engineer_prompt.txt",
    mime="text/plain",
)

st.divider()

st.subheader("✨ Demo output direction")
st.info(
    "Use this prompt with your forecast tables or screenshots from the dashboard. The best result comes when you paste the predicted order, Monte Carlo probabilities, weather metrics, and risk table under the prompt."
)

st.markdown(
    """
### Why this page looks strong

- It frames the project like an engineering decision-support system.
- It connects AI, probability, race strategy, and uncertainty.
- It is suitable for a technical portfolio, university presentation, and motorsport internship discussion.
- It avoids overclaiming: the model is presented as probabilistic and scientifically testable.
    """
)
