
## F1 Intelligence Platform Upgrade

This project also includes an advanced motorsport analytics layer:

### Telemetry Lab
Interactive FastF1-based comparison of two drivers:

- speed trace comparison
- throttle and brake traces
- gear usage
- delta-time proxy
- track-map speed heatmap

Run:

```bash
streamlit run app/pages/1_Telemetry_Lab.py
```

### Strategy Lab
Race strategy simulator with tire degradation, tire cliff behavior, pit-loss modeling and pit-window optimization.

Run:

```bash
streamlit run app/pages/2_Strategy_Lab.py
```

### AI Race Engineer
Transparent rule-based advisor that evaluates whether a driver should pit now, pit soon, or stay out based on:

- undercut gain
- tire age
- target compound
- safety-car probability
- rain probability
- gaps ahead and behind

Run:

```bash
streamlit run app/pages/3_Race_Engineer_AI.py
```

### Live Timing Demo
Synthetic live timing stream for demonstrating real-time probability updates.

Run:

```bash
streamlit run app/pages/4_Live_Timing_Demo.py
```

### Full Dashboard
Run the main dashboard normally:

```bash
streamlit run app/dashboard.py
```

Streamlit will automatically detect the `app/pages/` directory and expose the new pages in the sidebar.
