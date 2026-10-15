# F1-AI-Race-Engineer 🏎️

An advanced Formula 1 Predictive Race Strategy & Telemetry Engine combining live FastF1 data ingestion, official 2026 Driver Lineups, 2026 Active Aerodynamics (Straight X-Mode & High-Downforce Z-Mode apex speeds), non-linear thermal tire physics, linear fuel burn-off modeling, a 1,000-run Monte Carlo disruption simulation engine, real-time weather controls, and an interactive Pit-Wall Engineering Notebook with full CRUD capabilities.

---

## ⚡ Key Features

- **🌐 Dynamic FastF1 Ingestion (25 Championship Circuits)**:
  - Real-time Grand Prix schedule parsing, pre-season testing filtering, and live median baseline lap times across 25 circuits with fallback calibration.
- **🏎️ Official 2026 Drivers & Teams Lineup (11 Teams, 22 Race Cars + 11 Reserves = 33 Drivers)**:
  - **11 Formula 1 Teams (22 Full-Time Race Cars)**: Ferrari (Hamilton & Leclerc), Red Bull (Verstappen & Lawson), McLaren (Norris & Piastri), Mercedes (Russell & Antonelli), Aston Martin (Alonso & Stroll), Williams (Sainz & Albon), Alpine (Gasly & Doohan), Racing Bulls (Tsunoda & Hadjar), Audi / Sauber (Hülkenberg & Bortoleto), Haas (Ocon & Bearman), and Cadillac F1 Team (Pérez & Bottas).
  - **11 Official Reserve & Test Drivers**: Colapinto, Drugovich, O'Ward, Vesti, Schumacher, Iwasa, Ricciardo, Aron, Pourchaire, Fittipaldi, and Herta.
  - Interactive grid filter: view all 33 drivers, 22 full-time race drivers, or 11 official reserves.
  - Individual ratings for Qualifying Pace, Tyre Management, Wet Weather Mastery, and Aggression multi-factor weights.
- **🚦 Driver Qualifying & Grid Starting Position Dynamics (P1 to P22)**:
  - **Pole / Front Row (P1-P2)**: Clean air efficiency bonus (-0.22s/lap), minimal tire thermal sliding stress.
  - **Front Pack (P3-P6)**: Slipstream advantage (+0.10s/lap).
  - **Midfield Pack (P7-P16)**: Dirty air aerodynamic wake (+0.38s/lap penalty, +15% tire slide wear), elevated Lap 1 Turn 1 incident risk.
  - **Deep Traffic (P17-P22)**: DRS train congestion (+0.55s/lap) with reverse-strategy overcut incentives.
- **💨 2026 Car Aerodynamic & Corner Speed Breakdown**:
  - Max Straight-Line Speed in low-drag X-Mode (e.g., Monza: 354 km/h, Baku: 356 km/h, Las Vegas: 355 km/h).
  - High-Speed Corner Apex Speeds in Z-Mode downforce (e.g., Copse/Silverstone: 286 km/h, Eau Rouge/Spa: 305 km/h, 130R/Suzuka: 298 km/h).
  - Medium-speed chassis balance apexes, low-speed hairpin mechanical grip, and circuit tire energy ratings.
- **🌦️ Real-Time Track Meteorology & Weather Options**:
  - **Preset Scenarios**: Dry & Sunny, Extreme Heat Blistering (>40°C), Cold Track Grip Loss (<25°C), Greasy Damp, Monsoon Rain, and Dynamic Incoming Rain (rain arriving mid-race on Lap 18).
  - **Custom Engineering Input**: Ambient Temperature, Track Surface Temperature, Track Moisture %, Rain Probability %, and Wind Speed.
- **🎯 Prominent Best Tyre Strategy & Optimal Pit Windows Box**:
  - Live AI-recommended Plan A (e.g., Medium ➔ Hard 1-Stop, Reverse Overcut Off-Set, or Wet ➔ Inter rain crossover).
  - Exact Pit Window (e.g. Laps 21–25, Target In-Lap: Lap 23).
  - Undercut / Overcut potency ratings and Contingency Plan B (Safety Car pivot delta: -11.5s).
- **📝 Interactive Strategic Engineering Notebook (Full CRUD)**:
  - Add new strategic notes / radio communications with Lap tags, Author channel, Priority level, and Category.
  - Inline Edit existing notes and live updates.
  - Delete resolved notes.
- **🎲 Predictive 1,000-Run Monte Carlo Engine**:
  - Lap-by-lap probabilistic incident rolls: 15% VSC (2 laps), 70% SC (3 laps), 15% Red Flag (free tire change override).
  - Real-time tactical override station: **BOX THIS LAP (Call Undercut)** vs **STAY OUT** re-rendering 1,000-scenario win probabilities on the fly.
- **📈 4 Real-Time Interactive Plotly Telemetry Charts**:
  - Live Lap Times colored by compound (🔴 Soft, 🟡 Medium, ⚪ Hard, 🟢 Inter, 🔵 Wet).
  - Linear Fuel Mass Burn-off curve (1.9 kg/lap @ 0.035 s/kg benefit).
  - Tri-Sector Telemetry Splits (Sector 1: 33%, Sector 2: 34%, Sector 3: 33%).
  - Tyre Wear Degradation Percentage (%) resetting at pit stops.

---

## 🚀 Quick Start

### 1. Requirements & Dependencies
```bash
pip install streamlit fastf1 plotly pandas
```

### 2. Launch the Streamlit Pit-Wall Web App
```bash
streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

### 3. Launch the Terminal Console Engine
```bash
python simulator.py
```

---

## 📁 Project Structure

```text
F1-AI-Race-Engineer/
├── app.py               # Streamlit real-time interactive pit-wall command station
├── simulator.py         # Terminal-based 1,000-race Monte Carlo predictive strategy engine
├── f1_lap_simulator.py  # Synchronized simulator module
├── .gitignore           # Ignores f1_cache/ and temporary build files
└── README.md            # Comprehensive project documentation
```

---

## 📄 License
MIT License. Open source for motorsport engineers, data scientists, and racing enthusiasts.
