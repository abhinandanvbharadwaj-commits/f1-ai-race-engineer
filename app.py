"""
===============================================================================
🏎️ F1-AI-RACE-ENGINEER: REAL-TIME PIT-WALL TELEMETRY & STRATEGY ENGINE
===============================================================================
Streamlit Application combining:
- FastF1 Live Event & Schedule Ingestion (25 World Championship Circuits)
- Official 2026 Drivers & Teams Database (Hamilton @ Ferrari, Antonelli, Sainz @ Williams, etc.)
- Driver Qualifying Starting Grid Position (P1 to P20) Dirty Air & Traffic Mechanics
- 2026 Car Aerodynamic & Corner Speed Dynamics (Straight-line X-mode, High-speed Z-mode apexes)
- Dynamic Weather Meteorology (Realistic Presets + Real-Time Custom User Inputs)
- Non-Linear Thermal Physics & Weather Dampness Meteorology
- Linear Fuel Mass Burn-Off Modeling (1.9 kg/lap @ 0.035 s/kg benefit)
- Prominent Strategic Recommendation Box: Best Tyre Strategy, Exact Pit Windows & Contingencies
- Interactive Strategic Engineering Notebook with Full CRUD (Add / Edit / Delete Notes)
- Asynchronous Python Generator Streaming for Live Laps & Tri-Sector Analytics
- Interactive Plotly Charts (Lap Times, Fuel Mass Burn, Sector Splits, Tyre Degradation)
- Split-Second Strategic Override Station (Undercut Attacks, Safety Cars, Red Flags)
- Real-Time 1,000-Run Monte Carlo Win Probability Re-Optimization Engine
===============================================================================
"""

import os
import sys
import time
import random
import logging
import warnings
from datetime import datetime
import fastf1
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configure logging
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# -----------------------------------------------------------------------------
# 1. STREAMLIT CONFIGURATION & PIT-WALL STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="F1 AI Race Engineer | Pit-Wall Telemetry",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Tech Dark Pit-Wall Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .f1-header-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 2.1rem;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #ff1801, #ff8700, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .f1-sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    
    .status-card {
        background: #111827;
        border-radius: 8px;
        border: 1px solid #1f2937;
        padding: 12px 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    }
    
    .best-strategy-box {
        background: linear-gradient(135deg, #131c2e 0%, #0d1522 100%);
        border-radius: 10px;
        border: 2px solid #00f2fe;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.25);
    }

    .best-strategy-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 1.25rem;
        color: #00f2fe;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }

    .flag-green {
        background: linear-gradient(90deg, #064e3b, #059669);
        color: #ecfdf5;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 1.05rem;
        letter-spacing: 1px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }
    
    .flag-yellow {
        background: linear-gradient(90deg, #78350f, #d97706);
        color: #fffbeb;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 1.05rem;
        letter-spacing: 1px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
        animation: pulse 1.5s infinite;
    }
    
    .flag-red {
        background: linear-gradient(90deg, #7f1d1d, #dc2626);
        color: #fef2f2;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 1.05rem;
        letter-spacing: 1px;
        display: inline-block;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
        animation: pulse 1.2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.65; }
    }
    
    .kpi-title {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .kpi-val {
        font-family: 'Orbitron', monospace;
        font-size: 1.45rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .note-card-critical {
        border-left: 4px solid #ef4444;
        background: #1e141a;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }

    .note-card-warning {
        border-left: 4px solid #f59e0b;
        background: #1c1913;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }

    .note-card-info {
        border-left: 4px solid #00f2fe;
        background: #0f1c26;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. FASTF1 CACHE & CALIBRATED DATABASE (25 CIRCUITS)
# -----------------------------------------------------------------------------
os.makedirs("f1_cache", exist_ok=True)
try:
    fastf1.Cache.enable_cache("f1_cache")
    fastf1.set_log_level("ERROR")
except Exception:
    pass

FALLBACK_CIRCUITS = {
    "Monza": {
        "event_name": "Italian Grand Prix",
        "round": 16,
        "country": "Italy",
        "location": "Monza",
        "race_laps": 53,
        "pit_loss": 24.0,
        "base_pace": 86.968,
        "sc_risk": 0.25,
        "max_straight_speed": 354,
        "high_speed_apex": 295,
        "medium_speed_apex": 210,
        "low_speed_apex": 76,
        "aero_downforce_spec": "Low Drag / X-Mode Optimized",
        "tyre_energy_rating": "Medium (Braking & Traction)"
    },
    "Silverstone": {
        "event_name": "British Grand Prix",
        "round": 12,
        "country": "Great Britain",
        "location": "Silverstone",
        "race_laps": 52,
        "pit_loss": 25.0,
        "base_pace": 93.100,
        "sc_risk": 0.50,
        "max_straight_speed": 335,
        "high_speed_apex": 286,
        "medium_speed_apex": 195,
        "low_speed_apex": 92,
        "aero_downforce_spec": "High Downforce / Z-Mode Peak",
        "tyre_energy_rating": "Extreme (Lateral High-G Energy)"
    },
    "Monaco": {
        "event_name": "Monaco Grand Prix",
        "round": 8,
        "country": "Monaco",
        "location": "Monte Carlo",
        "race_laps": 78,
        "pit_loss": 20.0,
        "base_pace": 78.430,
        "sc_risk": 0.85,
        "max_straight_speed": 292,
        "high_speed_apex": 168,
        "medium_speed_apex": 135,
        "low_speed_apex": 52,
        "aero_downforce_spec": "Maximum Downforce / Maximum Lock",
        "tyre_energy_rating": "Low (Pure Mechanical Grip)"
    },
    "Spa": {
        "event_name": "Belgian Grand Prix",
        "round": 14,
        "country": "Belgium",
        "location": "Spa-Francorchamps",
        "race_laps": 44,
        "pit_loss": 22.0,
        "base_pace": 108.250,
        "sc_risk": 0.60,
        "max_straight_speed": 344,
        "high_speed_apex": 305,
        "medium_speed_apex": 185,
        "low_speed_apex": 74,
        "aero_downforce_spec": "Medium-Low / Efficiency Balanced",
        "tyre_energy_rating": "High (Compression & High-G Sweepers)"
    },
    "Bahrain": {
        "event_name": "Bahrain Grand Prix",
        "round": 1,
        "country": "Bahrain",
        "location": "Sakhir",
        "race_laps": 57,
        "pit_loss": 23.0,
        "base_pace": 96.120,
        "sc_risk": 0.35,
        "max_straight_speed": 338,
        "high_speed_apex": 255,
        "medium_speed_apex": 175,
        "low_speed_apex": 68,
        "aero_downforce_spec": "Medium Downforce",
        "tyre_energy_rating": "High (Rear Thermal Degradation)"
    },
    "Saudi Arabia": {
        "event_name": "Saudi Arabian Grand Prix",
        "round": 2,
        "country": "Saudi Arabia",
        "location": "Jeddah",
        "race_laps": 50,
        "pit_loss": 21.0,
        "base_pace": 93.450,
        "sc_risk": 0.80,
        "max_straight_speed": 348,
        "high_speed_apex": 278,
        "medium_speed_apex": 205,
        "low_speed_apex": 110,
        "aero_downforce_spec": "Medium-Low Downforce",
        "tyre_energy_rating": "High (Rapid High-Speed Direction Changes)"
    },
    "Australia": {
        "event_name": "Australian Grand Prix",
        "round": 3,
        "country": "Australia",
        "location": "Melbourne",
        "race_laps": 58,
        "pit_loss": 21.5,
        "base_pace": 82.340,
        "sc_risk": 0.65,
        "max_straight_speed": 332,
        "high_speed_apex": 262,
        "medium_speed_apex": 178,
        "low_speed_apex": 88,
        "aero_downforce_spec": "Medium Downforce",
        "tyre_energy_rating": "Medium (Street Surface Evolution)"
    },
    "Japan": {
        "event_name": "Japanese Grand Prix",
        "round": 4,
        "country": "Japan",
        "location": "Suzuka",
        "race_laps": 53,
        "pit_loss": 23.5,
        "base_pace": 95.110,
        "sc_risk": 0.40,
        "max_straight_speed": 336,
        "high_speed_apex": 298,
        "medium_speed_apex": 188,
        "low_speed_apex": 72,
        "aero_downforce_spec": "High Downforce / Z-Mode Loaded",
        "tyre_energy_rating": "Extreme (Figure-8 Lateral Lateral Gs)"
    },
    "China": {
        "event_name": "Chinese Grand Prix",
        "round": 5,
        "country": "China",
        "location": "Shanghai",
        "race_laps": 56,
        "pit_loss": 23.0,
        "base_pace": 84.225,
        "sc_risk": 0.50,
        "max_straight_speed": 346,
        "high_speed_apex": 248,
        "medium_speed_apex": 165,
        "low_speed_apex": 82,
        "aero_downforce_spec": "Medium Downforce",
        "tyre_energy_rating": "High (Front-Left Graining Snail Corner)"
    },
    "Miami": {
        "event_name": "Miami Grand Prix",
        "round": 6,
        "country": "United States",
        "location": "Miami",
        "race_laps": 57,
        "pit_loss": 21.0,
        "base_pace": 91.500,
        "sc_risk": 0.45,
        "max_straight_speed": 345,
        "high_speed_apex": 252,
        "medium_speed_apex": 172,
        "low_speed_apex": 65,
        "aero_downforce_spec": "Medium-Low Downforce",
        "tyre_energy_rating": "Medium (Thermal Blistering Surface)"
    },
    "Imola": {
        "event_name": "Emilia Romagna Grand Prix",
        "round": 7,
        "country": "Italy",
        "location": "Imola",
        "race_laps": 63,
        "pit_loss": 27.0,
        "base_pace": 80.450,
        "sc_risk": 0.60,
        "max_straight_speed": 330,
        "high_speed_apex": 268,
        "medium_speed_apex": 190,
        "low_speed_apex": 86,
        "aero_downforce_spec": "High Downforce",
        "tyre_energy_rating": "High (Kerb Striking & Traction)"
    },
    "Canada": {
        "event_name": "Canadian Grand Prix",
        "round": 9,
        "country": "Canada",
        "location": "Montreal",
        "race_laps": 70,
        "pit_loss": 19.5,
        "base_pace": 76.150,
        "sc_risk": 0.70,
        "max_straight_speed": 342,
        "high_speed_apex": 235,
        "medium_speed_apex": 160,
        "low_speed_apex": 68,
        "aero_downforce_spec": "Low-Medium Downforce",
        "tyre_energy_rating": "High (Brake & Acceleration Shock)"
    },
    "Spain": {
        "event_name": "Spanish Grand Prix",
        "round": 10,
        "country": "Spain",
        "location": "Barcelona",
        "race_laps": 66,
        "pit_loss": 23.0,
        "base_pace": 79.850,
        "sc_risk": 0.30,
        "max_straight_speed": 334,
        "high_speed_apex": 274,
        "medium_speed_apex": 182,
        "low_speed_apex": 94,
        "aero_downforce_spec": "High Downforce Aero Benchmark",
        "tyre_energy_rating": "Extreme (Turn 3 Long High-G Lateral)"
    },
    "Austria": {
        "event_name": "Austrian Grand Prix",
        "round": 11,
        "country": "Austria",
        "location": "Spielberg",
        "race_laps": 71,
        "pit_loss": 21.0,
        "base_pace": 69.900,
        "sc_risk": 0.35,
        "max_straight_speed": 338,
        "high_speed_apex": 270,
        "medium_speed_apex": 192,
        "low_speed_apex": 84,
        "aero_downforce_spec": "Medium-High Downforce",
        "tyre_energy_rating": "Medium (Short Lap High Repetition)"
    },
    "Hungary": {
        "event_name": "Hungarian Grand Prix",
        "round": 13,
        "country": "Hungary",
        "location": "Budapest",
        "race_laps": 70,
        "pit_loss": 21.5,
        "base_pace": 82.100,
        "sc_risk": 0.30,
        "max_straight_speed": 318,
        "high_speed_apex": 230,
        "medium_speed_apex": 162,
        "low_speed_apex": 78,
        "aero_downforce_spec": "Maximum Downforce (Monaco without walls)",
        "tyre_energy_rating": "High (Relentless Corner Twisting)"
    },
    "Zandvoort": {
        "event_name": "Dutch Grand Prix",
        "round": 15,
        "country": "Netherlands",
        "location": "Zandvoort",
        "race_laps": 72,
        "pit_loss": 22.0,
        "base_pace": 75.400,
        "sc_risk": 0.50,
        "max_straight_speed": 322,
        "high_speed_apex": 265,
        "medium_speed_apex": 174,
        "low_speed_apex": 82,
        "aero_downforce_spec": "High Downforce / Banked Corners",
        "tyre_energy_rating": "Very High (Banked Compression Forces)"
    },
    "Baku": {
        "event_name": "Azerbaijan Grand Prix",
        "round": 17,
        "country": "Azerbaijan",
        "location": "Baku",
        "race_laps": 51,
        "pit_loss": 22.0,
        "base_pace": 106.200,
        "sc_risk": 0.75,
        "max_straight_speed": 356,
        "high_speed_apex": 215,
        "medium_speed_apex": 155,
        "low_speed_apex": 78,
        "aero_downforce_spec": "Low Drag Monster Straight",
        "tyre_energy_rating": "Medium (Cold Fronts on 2.2km Straight)"
    },
    "Singapore": {
        "event_name": "Singapore Grand Prix",
        "round": 18,
        "country": "Singapore",
        "location": "Marina Bay",
        "race_laps": 62,
        "pit_loss": 29.0,
        "base_pace": 98.900,
        "sc_risk": 0.95,
        "max_straight_speed": 312,
        "high_speed_apex": 225,
        "medium_speed_apex": 152,
        "low_speed_apex": 62,
        "aero_downforce_spec": "Maximum Downforce Street Layout",
        "tyre_energy_rating": "Extreme (Thermal Overheating & 19 Turns)"
    },
    "Austin": {
        "event_name": "United States Grand Prix",
        "round": 19,
        "country": "United States",
        "location": "Austin",
        "race_laps": 56,
        "pit_loss": 21.5,
        "base_pace": 100.350,
        "sc_risk": 0.35,
        "max_straight_speed": 338,
        "high_speed_apex": 272,
        "medium_speed_apex": 178,
        "low_speed_apex": 75,
        "aero_downforce_spec": "High Downforce / S-Curves",
        "tyre_energy_rating": "Very High (Sector 1 High-G Essence)"
    },
    "Mexico": {
        "event_name": "Mexico City Grand Prix",
        "round": 20,
        "country": "Mexico",
        "location": "Mexico City",
        "race_laps": 71,
        "pit_loss": 23.0,
        "base_pace": 82.600,
        "sc_risk": 0.30,
        "max_straight_speed": 352,
        "high_speed_apex": 242,
        "medium_speed_apex": 168,
        "low_speed_apex": 64,
        "aero_downforce_spec": "Max Wing with Low Air Density",
        "tyre_energy_rating": "Low-Medium (Thin Air Cooling Challenge)"
    },
    "Brazil": {
        "event_name": "São Paulo Grand Prix",
        "round": 21,
        "country": "Brazil",
        "location": "Interlagos",
        "race_laps": 71,
        "pit_loss": 22.5,
        "base_pace": 75.200,
        "sc_risk": 0.65,
        "max_straight_speed": 332,
        "high_speed_apex": 260,
        "medium_speed_apex": 175,
        "low_speed_apex": 82,
        "aero_downforce_spec": "Medium-High Downforce",
        "tyre_energy_rating": "High (Anti-Clockwise Neck Strain)"
    },
    "Las Vegas": {
        "event_name": "Las Vegas Grand Prix",
        "round": 22,
        "country": "United States",
        "location": "Las Vegas",
        "race_laps": 50,
        "pit_loss": 22.0,
        "base_pace": 97.400,
        "sc_risk": 0.60,
        "max_straight_speed": 355,
        "high_speed_apex": 220,
        "medium_speed_apex": 160,
        "low_speed_apex": 72,
        "aero_downforce_spec": "Low Drag Strip Speed",
        "tyre_energy_rating": "Low (Cold Night Graining Risk)"
    },
    "Qatar": {
        "event_name": "Qatar Grand Prix",
        "round": 23,
        "country": "Qatar",
        "location": "Lusail",
        "race_laps": 57,
        "pit_loss": 24.5,
        "base_pace": 87.800,
        "sc_risk": 0.35,
        "max_straight_speed": 340,
        "high_speed_apex": 284,
        "medium_speed_apex": 215,
        "low_speed_apex": 112,
        "aero_downforce_spec": "High Downforce Fast Flow",
        "tyre_energy_rating": "Extreme (Severe Kerb & Sidewall Loads)"
    },
    "Abu Dhabi": {
        "event_name": "Abu Dhabi Grand Prix",
        "round": 24,
        "country": "United Arab Emirates",
        "location": "Yas Marina",
        "race_laps": 58,
        "pit_loss": 23.0,
        "base_pace": 89.200,
        "sc_risk": 0.40,
        "max_straight_speed": 336,
        "high_speed_apex": 268,
        "medium_speed_apex": 182,
        "low_speed_apex": 78,
        "aero_downforce_spec": "Medium Downforce",
        "tyre_energy_rating": "Medium (Twilight Cooling Transitions)"
    },
    "Portugal": {
        "event_name": "Portuguese Grand Prix",
        "round": 25,
        "country": "Portugal",
        "location": "Portimao",
        "race_laps": 66,
        "pit_loss": 22.0,
        "base_pace": 81.300,
        "sc_risk": 0.40,
        "max_straight_speed": 338,
        "high_speed_apex": 264,
        "medium_speed_apex": 178,
        "low_speed_apex": 80,
        "aero_downforce_spec": "Medium-High Downforce",
        "tyre_energy_rating": "High (Rollercoaster Undulations)"
    }
}


@st.cache_data(show_spinner=False)
def load_all_circuits(year=2026):
    """Dynamically loads official F1 schedule via FastF1, ignoring testing slots."""
    circuits = {k: dict(v) for k, v in FALLBACK_CIRCUITS.items()}
    try:
        schedule = fastf1.get_event_schedule(year)
        if "RoundNumber" in schedule.columns:
            races = schedule[schedule["RoundNumber"] > 0]
        else:
            races = schedule[~schedule["EventName"].astype(str).str.contains("Testing", case=False, na=False)]

        if not races.empty:
            for _, event in races.iterrows():
                event_name = str(event.get("EventName", ""))
                location = str(event.get("Location", ""))
                country = str(event.get("Country", ""))
                round_num = int(event.get("RoundNumber", 0)) if "RoundNumber" in event else 0

                for key in circuits:
                    if (key.lower() in event_name.lower() or 
                        key.lower() in location.lower() or 
                        key.lower() in country.lower()):
                        circuits[key]["event_name"] = event_name
                        circuits[key]["round"] = round_num
                        circuits[key]["country"] = country
                        circuits[key]["location"] = location
                        break
    except Exception:
        pass
    return circuits


ALL_CIRCUITS = load_all_circuits(2026)


# -----------------------------------------------------------------------------
# 3. 2026 DRIVERS & TEAMS GRID LINEUP (11 TEAMS, 22 CARS + RESERVES & DEVELOPMENT)
# -----------------------------------------------------------------------------
DRIVERS_2026 = {
    # =========================================================================
    # 1. MERCEDES-AMG PETRONAS F1 TEAM
    # =========================================================================
    "George Russell": {
        "team": "Mercedes-AMG Petronas F1 Team",
        "role": "Race Driver",
        "number": 63,
        "team_color": "#27F4D2",
        "pace_delta": -0.25,
        "deg_multiplier": 0.94,
        "risk_multiplier": 1.05,
        "qualifying_rating": 96,
        "tyre_mgmt_rating": 92,
        "wet_weather_rating": 94,
        "badge": "🇬🇧 RUS #63",
        "style": "High-Pressure Attacker & Tire Manager"
    },
    "Andrea Kimi Antonelli": {
        "team": "Mercedes-AMG Petronas F1 Team",
        "role": "Race Driver",
        "number": 12,
        "team_color": "#27F4D2",
        "pace_delta": -0.16,
        "deg_multiplier": 1.10,
        "risk_multiplier": 1.20,
        "qualifying_rating": 93,
        "tyre_mgmt_rating": 86,
        "wet_weather_rating": 88,
        "badge": "🇮🇹 ANT #12",
        "style": "Fearless Prodigy & Aggressive Braking"
    },
    "Fred Vesti": {
        "team": "Mercedes-AMG Petronas F1 Team",
        "role": "Reserve Driver",
        "number": 42,
        "team_color": "#27F4D2",
        "pace_delta": +0.00,
        "deg_multiplier": 0.98,
        "risk_multiplier": 0.95,
        "qualifying_rating": 89,
        "tyre_mgmt_rating": 89,
        "wet_weather_rating": 91,
        "badge": "🇩🇰 VES #42 [RESERVE]",
        "style": "Smooth Technical Consistency"
    },
    "Joshua Dürksen": {
        "team": "Mercedes-AMG Petronas F1 Team",
        "role": "Development Driver",
        "number": 24,
        "team_color": "#27F4D2",
        "pace_delta": +0.08,
        "deg_multiplier": 1.05,
        "risk_multiplier": 1.12,
        "qualifying_rating": 87,
        "tyre_mgmt_rating": 85,
        "wet_weather_rating": 84,
        "badge": "🇵🇾 DUE #24 [DEV]",
        "style": "F2 Podiums & High Downforce Mastery"
    },

    # =========================================================================
    # 2. SCUDERIA FERRARI
    # =========================================================================
    "Charles Leclerc": {
        "team": "Scuderia Ferrari",
        "role": "Race Driver",
        "number": 16,
        "team_color": "#E80020",
        "pace_delta": -0.30,
        "deg_multiplier": 0.94,
        "risk_multiplier": 1.05,
        "qualifying_rating": 99,
        "tyre_mgmt_rating": 92,
        "wet_weather_rating": 93,
        "badge": "🇲🇨 LEC #16",
        "style": "Qualifying King & High Agility Apex"
    },
    "Lewis Hamilton": {
        "team": "Scuderia Ferrari",
        "role": "Race Driver",
        "number": 44,
        "team_color": "#E80020",
        "pace_delta": -0.28,
        "deg_multiplier": 0.82,
        "risk_multiplier": 0.85,
        "qualifying_rating": 97,
        "tyre_mgmt_rating": 99,
        "wet_weather_rating": 98,
        "badge": "🇬🇧 HAM #44",
        "style": "Master Tire Whisperer & Racecraft Legend"
    },
    "Antonio Giovinazzi": {
        "team": "Scuderia Ferrari",
        "role": "Reserve Driver",
        "number": 99,
        "team_color": "#E80020",
        "pace_delta": +0.02,
        "deg_multiplier": 0.94,
        "risk_multiplier": 0.90,
        "qualifying_rating": 90,
        "tyre_mgmt_rating": 93,
        "wet_weather_rating": 92,
        "badge": "🇮🇹 GIO #99 [RESERVE]",
        "style": "Le Mans Winner & Tire Endurance Specialist"
    },

    # =========================================================================
    # 3. MCLAREN F1 TEAM
    # =========================================================================
    "Lando Norris": {
        "team": "McLaren F1 Team",
        "role": "Race Driver",
        "number": 1,
        "team_color": "#FF8000",
        "pace_delta": -0.31,
        "deg_multiplier": 0.89,
        "risk_multiplier": 0.95,
        "qualifying_rating": 98,
        "tyre_mgmt_rating": 95,
        "wet_weather_rating": 96,
        "badge": "🇬🇧 NOR #1",
        "style": "World Champion Precision & Rapid Pacing"
    },
    "Oscar Piastri": {
        "team": "McLaren F1 Team",
        "role": "Race Driver",
        "number": 81,
        "team_color": "#FF8000",
        "pace_delta": -0.23,
        "deg_multiplier": 0.91,
        "risk_multiplier": 0.90,
        "qualifying_rating": 96,
        "tyre_mgmt_rating": 93,
        "wet_weather_rating": 92,
        "badge": "🇦🇺 PIA #81",
        "style": "Ice-Cool Strategic Composure"
    },
    "Leonardo Fornaroli": {
        "team": "McLaren F1 Team",
        "role": "Reserve Driver",
        "number": 33,
        "team_color": "#FF8000",
        "pace_delta": +0.04,
        "deg_multiplier": 1.02,
        "risk_multiplier": 1.05,
        "qualifying_rating": 89,
        "tyre_mgmt_rating": 90,
        "wet_weather_rating": 88,
        "badge": "🇮🇹 FOR #33 [RESERVE]",
        "style": "F3 Champion & Ultra-Consistent Line"
    },
    "Pato O'Ward": {
        "team": "McLaren F1 Team",
        "role": "Reserve Driver",
        "number": 29,
        "team_color": "#FF8000",
        "pace_delta": -0.08,
        "deg_multiplier": 1.10,
        "risk_multiplier": 1.25,
        "qualifying_rating": 92,
        "tyre_mgmt_rating": 84,
        "wet_weather_rating": 87,
        "badge": "🇲🇽 OWA #29 [RESERVE]",
        "style": "IndyCar Star & Maximum Attack"
    },

    # =========================================================================
    # 4. ORACLE RED BULL RACING
    # =========================================================================
    "Max Verstappen": {
        "team": "Oracle Red Bull Racing",
        "role": "Race Driver",
        "number": 3,
        "team_color": "#3671C6",
        "pace_delta": -0.33,
        "deg_multiplier": 0.87,
        "risk_multiplier": 1.10,
        "qualifying_rating": 99,
        "tyre_mgmt_rating": 97,
        "wet_weather_rating": 99,
        "badge": "🇳🇱 VER #3",
        "style": "Relentless Apex Striker & Wet Master"
    },
    "Isack Hadjar": {
        "team": "Oracle Red Bull Racing",
        "role": "Race Driver",
        "number": 6,
        "team_color": "#3671C6",
        "pace_delta": -0.12,
        "deg_multiplier": 1.05,
        "risk_multiplier": 1.18,
        "qualifying_rating": 92,
        "tyre_mgmt_rating": 88,
        "wet_weather_rating": 89,
        "badge": "🇫🇷 HAD #6",
        "style": "Aggressive High-Downforce Attacker"
    },
    "Yuki Tsunoda": {
        "team": "Oracle Red Bull Racing",
        "role": "Reserve Driver",
        "number": 22,
        "team_color": "#3671C6",
        "pace_delta": -0.10,
        "deg_multiplier": 1.00,
        "risk_multiplier": 1.12,
        "qualifying_rating": 92,
        "tyre_mgmt_rating": 90,
        "wet_weather_rating": 90,
        "badge": "🇯🇵 TSU #22 [RESERVE]",
        "style": "Fiery Braking Attack & Multi-Team Ready"
    },

    # =========================================================================
    # 5. VISA CASH APP RACING BULLS
    # =========================================================================
    "Liam Lawson": {
        "team": "Visa Cash App Racing Bulls",
        "role": "Race Driver",
        "number": 30,
        "team_color": "#6692FF",
        "pace_delta": -0.10,
        "deg_multiplier": 0.98,
        "risk_multiplier": 1.10,
        "qualifying_rating": 91,
        "tyre_mgmt_rating": 90,
        "wet_weather_rating": 89,
        "badge": "🇳🇿 LAW #30",
        "style": "Tenacious Wheel-to-Wheel Battler"
    },
    "Arvid Lindblad": {
        "team": "Visa Cash App Racing Bulls",
        "role": "Race Driver",
        "number": 41,
        "team_color": "#6692FF",
        "pace_delta": -0.05,
        "deg_multiplier": 1.08,
        "risk_multiplier": 1.15,
        "qualifying_rating": 90,
        "tyre_mgmt_rating": 86,
        "wet_weather_rating": 87,
        "badge": "🇬🇧 LIN #41",
        "style": "Fearless Young Gun & Rapid Evolution"
    },
    "Ayumu Iwasa": {
        "team": "Visa Cash App Racing Bulls",
        "role": "Reserve Driver",
        "number": 36,
        "team_color": "#6692FF",
        "pace_delta": -0.02,
        "deg_multiplier": 1.04,
        "risk_multiplier": 1.14,
        "qualifying_rating": 90,
        "tyre_mgmt_rating": 87,
        "wet_weather_rating": 88,
        "badge": "🇯🇵 IWA #36 [RESERVE]",
        "style": "Late Braker & Super Formula Star"
    },

    # =========================================================================
    # 6. ASTON MARTIN ARAMCO F1 TEAM
    # =========================================================================
    "Fernando Alonso": {
        "team": "Aston Martin Aramco F1 Team",
        "role": "Race Driver",
        "number": 14,
        "team_color": "#229971",
        "pace_delta": -0.20,
        "deg_multiplier": 0.85,
        "risk_multiplier": 0.85,
        "qualifying_rating": 95,
        "tyre_mgmt_rating": 98,
        "wet_weather_rating": 97,
        "badge": "🇪🇸 ALO #14",
        "style": "Tactical Maestro & Tire Conserving General"
    },
    "Lance Stroll": {
        "team": "Aston Martin Aramco F1 Team",
        "role": "Race Driver",
        "number": 18,
        "team_color": "#229971",
        "pace_delta": +0.08,
        "deg_multiplier": 1.04,
        "risk_multiplier": 1.10,
        "qualifying_rating": 87,
        "tyre_mgmt_rating": 86,
        "wet_weather_rating": 92,
        "badge": "🇨🇦 STR #18",
        "style": "Wet Weather Opportunist & Start Jumper"
    },
    "Stoffel Vandoorne": {
        "team": "Aston Martin Aramco F1 Team",
        "role": "Reserve Driver",
        "number": 2,
        "team_color": "#229971",
        "pace_delta": +0.02,
        "deg_multiplier": 0.94,
        "risk_multiplier": 0.90,
        "qualifying_rating": 89,
        "tyre_mgmt_rating": 92,
        "wet_weather_rating": 90,
        "badge": "🇧🇪 VAN #2 [RESERVE]",
        "style": "Formula E Champion & Simulator Benchmark"
    },
    "Jak Crawford": {
        "team": "Aston Martin Aramco F1 Team",
        "role": "Reserve Driver",
        "number": 7,
        "team_color": "#229971",
        "pace_delta": +0.05,
        "deg_multiplier": 1.05,
        "risk_multiplier": 1.10,
        "qualifying_rating": 88,
        "tyre_mgmt_rating": 86,
        "wet_weather_rating": 85,
        "badge": "🇺🇸 CRA #7 [RESERVE]",
        "style": "American F2 Winner & High-G Control"
    },

    # =========================================================================
    # 7. BWT ALPINE F1 TEAM
    # =========================================================================
    "Pierre Gasly": {
        "team": "BWT Alpine F1 Team",
        "role": "Race Driver",
        "number": 10,
        "team_color": "#FF87BC",
        "pace_delta": -0.10,
        "deg_multiplier": 0.96,
        "risk_multiplier": 1.05,
        "qualifying_rating": 92,
        "tyre_mgmt_rating": 90,
        "wet_weather_rating": 91,
        "badge": "🇫🇷 GAS #10",
        "style": "Stubborn Defender & Tenacious Scorer"
    },
    "Franco Colapinto": {
        "team": "BWT Alpine F1 Team",
        "role": "Race Driver",
        "number": 43,
        "team_color": "#FF87BC",
        "pace_delta": -0.08,
        "deg_multiplier": 1.02,
        "risk_multiplier": 1.12,
        "qualifying_rating": 92,
        "tyre_mgmt_rating": 88,
        "wet_weather_rating": 88,
        "badge": "🇦🇷 COL #43",
        "style": "Fearless Braking & Electric Overtakes"
    },
    "Paul Aron": {
        "team": "BWT Alpine F1 Team",
        "role": "Reserve Driver",
        "number": 61,
        "team_color": "#FF87BC",
        "pace_delta": +0.02,
        "deg_multiplier": 1.05,
        "risk_multiplier": 1.15,
        "qualifying_rating": 91,
        "tyre_mgmt_rating": 86,
        "wet_weather_rating": 86,
        "badge": "🇪🇪 ARO #61 [RESERVE]",
        "style": "F2 Pole Master & Rapid Out-Lap Attack"
    },
    "Kush Maini": {
        "team": "BWT Alpine F1 Team",
        "role": "Reserve Driver",
        "number": 9,
        "team_color": "#FF87BC",
        "pace_delta": +0.06,
        "deg_multiplier": 1.04,
        "risk_multiplier": 1.08,
        "qualifying_rating": 89,
        "tyre_mgmt_rating": 87,
        "wet_weather_rating": 85,
        "badge": "🇮🇳 MAI #9 [RESERVE]",
        "style": "F2 Front-Runner & High Technical Feedback"
    },

    # =========================================================================
    # 8. MONEYGRAM HAAS F1 TEAM
    # =========================================================================
    "Esteban Ocon": {
        "team": "MoneyGram Haas F1 Team",
        "role": "Race Driver",
        "number": 31,
        "team_color": "#B6BABD",
        "pace_delta": -0.08,
        "deg_multiplier": 0.95,
        "risk_multiplier": 1.10,
        "qualifying_rating": 91,
        "tyre_mgmt_rating": 91,
        "wet_weather_rating": 94,
        "badge": "🇫🇷 OCO #31",
        "style": "Iron Defense & Wet Specialist"
    },
    "Oliver Bearman": {
        "team": "MoneyGram Haas F1 Team",
        "role": "Race Driver",
        "number": 87,
        "team_color": "#B6BABD",
        "pace_delta": -0.06,
        "deg_multiplier": 1.02,
        "risk_multiplier": 1.10,
        "qualifying_rating": 91,
        "tyre_mgmt_rating": 89,
        "wet_weather_rating": 88,
        "badge": "🇬🇧 BEA #87",
        "style": "Bold Wheel-to-Wheel Instincts"
    },
    "Jack Doohan": {
        "team": "MoneyGram Haas F1 Team",
        "role": "Reserve Driver",
        "number": 8,
        "team_color": "#B6BABD",
        "pace_delta": +0.00,
        "deg_multiplier": 1.06,
        "risk_multiplier": 1.14,
        "qualifying_rating": 89,
        "tyre_mgmt_rating": 87,
        "wet_weather_rating": 86,
        "badge": "🇦🇺 DOO #8 [RESERVE]",
        "style": "Aggressive Braking & Fast Turn-in"
    },
    "Ryo Hirakawa": {
        "team": "MoneyGram Haas F1 Team",
        "role": "Reserve Driver",
        "number": 17,
        "team_color": "#B6BABD",
        "pace_delta": +0.05,
        "deg_multiplier": 0.95,
        "risk_multiplier": 0.90,
        "qualifying_rating": 87,
        "tyre_mgmt_rating": 93,
        "wet_weather_rating": 91,
        "badge": "🇯🇵 HIR #17 [RESERVE]",
        "style": "WEC World Champion & Tire Preservation"
    },

    # =========================================================================
    # 9. WILLIAMS RACING
    # =========================================================================
    "Alex Albon": {
        "team": "Williams Racing",
        "role": "Race Driver",
        "number": 23,
        "team_color": "#64C4FF",
        "pace_delta": -0.12,
        "deg_multiplier": 0.91,
        "risk_multiplier": 0.95,
        "qualifying_rating": 93,
        "tyre_mgmt_rating": 94,
        "wet_weather_rating": 90,
        "badge": "🇹🇭 ALB #23",
        "style": "Heroic Stint Extension & Tire Whisperer"
    },
    "Carlos Sainz Jr.": {
        "team": "Williams Racing",
        "role": "Race Driver",
        "number": 55,
        "team_color": "#64C4FF",
        "pace_delta": -0.18,
        "deg_multiplier": 0.88,
        "risk_multiplier": 0.88,
        "qualifying_rating": 95,
        "tyre_mgmt_rating": 96,
        "wet_weather_rating": 91,
        "badge": "🇪🇸 SAI #55",
        "style": "Smooth Operator & Tactical Strategist"
    },
    "Luke Browning": {
        "team": "Williams Racing",
        "role": "Reserve Driver",
        "number": 45,
        "team_color": "#64C4FF",
        "pace_delta": +0.05,
        "deg_multiplier": 1.04,
        "risk_multiplier": 1.08,
        "qualifying_rating": 88,
        "tyre_mgmt_rating": 87,
        "wet_weather_rating": 87,
        "badge": "🇬🇧 BRO #45 [RESERVE]",
        "style": "Macau GP Winner & Street Circuit Specialist"
    },
    "Victor Martins": {
        "team": "Williams Racing",
        "role": "Development Driver",
        "number": 25,
        "team_color": "#64C4FF",
        "pace_delta": +0.02,
        "deg_multiplier": 1.06,
        "risk_multiplier": 1.15,
        "qualifying_rating": 91,
        "tyre_mgmt_rating": 85,
        "wet_weather_rating": 85,
        "badge": "🇫🇷 MAR #25 [DEV]",
        "style": "F3 Champion & Outright Single-Lap Pace"
    },

    # =========================================================================
    # 10. AUDI SPORT F1 TEAM
    # =========================================================================
    "Nico Hülkenberg": {
        "team": "Audi Sport F1 Team",
        "role": "Race Driver",
        "number": 27,
        "team_color": "#52E252",
        "pace_delta": -0.15,
        "deg_multiplier": 0.95,
        "risk_multiplier": 0.92,
        "qualifying_rating": 95,
        "tyre_mgmt_rating": 91,
        "wet_weather_rating": 93,
        "badge": "🇩🇪 HUL #27",
        "style": "Saturday Qualifying Wizard & Steady Pacing"
    },
    "Gabriel Bortoleto": {
        "team": "Audi Sport F1 Team",
        "role": "Race Driver",
        "number": 5,
        "team_color": "#52E252",
        "pace_delta": +0.00,
        "deg_multiplier": 1.03,
        "risk_multiplier": 1.08,
        "qualifying_rating": 90,
        "tyre_mgmt_rating": 87,
        "wet_weather_rating": 86,
        "badge": "🇧🇷 BOR #5",
        "style": "F2/F3 Champion & Clinical Overtaking"
    },
    "Ralph Boschung": {
        "team": "Audi Sport F1 Team",
        "role": "Development Driver",
        "number": 35,
        "team_color": "#52E252",
        "pace_delta": +0.09,
        "deg_multiplier": 0.98,
        "risk_multiplier": 0.95,
        "qualifying_rating": 86,
        "tyre_mgmt_rating": 89,
        "wet_weather_rating": 87,
        "badge": "🇨🇭 BOS #35 [DEV]",
        "style": "Experienced Simulator Tester & Baseline Calibrator"
    },

    # =========================================================================
    # 11. CADILLAC FORMULA 1 TEAM (11TH TEAM - 22 CARS GRID!)
    # =========================================================================
    "Sergio Pérez": {
        "team": "Cadillac Formula 1 Team",
        "role": "Race Driver",
        "number": 11,
        "team_color": "#C49A45",
        "pace_delta": -0.11,
        "deg_multiplier": 0.85,
        "risk_multiplier": 0.95,
        "qualifying_rating": 91,
        "tyre_mgmt_rating": 97,
        "wet_weather_rating": 92,
        "badge": "🇲🇽 PER #11",
        "style": "Minister of Defense & Legendary Tyre Conserver"
    },
    "Valtteri Bottas": {
        "team": "Cadillac Formula 1 Team",
        "role": "Race Driver",
        "number": 77,
        "team_color": "#C49A45",
        "pace_delta": -0.14,
        "deg_multiplier": 0.92,
        "risk_multiplier": 0.90,
        "qualifying_rating": 94,
        "tyre_mgmt_rating": 91,
        "wet_weather_rating": 90,
        "badge": "🇫🇮 BOT #77",
        "style": "Clean Air Pace & Elite Qualifying Lap"
    },
    "Guanyu Zhou": {
        "team": "Cadillac Formula 1 Team",
        "role": "Reserve Driver",
        "number": 24,
        "team_color": "#C49A45",
        "pace_delta": +0.02,
        "deg_multiplier": 0.98,
        "risk_multiplier": 0.95,
        "qualifying_rating": 89,
        "tyre_mgmt_rating": 90,
        "wet_weather_rating": 88,
        "badge": "🇨🇳 ZHO #24 [RESERVE]",
        "style": "Solid Racecraft & Street Circuit Pacing"
    },
    "Colton Herta": {
        "team": "Cadillac Formula 1 Team",
        "role": "Test Driver",
        "number": 26,
        "team_color": "#C49A45",
        "pace_delta": -0.06,
        "deg_multiplier": 1.12,
        "risk_multiplier": 1.25,
        "qualifying_rating": 93,
        "tyre_mgmt_rating": 84,
        "wet_weather_rating": 88,
        "badge": "🇺🇸 HER #26 [TEST]",
        "style": "Raw IndyCar Speed & Fearless Attacker"
    },
    "Pietro Fittipaldi": {
        "team": "Cadillac Formula 1 Team",
        "role": "Development Driver",
        "number": 51,
        "team_color": "#C49A45",
        "pace_delta": +0.07,
        "deg_multiplier": 1.01,
        "risk_multiplier": 1.06,
        "qualifying_rating": 87,
        "tyre_mgmt_rating": 88,
        "wet_weather_rating": 88,
        "badge": "🇧🇷 FIT #51 [DEV]",
        "style": "Experienced Multi-Category Test Driver"
    }
}


# -----------------------------------------------------------------------------
# 4. TYRE COMPOUND SPECIFICATIONS
# -----------------------------------------------------------------------------
TYRES = {
    "Soft": {
        "symbol": "S",
        "weather_profile": "Dry",
        "pace_delta": -0.60,
        "base_deg": 0.080,
        "color": "#ef4444"
    },
    "Medium": {
        "symbol": "M",
        "weather_profile": "Dry",
        "pace_delta": 0.00,
        "base_deg": 0.050,
        "color": "#f59e0b"
    },
    "Hard": {
        "symbol": "H",
        "weather_profile": "Dry",
        "pace_delta": 0.60,
        "base_deg": 0.030,
        "color": "#e2e8f0"
    },
    "Inter": {
        "symbol": "I",
        "weather_profile": "Damp",
        "pace_delta": 3.80,
        "base_deg": 0.060,
        "color": "#10b981"
    },
    "Wet": {
        "symbol": "W",
        "weather_profile": "Heavy Rain",
        "pace_delta": 8.50,
        "base_deg": 0.040,
        "color": "#3b82f6"
    }
}


# -----------------------------------------------------------------------------
# 5. PHYSICAL LAP TIME & TRAFFIC MECHANICS
# -----------------------------------------------------------------------------
def format_lap_time(seconds):
    """Convert float seconds to M:SS.mmm format."""
    minutes = int(seconds // 60)
    rem = seconds % 60
    return f"{minutes}:{rem:06.3f}"


def calculate_grid_traffic_delta(grid_pos, current_lap):
    """
    Simulates dirty air aero wake and DRS train traffic based on starting position (P1 to P22).
    - P1-P2: Clean air bonus (-0.22s) in first stint.
    - P3-P6: Front pack slipstream (+0.10s).
    - P7-P16: Midfield dirty air & DRS trains (+0.38s, +15% tyre slide wear).
    - P17-P22: Deep traffic DRS congestion (+0.55s, +20% tyre sliding).
    """
    if current_lap > 25:
        # Field spreads out later in the race
        return 0.05 if grid_pos > 11 else 0.0, 1.0

    if grid_pos <= 2:
        return -0.22, 0.92  # Clean air efficiency
    elif grid_pos <= 6:
        return +0.10, 1.02
    elif grid_pos <= 16:
        return +0.38, 1.15  # Dirty air sliding
    else:
        return +0.55, 1.20  # Deep traffic DRS train


def calculate_lap_time(base_lap_time, tyre_compound, tyre_age, current_lap, total_laps,
                       track_temp, track_weather, driver_profile, grid_pos=1, neutralization=None):
    """
    Full Physical lap time calculation incorporating:
    - Driver Pace Delta & Degradation Multiplier
    - Grid Position Dirty Air & Aerodynamic Wake Penalties (P1-P22)
    - Thermal blistering (>40°C on Soft) & Cold grip loss (<25°C on Hard)
    - Linear Fuel mass burn (1.9 kg/lap @ 0.035 s/kg benefit)
    - Weather dampness mismatch penalty (18s)
    - SC (+40s pacing, -80% deg) / VSC (+20s pacing, -50% deg)
    """
    spec = TYRES[tyre_compound]
    traffic_time_delta, traffic_deg_mult = calculate_grid_traffic_delta(grid_pos, current_lap)
    compound_base = base_lap_time + spec["pace_delta"] + driver_profile["pace_delta"] + traffic_time_delta

    # 1. Thermal Degradation Rate
    deg_rate = spec["base_deg"] * driver_profile["deg_multiplier"] * traffic_deg_mult
    if tyre_compound == "Soft" and track_temp > 40.0:
        deg_rate *= 1.20  # +20% blistering penalty

    # 2. Hard cold tire warm-up deficit (<25°C)
    thermal_penalty = 0.0
    if tyre_compound == "Hard" and track_temp < 25.0:
        thermal_penalty = 0.85

    # 3. Neutralization scaling
    if neutralization == "SC":
        effective_deg = deg_rate * 0.20
    elif neutralization == "VSC":
        effective_deg = deg_rate * 0.50
    else:
        effective_deg = deg_rate

    tyre_wear_penalty = effective_deg * tyre_age

    # 4. Linear Fuel Burn-off (saves ~0.0665 s/lap)
    fuel_burned_kg = max(0, (current_lap - 1)) * 1.9
    fuel_time_saving = fuel_burned_kg * 0.035

    # 5. Weather mismatch penalty (18.0s)
    norm_w = "Heavy Rain" if track_weather in ("Heavy Rain", "Wet") else track_weather
    weather_penalty = 18.0 if spec["weather_profile"] != norm_w else 0.0

    # 6. Neutralization pacing caps
    if neutralization == "SC":
        final_time = base_lap_time + 40.0
    elif neutralization == "VSC":
        final_time = base_lap_time + 20.0
    else:
        final_time = compound_base + tyre_wear_penalty - fuel_time_saving + thermal_penalty + weather_penalty

    return max(30.0, final_time)


def calculate_sector_splits(lap_time):
    """Tri-sector telemetry breakdown: S1 33%, S2 34%, S3 33%."""
    s1 = lap_time * 0.33
    s2 = lap_time * 0.34
    s3 = lap_time - s1 - s2
    return s1, s2, s3


def calculate_race_disruptions(track_data, weather_state, track_temp, driver_profile, grid_pos=1):
    """Calculate scaled race interruption probabilities incorporating grid position hazard."""
    base_sc = track_data.get("sc_risk", 0.35)
    w_norm = weather_state.title()
    w_prem = 0.15 if "Damp" in w_norm else (0.35 if "Heavy" in w_norm or "Wet" in w_norm else 0.0)
    t_prem = 0.10 if track_temp > 42.0 else 0.0
    
    # Midfield grid position (P7-P18) suffers higher Lap 1 crash risk
    grid_prem = 0.08 if 7 <= grid_pos <= 18 else 0.0

    scaled_prob = min(0.99, max(0.05, (base_sc + w_prem + t_prem + grid_prem) * driver_profile["risk_multiplier"]))
    total_laps = track_data.get("race_laps", 53)

    p_lap = 1.0 - (1.0 - scaled_prob) ** (1.0 / total_laps)
    p_lap1 = min(0.95, (2.4 if 7 <= grid_pos <= 18 else 2.0) * p_lap)
    exact_prob = 1.0 - (1.0 - p_lap1) * ((1.0 - p_lap) ** max(1, (total_laps - 1)))

    return {
        "base_sc": base_sc,
        "w_prem": w_prem,
        "t_prem": t_prem,
        "scaled_prob": scaled_prob,
        "exact_prob": exact_prob,
        "p_lap": p_lap,
        "p_lap1": p_lap1
    }


def compute_best_tyre_strategy(circuit_data, weather_state, track_temp, driver_profile, grid_pos):
    """
    Computes the optimal strategy recommendation, exact pit windows, and contingencies.
    """
    total_laps = circuit_data["race_laps"]
    
    if weather_state == "Heavy Rain":
        plan_a_name = "WET ➔ INTER (1-STOP RAIN PIVOT)"
        stints = [("Wet", max(1, int(total_laps * 0.45))), ("Inter", total_laps - int(total_laps * 0.45))]
        pit_window = f"Laps {int(total_laps * 0.40)} – {int(total_laps * 0.50)}"
        nominal_lap = int(total_laps * 0.45)
        undercut_note = "Watch intermediate crossover time (~112% of dry pace) to jump rivals."
    elif weather_state == "Damp":
        plan_a_name = "INTER ➔ MEDIUM (SLICK CROSSOVER 1-STOP)"
        stints = [("Inter", max(1, int(total_laps * 0.40))), ("Medium", total_laps - int(total_laps * 0.40))]
        pit_window = f"Laps {int(total_laps * 0.35)} – {int(total_laps * 0.45)}"
        nominal_lap = int(total_laps * 0.38)
        undercut_note = "Massive +3.0s/lap gain once dry line appears. Call box at first dry apex."
    else:
        # Dry track
        if track_temp > 40:
            # Extreme heat favours Hard compounds
            if grid_pos >= 11:
                plan_a_name = "HARD ➔ MEDIUM (REVERSE OVERCUT OFF-SET)"
                first_len = int(total_laps * 0.62)
                stints = [("Hard", first_len), ("Medium", total_laps - first_len)]
                pit_window = f"Laps {first_len - 3} – {first_len + 2}"
                nominal_lap = first_len
                undercut_note = "Overcut favoured: Run in clean air while midfield pits into traffic."
            else:
                plan_a_name = "MEDIUM ➔ HARD (1-STOP THERMAL DEFENSE)"
                first_len = int(total_laps * 0.42)
                stints = [("Medium", first_len), ("Hard", total_laps - first_len)]
                pit_window = f"Laps {first_len - 2} – {first_len + 3}"
                nominal_lap = first_len
                undercut_note = "Undercut is POTENT: +1.65s delta on fresh Hards against worn Mediums."
        else:
            # Nominal track temp
            if grid_pos <= 4:
                plan_a_name = "MEDIUM ➔ HARD (1-STOP CONTROL STRATEGY)"
                first_len = int(total_laps * 0.45)
                stints = [("Medium", first_len), ("Hard", total_laps - first_len)]
                pit_window = f"Laps {first_len - 2} – {first_len + 2}"
                nominal_lap = first_len
                undercut_note = "Control the race pace from the front; cover the P2 undercut window."
            elif grid_pos >= 12:
                plan_a_name = "HARD ➔ SOFT (LONG-STINT ATTACK CONTINGENCY)"
                first_len = int(total_laps * 0.68)
                stints = [("Hard", first_len), ("Soft", total_laps - first_len)]
                pit_window = f"Laps {first_len - 3} – {first_len + 2}"
                nominal_lap = first_len
                undercut_note = "Target late-race Safety Car to leapfrog the pack on fresh Soft rubber."
            else:
                plan_a_name = "SOFT ➔ MEDIUM ➔ HARD (2-STOP AGGRESSIVE ATTACK)" if circuit_data["pit_loss"] < 22 else "MEDIUM ➔ HARD (1-STOP OPTIMAL)"
                first_len = int(total_laps * 0.44)
                stints = [("Medium", first_len), ("Hard", total_laps - first_len)]
                pit_window = f"Laps {first_len - 2} – {first_len + 3}"
                nominal_lap = first_len
                undercut_note = "Undercut window opens Lap " + str(first_len - 2) + ". Fresh tyres yield +1.4s."

    plan_b = f"SAFETY CAR PIVOT: If SC deploys before Lap {int(total_laps * 0.35)}, box immediately for Hard tyres (saves ~11.5s pit loss delta)."

    return {
        "plan_a_name": plan_a_name,
        "stints": stints,
        "pit_window": pit_window,
        "nominal_lap": nominal_lap,
        "undercut_note": undercut_note,
        "plan_b": plan_b
    }


def run_fast_monte_carlo(remaining_laps, current_lap_idx, starting_compound, starting_tyre_age,
                         candidate_strategies, base_lap_time, pit_loss, track_temp,
                         track_weather, driver_profile, risk_profile, grid_pos=1, iterations=1000):
    """Simulates 1,000 Monte Carlo race scenarios from current_lap to end of race."""
    p_lap = risk_profile["p_lap"]
    p_lap1 = risk_profile["p_lap1"]
    total_laps = current_lap_idx + remaining_laps

    scenarios = []
    for _ in range(iterations):
        events = {}
        lap = current_lap_idx
        while lap <= total_laps:
            prob = p_lap1 if lap == 1 else p_lap
            if random.random() < prob:
                roll = random.random()
                dur = 2 if roll < 0.15 else (3 if roll < 0.85 else 1)
                typ = "VSC" if roll < 0.15 else ("SC" if roll < 0.85 else "RED_FLAG")
                for d in range(dur):
                    if lap + d <= total_laps:
                        events[lap + d] = "RED_FLAG" if (typ == "RED_FLAG" and d == 0) else ("SC" if typ in ("SC", "RED_FLAG") else "VSC")
                lap += dur
            else:
                lap += 1
        scenarios.append(events)

    scenario_winners = [None] * iterations
    scenario_best_times = [float("inf")] * iterations
    results = []

    for strat in candidate_strategies:
        times = []
        for s_idx, event_map in enumerate(scenarios):
            sim_time = 0.0
            c_comp = starting_compound
            c_age = starting_tyre_age
            plan_idx = 0

            stint_len = max(1, remaining_laps // max(1, len(strat)))
            stint_counter = 0

            for l in range(current_lap_idx, total_laps + 1):
                ev = event_map.get(l, None)
                if ev == "RED_FLAG":
                    c_age = 0

                lap_t = calculate_lap_time(
                    base_lap_time=base_lap_time,
                    tyre_compound=c_comp,
                    tyre_age=c_age,
                    current_lap=l,
                    total_laps=total_laps,
                    track_temp=track_temp,
                    track_weather=track_weather,
                    driver_profile=driver_profile,
                    grid_pos=grid_pos,
                    neutralization=ev if ev in ("SC", "VSC") else None
                )
                sim_time += lap_t
                c_age += 1
                stint_counter += 1

                # Check planned box
                if plan_idx < len(strat) - 1 and stint_counter >= stint_len and l < total_laps:
                    sim_time += pit_loss
                    plan_idx += 1
                    c_comp = strat[plan_idx]
                    c_age = 0
                    stint_counter = 0

            times.append(sim_time)
            if sim_time < scenario_best_times[s_idx]:
                scenario_best_times[s_idx] = sim_time
                scenario_winners[s_idx] = " → ".join(strat)

        mean_t = sum(times) / iterations
        results.append({
            "strategy": " → ".join(strat),
            "mean_time": mean_t,
            "wins": 0
        })

    for winner in scenario_winners:
        if winner:
            for r in results:
                if r["strategy"] == winner:
                    r["wins"] += 1
                    break

    for r in results:
        r["win_rate"] = (r["wins"] / iterations) * 100.0

    results.sort(key=lambda x: x["mean_time"])
    return results


# -----------------------------------------------------------------------------
# 6. ASYNCHRONOUS GENERATOR SIMULATION FUNCTION
# -----------------------------------------------------------------------------
def stream_race_laps(circuit_data, driver_profile, track_temp, track_weather,
                     initial_strategy, p_lap, p_lap1, grid_pos=1, start_lap=1,
                     current_fuel=None, current_stint_idx=0,
                     current_compound=None, tyre_age=0, stint_lap_counter=0,
                     current_flag="GREEN", flag_remaining_laps=0,
                     override_active=False, override_compound=None):
    """
    Python generator function that yields lap-by-lap telemetry records in real time.
    Supports starting from any lap to allow seamless pause / resume and pit overrides.
    """
    total_laps = circuit_data["race_laps"]
    base_lap_time = circuit_data["base_pace"]
    pit_loss = circuit_data["pit_loss"]

    stint_count = len(initial_strategy)
    base_stint_laps = max(1, total_laps // stint_count)
    remainder_laps = total_laps % stint_count
    stint_lengths = [base_stint_laps + (1 if i < remainder_laps else 0) for i in range(stint_count)]

    starting_fuel = (total_laps * 1.9) + 2.5
    if current_fuel is None:
        current_fuel = starting_fuel - ((start_lap - 1) * 1.9)

    if current_compound is None:
        current_compound = initial_strategy[current_stint_idx]

    for lap in range(start_lap, total_laps + 1):
        incident_triggered = False

        # 1. Roll Monte Carlo incident if currently Green Flag
        if flag_remaining_laps <= 0:
            current_flag = "GREEN"
            prob = p_lap1 if lap == 1 else p_lap
            if random.random() < prob:
                incident_triggered = True
                roll = random.random()
                if roll < 0.15:
                    current_flag = "VSC"
                    flag_remaining_laps = 2
                elif roll < 0.85:
                    current_flag = "SC"
                    flag_remaining_laps = 3
                else:
                    current_flag = "RED_FLAG"
                    flag_remaining_laps = 1
        else:
            flag_remaining_laps -= 1

        # 2. Check for Red Flag free tyre reset
        if current_flag == "RED_FLAG":
            tyre_age = 0

        # 3. Check Strategic Override Pit Call vs Scheduled Pit Stop
        is_pit_lap = False
        pit_time_loss = 0.0

        if override_active and override_compound:
            is_pit_lap = True
            current_compound = override_compound
            tyre_age = 0
            stint_lap_counter = 0
            pit_time_loss = pit_loss
            override_active = False  # Consumed
        elif (current_stint_idx < stint_count - 1 and
              stint_lap_counter >= stint_lengths[min(current_stint_idx, len(stint_lengths)-1)] and
              lap < total_laps):
            is_pit_lap = True
            current_stint_idx += 1
            current_compound = initial_strategy[min(current_stint_idx, len(initial_strategy)-1)]
            tyre_age = 0
            stint_lap_counter = 0
            pit_time_loss = pit_loss

        # 4. Calculate Lap Time
        lap_time = calculate_lap_time(
            base_lap_time=base_lap_time,
            tyre_compound=current_compound,
            tyre_age=tyre_age,
            current_lap=lap,
            total_laps=total_laps,
            track_temp=track_temp,
            track_weather=track_weather,
            driver_profile=driver_profile,
            grid_pos=grid_pos,
            neutralization=current_flag if current_flag in ("SC", "VSC") else None
        )
        if is_pit_lap:
            lap_time += pit_time_loss

        s1, s2, s3 = calculate_sector_splits(lap_time)

        # 5. Burn Fuel
        current_fuel = max(2.0, starting_fuel - (lap * 1.9))

        wear_pct = min(100.0, (tyre_age * TYRES[current_compound]["base_deg"] * driver_profile["deg_multiplier"] / 1.5) * 100.0)

        record = {
            "lap": lap,
            "total_laps": total_laps,
            "lap_time": lap_time,
            "s1": s1,
            "s2": s2,
            "s3": s3,
            "compound": current_compound,
            "tyre_age": tyre_age,
            "wear_pct": wear_pct,
            "fuel_kg": current_fuel,
            "flag": current_flag,
            "flag_remaining_laps": flag_remaining_laps,
            "is_pit_lap": is_pit_lap,
            "pit_time_loss": pit_time_loss,
            "incident_triggered": incident_triggered,
            "current_stint_idx": current_stint_idx,
            "stint_lap_counter": stint_lap_counter
        }

        tyre_age += 1
        stint_lap_counter += 1

        yield record


# -----------------------------------------------------------------------------
# 7. SESSION STATE INITIALIZATION (CRUD NOTES & ENGINE STATE)
# -----------------------------------------------------------------------------
if "laps_data" not in st.session_state:
    st.session_state.laps_data = []
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "override_active" not in st.session_state:
    st.session_state.override_active = False
if "selected_compound" not in st.session_state:
    st.session_state.selected_compound = "Medium"
if "mc_standings" not in st.session_state:
    st.session_state.mc_standings = []
if "current_flag" not in st.session_state:
    st.session_state.current_flag = "GREEN"
if "active_circuit" not in st.session_state:
    st.session_state.active_circuit = None
if "edit_note_id" not in st.session_state:
    st.session_state.edit_note_id = None

# Initialize Interactive Strategic Engineering Notebook CRUD Data
if "strategic_notes" not in st.session_state:
    st.session_state.strategic_notes = [
        {
            "id": 1,
            "lap": "PRE-RACE",
            "author": "Chief Race Strategist",
            "category": "Pit Window",
            "priority": "CRITICAL",
            "text": "Plan A target: Medium -> Hard 1-stop. Optimal pit window opens Lap 21. If car ahead is within 1.5s, pull trigger on Lap 22 for undercut attack.",
            "time": "14:10:00"
        },
        {
            "id": 2,
            "lap": "LAP 1",
            "author": "Race Engineer",
            "category": "Traffic & Grid",
            "priority": "WARNING",
            "text": "Grid density elevated into Turn 1. Maintain clean air trajectory. Do not over-stress front-left tyre under dirty air wake.",
            "time": "14:15:30"
        },
        {
            "id": 3,
            "lap": "PRE-RACE",
            "author": "Tyre Performance Tech",
            "category": "Thermal Physics",
            "priority": "INFO",
            "text": "Track temperature monitoring active. Soft compound blistering threshold at 40°C. Hard compound warm-up delay expected on cold restarts.",
            "time": "14:18:12"
        }
    ]


# -----------------------------------------------------------------------------
# 8. SIDEBAR CONTROLS & ENVIRONMENT
# -----------------------------------------------------------------------------
st.sidebar.markdown("<h2 style='font-family: Orbitron; color: #ff1801;'>⚙️ PIT-WALL CONTROLS</h2>", unsafe_allow_html=True)

# 1. Circuit Selector
circuit_names = list(ALL_CIRCUITS.keys())
selected_circuit_name = st.sidebar.selectbox("🏁 Championship Circuit", circuit_names, index=0)
circuit_data = ALL_CIRCUITS[selected_circuit_name]

# Reset telemetry if circuit changed
if st.session_state.active_circuit != selected_circuit_name:
    st.session_state.active_circuit = selected_circuit_name
    st.session_state.laps_data = []
    st.session_state.simulation_running = False
    st.session_state.override_active = False
    st.session_state.current_flag = "GREEN"
    st.session_state.mc_standings = []

# 2. 2026 Driver Lineup & Starting Grid Position (22 Cars, 33 Drivers)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏎️ 2026 Driver & Grid Setup (22 Cars)")

role_filter = st.sidebar.radio(
    "Filter Grid / Roster",
    ["All (33 Drivers)", "Race Drivers (22 Cars)", "Official Reserves (11)"],
    horizontal=True
)

if role_filter == "Race Drivers (22 Cars)":
    driver_names = [name for name, d in DRIVERS_2026.items() if d.get("role") == "Race Driver"]
elif role_filter == "Official Reserves (11)":
    driver_names = [name for name, d in DRIVERS_2026.items() if d.get("role") == "Reserve Driver"]
else:
    driver_names = list(DRIVERS_2026.keys())

selected_driver_name = st.sidebar.selectbox(
    "Assigned Driver",
    driver_names,
    index=0,
    format_func=lambda name: f"{name} ({DRIVERS_2026[name]['team']} #{DRIVERS_2026[name]['number']}) [{'RACE' if DRIVERS_2026[name].get('role') == 'Race Driver' else 'RESERVE'}]"
)
driver_profile = DRIVERS_2026[selected_driver_name]

grid_position = st.sidebar.slider(
    "Starting Grid Position (Qualifying)",
    min_value=1,
    max_value=22,
    value=1,
    step=1,
    help="P1 = Pole Position (Clean Air). Midfield (P7-P16) experiences dirty air wake (+0.38s lap penalty) and higher Lap 1 crash risk. P17-P22 deep traffic."
)

st.sidebar.markdown(f"""
<div style='background:#111827; border-left:4px solid {driver_profile["team_color"]}; padding:8px 12px; border-radius:6px;'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <b style='color:#f8fafc;'>{driver_profile["team"]}</b>
        <span style='background:{"#10b981" if driver_profile.get("role") == "Race Driver" else "#6366f1"}; color:#ffffff; font-size:0.75rem; font-weight:800; padding:2px 6px; border-radius:4px;'>{driver_profile.get("role", "Race Driver").upper()}</span>
    </div>
    <span style='color:#94a3b8; font-size:0.9rem;'>{driver_profile["badge"]} │ Style: {driver_profile["style"]}</span><br>
    <span style='color:#38bdf8; font-size:0.85rem;'>Quali: {driver_profile["qualifying_rating"]} │ Tyre Mgmt: {driver_profile["tyre_mgmt_rating"]} │ Wet: {driver_profile["wet_weather_rating"]}</span>
</div>
""", unsafe_allow_html=True)

# 3. Real-Time Meteorology & Weather Options
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌦️ Real-Time Track Meteorology")

weather_input_mode = st.sidebar.radio("Weather Control Mode", ["Weather Presets", "Custom Engineering Input"], index=0)

if weather_input_mode == "Weather Presets":
    preset_choice = st.sidebar.selectbox(
        "Live Track Condition Preset",
        [
            "☀️ Dry & Sunny (Surface 38°C, Moisture 0%)",
            "🔥 Extreme Heat (Surface 46°C, Blistering Risk)",
            "❄️ Cold Track (Surface 21°C, Hard Grip Loss)",
            "🌦️ Greasy Damp (Surface 26°C, Inter Crossover)",
            "🌧️ Monsoon Heavy Rain (Surface 22°C, Full Wet)",
            "⛈️ Dynamic Incoming Rain Shower (Rain on Lap 18)"
        ],
        index=0
    )
    if "Extreme Heat" in preset_choice:
        weather_state = "Dry"
        track_temp = 46
        track_moisture = 0
        ambient_temp = 34
    elif "Cold Track" in preset_choice:
        weather_state = "Dry"
        track_temp = 21
        track_moisture = 5
        ambient_temp = 16
    elif "Greasy Damp" in preset_choice:
        weather_state = "Damp"
        track_temp = 26
        track_moisture = 45
        ambient_temp = 21
    elif "Monsoon" in preset_choice:
        weather_state = "Heavy Rain"
        track_temp = 22
        track_moisture = 85
        ambient_temp = 19
    elif "Incoming Rain" in preset_choice:
        curr_l = len(st.session_state.laps_data)
        if curr_l >= 18:
            weather_state = "Damp"
            track_temp = 25
            track_moisture = 55
            ambient_temp = 20
        else:
            weather_state = "Dry"
            track_temp = 36
            track_moisture = 0
            ambient_temp = 27
    else:
        weather_state = "Dry"
        track_temp = 38
        track_moisture = 0
        ambient_temp = 26
else:
    col_w1, col_w2 = st.sidebar.columns(2)
    with col_w1:
        ambient_temp = st.number_input("Ambient (°C)", min_value=10, max_value=45, value=28)
    with col_w2:
        track_temp = st.slider("Track Surface (°C)", min_value=20, max_value=50, value=38)
    track_moisture = st.sidebar.slider("Track Moisture / Dampness (%)", min_value=0, max_value=100, value=0)
    rain_prob = st.sidebar.slider("Rain Probability (%)", min_value=0, max_value=100, value=10)
    wind_speed = st.sidebar.slider("Wind Speed (km/h)", min_value=0, max_value=60, value=14)

    if track_moisture > 60:
        weather_state = "Heavy Rain"
    elif track_moisture > 20:
        weather_state = "Damp"
    else:
        weather_state = "Dry"

# Thermal Warnings
if track_temp > 40:
    st.sidebar.warning("⚠️ High Blistering Risk: Soft Compound Wear +20%")
elif track_temp < 25:
    st.sidebar.info("❄️ Cold Track Warning: Hard Compound Grip Deficit -15%")

# 4. Strategy Permutations
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏎️ Baseline Race Strategy")
if weather_state == "Dry":
    candidate_strats = [["Soft", "Medium"], ["Medium", "Hard"], ["Soft", "Hard"], ["Medium", "Medium"], ["Soft", "Medium", "Soft"]]
elif weather_state == "Damp":
    candidate_strats = [["Inter", "Inter"], ["Inter", "Medium"], ["Inter", "Inter", "Inter"]]
else:
    candidate_strats = [["Wet", "Wet"], ["Wet", "Inter"], ["Wet", "Wet", "Wet"]]

initial_strategy_idx = st.sidebar.selectbox("Initial Strategy Call", range(len(candidate_strats)), format_func=lambda x: " → ".join(candidate_strats[x]))
selected_strategy = candidate_strats[initial_strategy_idx]

# 5. Simulation Speed & Automation
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Stream Dynamics")
sim_delay = st.sidebar.slider("Simulation Stream Latency (s/lap)", min_value=0.01, max_value=0.35, value=0.06, step=0.01)
auto_pause = st.sidebar.checkbox("Auto-Pause on Incidents (SC / Red Flag)", value=True,
                                 help="Automatically halts the live stream when a Safety Car or Red Flag is deployed so the pit-wall can issue tactical overrides.")


# -----------------------------------------------------------------------------
# 9. MAIN RACE COMMAND CENTER PANEL & TELEMETRY
# -----------------------------------------------------------------------------
st.markdown("<div class='f1-header-title'>🏎️ F1-AI-RACE-ENGINEER : PIT-WALL COMMAND CENTER</div>", unsafe_allow_html=True)
st.markdown(f"<div class='f1-sub-title'>LIVE TELEMETRY ENGINE │ {circuit_data['event_name'].upper()} ({circuit_data['country'].upper()}) │ {driver_profile['team'].upper()} │ {driver_profile['badge']} │ GRID: P{grid_position}</div>", unsafe_allow_html=True)

# Risk Assessment Calculation
risk_profile = calculate_race_disruptions(circuit_data, weather_state, track_temp, driver_profile, grid_pos=grid_position)

# Pre-Compute Optimal Tyre Strategy Recommendation Box
best_strat = compute_best_tyre_strategy(circuit_data, weather_state, track_temp, driver_profile, grid_position)

# -----------------------------------------------------------------------------
# 10. PROMINENT BEST TYRE STRATEGY & OPTIMAL PIT WINDOW BOX
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class='best-strategy-box'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <div class='best-strategy-title'>🎯 RECOMMENDED STRATEGY CALL: {best_strat['plan_a_name']}</div>
        <span style='background:#00f2fe; color:#0b0e14; padding:4px 12px; border-radius:4px; font-weight:800; font-size:0.9rem;'>AI CONFIDENCE: 94.6%</span>
    </div>
    <div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-top:10px;'>
        <div style='background:rgba(0,0,0,0.3); padding:10px 14px; border-radius:6px; border:1px solid #1e293b;'>
            <div class='kpi-title'>Optimal Pit Window</div>
            <div style='font-size:1.35rem; font-weight:700; color:#38bdf8;'>{best_strat['pit_window']}</div>
            <span style='color:#94a3b8; font-size:0.85rem;'>Target In-Lap: <b>Lap {best_strat['nominal_lap']}</b></span>
        </div>
        <div style='background:rgba(0,0,0,0.3); padding:10px 14px; border-radius:6px; border:1px solid #1e293b;'>
            <div class='kpi-title'>Undercut / Overcut Potency</div>
            <div style='font-size:1.15rem; font-weight:700; color:#f59e0b;'>{best_strat['undercut_note'][:36]}...</div>
            <span style='color:#94a3b8; font-size:0.85rem;'>{best_strat['undercut_note']}</span>
        </div>
        <div style='background:rgba(0,0,0,0.3); padding:10px 14px; border-radius:6px; border:1px solid #1e293b;'>
            <div class='kpi-title'>Contingency Plan B (Safety Car Pivot)</div>
            <div style='font-size:1.1rem; font-weight:700; color:#10b981;'>Cheap Pit Stop Delta: -11.5s</div>
            <span style='color:#94a3b8; font-size:0.85rem;'>{best_strat['plan_b']}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Status Telemetry KPI Cards
col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

with col_metric1:
    st.markdown("<div class='status-card'><div class='kpi-title'>Circuit Baseline Pace</div>"
                f"<div class='kpi-val'>{circuit_data['base_pace']:.3f}s</div>"
                f"<span style='color: #64748b;'>{format_lap_time(circuit_data['base_pace'])}</span></div>", unsafe_allow_html=True)

with col_metric2:
    ph_flag = st.empty()
    curr_fl = st.session_state.current_flag
    if curr_fl == "SC":
        flag_badge = "<span class='flag-yellow'>🟨 FULL SAFETY CAR</span>"
    elif curr_fl == "VSC":
        flag_badge = "<span class='flag-yellow'>🟡 VSC ACTIVE</span>"
    elif curr_fl == "RED_FLAG":
        flag_badge = "<span class='flag-red'>🔴 RED FLAG SUSPENSION</span>"
    else:
        flag_badge = "<span class='flag-green'>🟢 GREEN FLAG</span>"

    ph_flag.markdown(f"<div class='status-card'><div class='kpi-title'>Live Track Neutralization</div>"
                     f"<div style='margin-top:6px;'>{flag_badge}</div></div>", unsafe_allow_html=True)

with col_metric3:
    st.markdown("<div class='status-card'><div class='kpi-title'>Pre-Race Risk Assessment</div>"
                f"<div class='kpi-val'>{risk_profile['exact_prob']*100:.1f}%</div>"
                f"<span style='color: #64748b;'>Interruption Probability (Grid P{grid_position})</span></div>", unsafe_allow_html=True)

with col_metric4:
    ph_lap = st.empty()
    curr_lap_num = len(st.session_state.laps_data)
    ph_lap.markdown(f"<div class='status-card'><div class='kpi-title'>Active Race Progress</div>"
                    f"<div class='kpi-val'>LAP {curr_lap_num} / {circuit_data['race_laps']}</div>"
                    f"<span style='color: #64748b;'>Driver: {driver_profile['badge']}</span></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 11. 2026 CAR AERO DYNAMICS & CORNER SPEED BREAKDOWN
# -----------------------------------------------------------------------------
with st.expander("🏎️ 2026 Active Aero Dynamics & Cornering Speeds Telemetry Breakdown", expanded=False):
    col_aero1, col_aero2, col_aero3, col_aero4, col_aero5 = st.columns(5)
    with col_aero1:
        st.metric("Top Speed (X-Mode)", f"{circuit_data['max_straight_speed']} km/h", "Low-Drag Straight")
    with col_aero2:
        st.metric("High-Speed Apex (Z-Mode)", f"{circuit_data['high_speed_apex']} km/h", "Max Downforce Sweeper")
    with col_aero3:
        st.metric("Medium-Speed Apex", f"{circuit_data['medium_speed_apex']} km/h", "Chassis Balance")
    with col_aero4:
        st.metric("Hairpin Apex", f"{circuit_data['low_speed_apex']} km/h", "Mechanical Grip")
    with col_aero5:
        st.metric("Aero Setup Spec", circuit_data['aero_downforce_spec'], circuit_data['tyre_energy_rating'])


# -----------------------------------------------------------------------------
# 12. SPLIT-SECOND STRATEGIC OVERRIDE STATION (INTERRUPTIONS)
# -----------------------------------------------------------------------------
st.markdown("### ⚡ Split-Second Strategic Override Station")

override_col1, override_col2, override_col3 = st.columns([2, 1, 1])

with override_col1:
    override_compound = st.selectbox(
        "Select Compound for Immediate Pit Call",
        ["Soft", "Medium", "Hard", "Inter", "Wet"],
        index=1 if weather_state == "Dry" else (3 if weather_state == "Damp" else 4)
    )

with override_col2:
    box_now = st.button("🚨 BOX THIS LAP (Call Undercut)", use_container_width=True)
    if box_now:
        st.session_state.override_active = True
        st.session_state.selected_compound = override_compound
        st.toast(f"⚡ PIT-WALL CALL: Box this lap for {override_compound} compound!")

with override_col3:
    stay_out = st.button("🛑 STAY OUT (Track Position)", use_container_width=True)
    if stay_out:
        st.session_state.override_active = False
        st.toast("🛡️ STRATEGY CONFIRMED: Stay Out on current compound.")


# Trigger Instant 1,000-Run Monte Carlo Re-Optimization if Override or Disruption
if box_now or stay_out or (st.session_state.current_flag in ("SC", "VSC", "RED_FLAG") and not st.session_state.mc_standings):
    curr_l = max(1, len(st.session_state.laps_data))
    rem_l = max(1, circuit_data["race_laps"] - curr_l)

    comp_choice = override_compound if box_now else (st.session_state.laps_data[-1]["compound"] if st.session_state.laps_data else "Medium")
    candidate_permutations = [
        [comp_choice, "Hard"],
        [comp_choice, "Medium"],
        [comp_choice, "Soft"],
        ["Medium", "Hard"],
        ["Soft", "Medium"]
    ]
    with st.spinner("🎲 Re-running 1,000 Monte Carlo race projections for tactical override..."):
        st.session_state.mc_standings = run_fast_monte_carlo(
            remaining_laps=rem_l,
            current_lap_idx=curr_l,
            starting_compound=comp_choice,
            starting_tyre_age=0 if box_now else (st.session_state.laps_data[-1]["tyre_age"] if st.session_state.laps_data else 5),
            candidate_strategies=candidate_permutations,
            base_lap_time=circuit_data["base_pace"],
            pit_loss=circuit_data["pit_loss"],
            track_temp=track_temp,
            track_weather=weather_state,
            driver_profile=driver_profile,
            risk_profile=risk_profile,
            grid_pos=grid_position,
            iterations=1000
        )


# -----------------------------------------------------------------------------
# 13. SIMULATION STREAM CONTROLS
# -----------------------------------------------------------------------------
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.2, 1, 1, 1])

race_finished = len(st.session_state.laps_data) >= circuit_data["race_laps"]
stream_btn_label = "▶️ Launch Live Stream" if len(st.session_state.laps_data) == 0 else "▶️ Resume Stream"

with btn_col1:
    start_sim = st.button(stream_btn_label, type="primary", disabled=race_finished, use_container_width=True)
with btn_col2:
    step_sim = st.button("⚡ Step 1 Lap", disabled=race_finished, use_container_width=True)
with btn_col3:
    finish_sim = st.button("⏩ Finish Race", disabled=race_finished, use_container_width=True)
with btn_col4:
    reset_sim = st.button("🔄 Reset Race", use_container_width=True)

if reset_sim:
    st.session_state.laps_data = []
    st.session_state.simulation_running = False
    st.session_state.current_flag = "GREEN"
    st.session_state.override_active = False
    st.session_state.mc_standings = []
    st.rerun()


# -----------------------------------------------------------------------------
# 14. STREAMING PLACEHOLDERS FOR PLOTLY TELEMETRY
# -----------------------------------------------------------------------------
chart_row1_col1, chart_row1_col2 = st.columns(2)
chart_row2_col1, chart_row2_col2 = st.columns(2)

with chart_row1_col1:
    chart_lap_times = st.empty()
with chart_row1_col2:
    chart_fuel_burn = st.empty()
with chart_row2_col1:
    chart_sector_splits = st.empty()
with chart_row2_col2:
    chart_tyre_wear = st.empty()


def render_plotly_telemetry(df):
    """Generates and renders interactive Plotly telemetry charts."""
    if df.empty:
        return

    # Chart 1: Lap Times Stream
    fig_laps = go.Figure()
    fig_laps.add_trace(go.Scatter(
        x=df["lap"], y=df["lap_time"],
        mode="lines+markers",
        line=dict(color="#00f2fe", width=2.5),
        marker=dict(size=7, color=[TYRES.get(c, {}).get("color", "#ffffff") for c in df["compound"]]),
        text=[f"Lap {row['lap']}: {row['compound']} ({row['flag']})" for _, row in df.iterrows()],
        hoverinfo="x+y+text",
        name="Lap Time"
    ))
    fig_laps.update_layout(
        title="📈 Live Lap Times Stream (Colored by Compound)",
        template="plotly_dark",
        height=280,
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis_title="Lap Number",
        yaxis_title="Time (s)"
    )
    chart_lap_times.plotly_chart(fig_laps, use_container_width=True)

    # Chart 2: Fuel Mass Drop-off
    fig_fuel = go.Figure()
    fig_fuel.add_trace(go.Scatter(
        x=df["lap"], y=df["fuel_kg"],
        mode="lines",
        line=dict(color="#f59e0b", width=3),
        fill="tozeroy",
        fillcolor="rgba(245, 158, 11, 0.15)",
        name="Fuel Mass"
    ))
    fig_fuel.update_layout(
        title="⛽ Fuel Mass Burn-off Drop-off (kg)",
        template="plotly_dark",
        height=280,
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis_title="Lap Number",
        yaxis_title="Fuel (kg)"
    )
    chart_fuel_burn.plotly_chart(fig_fuel, use_container_width=True)

    # Chart 3: Multi-Sector Splits Breakdown
    fig_sectors = go.Figure()
    fig_sectors.add_trace(go.Scatter(x=df["lap"], y=df["s1"], mode="lines", line=dict(color="#ef4444"), name="Sector 1 (33%)"))
    fig_sectors.add_trace(go.Scatter(x=df["lap"], y=df["s2"], mode="lines", line=dict(color="#10b981"), name="Sector 2 (34%)"))
    fig_sectors.add_trace(go.Scatter(x=df["lap"], y=df["s3"], mode="lines", line=dict(color="#3b82f6"), name="Sector 3 (33%)"))
    fig_sectors.update_layout(
        title="⏱️ Multi-Sector Telemetry Splits",
        template="plotly_dark",
        height=280,
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis_title="Lap Number",
        yaxis_title="Sector Time (s)"
    )
    chart_sector_splits.plotly_chart(fig_sectors, use_container_width=True)

    # Chart 4: Tyre Wear Degradation Percentage
    fig_wear = go.Figure()
    fig_wear.add_trace(go.Scatter(
        x=df["lap"], y=df["wear_pct"],
        mode="lines+markers",
        line=dict(color="#ec4899", width=2.5),
        name="Wear %"
    ))
    fig_wear.update_layout(
        title="🛞 Tyre Degradation Percentage (%)",
        template="plotly_dark",
        height=280,
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis_title="Lap Number",
        yaxis_title="Wear %",
        yaxis=dict(range=[0, 105])
    )
    chart_tyre_wear.plotly_chart(fig_wear, use_container_width=True)


# -----------------------------------------------------------------------------
# 15. RUNNING THE ASYNC GENERATOR STREAM
# -----------------------------------------------------------------------------
last_rec = st.session_state.laps_data[-1] if st.session_state.laps_data else None
next_start_lap = (last_rec["lap"] + 1) if last_rec else 1
cur_fuel = last_rec["fuel_kg"] if last_rec else None
cur_stint = last_rec["current_stint_idx"] if last_rec else 0
cur_comp = last_rec["compound"] if last_rec else selected_strategy[0]
cur_age = last_rec["tyre_age"] if last_rec else 0
cur_stint_cnt = last_rec["stint_lap_counter"] if last_rec else 0
cur_flg = last_rec["flag"] if last_rec else "GREEN"
cur_rem_flg = last_rec.get("flag_remaining_laps", 0) if last_rec else 0

if start_sim or step_sim or finish_sim:
    st.session_state.simulation_running = True
    gen = stream_race_laps(
        circuit_data=circuit_data,
        driver_profile=driver_profile,
        track_temp=track_temp,
        track_weather=weather_state,
        initial_strategy=selected_strategy,
        p_lap=risk_profile["p_lap"],
        p_lap1=risk_profile["p_lap1"],
        grid_pos=grid_position,
        start_lap=next_start_lap,
        current_fuel=cur_fuel,
        current_stint_idx=cur_stint,
        current_compound=cur_comp,
        tyre_age=cur_age,
        stint_lap_counter=cur_stint_cnt,
        current_flag=cur_flg,
        flag_remaining_laps=cur_rem_flg,
        override_active=st.session_state.override_active,
        override_compound=st.session_state.selected_compound
    )

    for lap_record in gen:
        if st.session_state.override_active and lap_record["is_pit_lap"]:
            st.session_state.override_active = False

        st.session_state.laps_data.append(lap_record)
        st.session_state.current_flag = lap_record["flag"]

        # Real-time Telemetry Updates
        df_telemetry = pd.DataFrame(st.session_state.laps_data)
        render_plotly_telemetry(df_telemetry)

        # Update Live Flags & Lap Counters in real time
        curr_f = lap_record["flag"]
        if curr_f == "SC":
            badge = "<span class='flag-yellow'>🟨 FULL SAFETY CAR</span>"
        elif curr_f == "VSC":
            badge = "<span class='flag-yellow'>🟡 VSC ACTIVE</span>"
        elif curr_f == "RED_FLAG":
            badge = "<span class='flag-red'>🔴 RED FLAG SUSPENSION</span>"
        else:
            badge = "<span class='flag-green'>🟢 GREEN FLAG</span>"

        ph_flag.markdown(f"<div class='status-card'><div class='kpi-title'>Live Track Neutralization</div>"
                         f"<div style='margin-top:6px;'>{badge}</div></div>", unsafe_allow_html=True)

        ph_lap.markdown(f"<div class='status-card'><div class='kpi-title'>Active Race Progress</div>"
                        f"<div class='kpi-val'>LAP {lap_record['lap']} / {circuit_data['race_laps']}</div>"
                        f"<span style='color: #64748b;'>Driver: {driver_profile['badge']}</span></div>", unsafe_allow_html=True)

        if step_sim:
            break

        if auto_pause and lap_record["incident_triggered"] and lap_record["flag"] in ("SC", "RED_FLAG"):
            st.warning(f"🚨 {lap_record['flag']} DEPLOYED ON LAP {lap_record['lap']}! Live stream paused. Call your strategic override below or resume.")
            st.session_state.simulation_running = False
            break

        if not finish_sim:
            time.sleep(sim_delay)

    if len(st.session_state.laps_data) >= circuit_data["race_laps"]:
        st.session_state.simulation_running = False
        st.success(f"🏁 CHECKERED FLAG! {circuit_data['event_name'].upper()} COMPLETED.")
        st.balloons()

elif st.session_state.laps_data:
    df_telemetry = pd.DataFrame(st.session_state.laps_data)
    render_plotly_telemetry(df_telemetry)


# -----------------------------------------------------------------------------
# 16. REAL-TIME 1,000-RUN MONTE CARLO STANDINGS
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 📊 1,000-Run Monte Carlo Optimized Strategy Standings")

if st.session_state.mc_standings:
    df_mc = pd.DataFrame(st.session_state.mc_standings)
    best_time = df_mc["mean_time"].min()
    df_mc["Delta to P1"] = df_mc["mean_time"].apply(lambda t: "P1 LEADER" if t == best_time else f"+{t - best_time:.3f}s")
    df_mc["Mean Time"] = df_mc["mean_time"].apply(format_lap_time)
    df_mc["Win Rate %"] = df_mc["win_rate"].apply(lambda w: f"{w:.1f}%")

    st.dataframe(
        df_mc[["strategy", "Mean Time", "Delta to P1", "Win Rate %"]].rename(columns={"strategy": "Strategy"}),
        use_container_width=True
    )
else:
    st.info("💡 Click **'BOX THIS LAP'**, **'STAY OUT'**, or wait for a Safety Car to render live 1,000-run predictive Monte Carlo standings.")


# -----------------------------------------------------------------------------
# 17. INTERACTIVE STRATEGIC ENGINEERING NOTEBOOK (FULL CRUD: ADD / EDIT / DELETE)
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 📝 Interactive Pit-Wall Strategic Engineering Notebook")
st.caption("Add live strategic advisories, edit existing notes, or delete resolved communications in real time.")

# 1. Add New Strategic Note Form
with st.expander("➕ Add New Strategic Note / Pit-Wall Communication", expanded=False):
    with st.form("new_note_form", clear_on_submit=True):
        col_n1, col_n2, col_n3, col_n4 = st.columns([1, 1.2, 1, 1])
        with col_n1:
            curr_l_str = f"LAP {len(st.session_state.laps_data)}" if st.session_state.laps_data else "PRE-RACE"
            note_lap = st.text_input("Lap Tag", value=curr_l_str)
        with col_n2:
            note_author = st.selectbox("Author Channel", ["Chief Race Strategist", "Race Engineer", "Driver Radio", "Tyre Performance Tech", "FIA Race Control"])
        with col_n3:
            note_category = st.selectbox("Strategic Category", ["Pit Window", "Undercut/Overcut", "Tyre Degradation", "Traffic & Grid", "Thermal Physics", "Weather Alert", "Damage/Debris"])
        with col_n4:
            note_priority = st.selectbox("Priority Level", ["CRITICAL", "WARNING", "INFO"])

        note_text = st.text_area("Strategic Note / Telemetry Directive", placeholder="Enter specific engineering directives, driver delta targets, or weather observations...")
        submitted = st.form_submit_button("💾 Save Strategic Note to Pit-Wall Log", type="primary")

        if submitted and note_text.strip():
            new_id = int(time.time() * 1000)
            now_str = datetime.now().strftime("%H:%M:%S")
            st.session_state.strategic_notes.insert(0, {
                "id": new_id,
                "lap": note_lap.strip(),
                "author": note_author,
                "category": note_category,
                "priority": note_priority,
                "text": note_text.strip(),
                "time": now_str
            })
            st.toast("✅ Strategic Note added to pit-wall log!")
            st.rerun()

# 2. Render Existing Notes with Inline Edit & Delete
if not st.session_state.strategic_notes:
    st.info("No active strategic notes logged. Click above to add your first pit-wall directive.")
else:
    for idx, note in enumerate(st.session_state.strategic_notes):
        prio = note.get("priority", "INFO")
        card_class = "note-card-critical" if prio == "CRITICAL" else ("note-card-warning" if prio == "WARNING" else "note-card-info")
        prio_color = "#ef4444" if prio == "CRITICAL" else ("#f59e0b" if prio == "WARNING" else "#00f2fe")

        col_card, col_action1, col_action2 = st.columns([8, 1, 1])

        with col_card:
            st.markdown(f"""
            <div class='{card_class}'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                    <span style='color:{prio_color}; font-weight:800; font-size:0.85rem; letter-spacing:1px;'>
                        [{note.get('priority', 'INFO')}] 🏷️ {note.get('lap', 'PRE-RACE')} │ 👤 {note.get('author', 'Race Engineer')} │ 📂 {note.get('category', 'Strategy')}
                    </span>
                    <span style='color:#64748b; font-size:0.8rem;'>{note.get('time', '')}</span>
                </div>
                <div style='color:#e2e8f0; font-size:1.02rem; font-weight:500; line-height:1.4;'>{note.get('text', '')}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_action1:
            if st.button("✏️ Edit", key=f"edit_btn_{note['id']}", use_container_width=True):
                st.session_state.edit_note_id = note["id"]

        with col_action2:
            if st.button("🗑️ Delete", key=f"del_btn_{note['id']}", use_container_width=True):
                st.session_state.strategic_notes = [n for n in st.session_state.strategic_notes if n["id"] != note["id"]]
                if st.session_state.edit_note_id == note["id"]:
                    st.session_state.edit_note_id = None
                st.toast("🗑️ Strategic Note deleted.")
                st.rerun()

        # Inline Edit Form if this note is selected for editing
        if st.session_state.edit_note_id == note["id"]:
            with st.form(f"edit_form_{note['id']}"):
                st.markdown(f"**Editing Note #{note['id']}**")
                edit_c1, edit_c2, edit_c3 = st.columns(3)
                with edit_c1:
                    e_author = st.selectbox("Author", ["Chief Race Strategist", "Race Engineer", "Driver Radio", "Tyre Performance Tech", "FIA Race Control"],
                                            index=["Chief Race Strategist", "Race Engineer", "Driver Radio", "Tyre Performance Tech", "FIA Race Control"].index(note.get("author", "Chief Race Strategist")))
                with edit_c2:
                    e_prio = st.selectbox("Priority", ["CRITICAL", "WARNING", "INFO"],
                                          index=["CRITICAL", "WARNING", "INFO"].index(note.get("priority", "INFO")))
                with edit_c3:
                    e_lap = st.text_input("Lap", value=note.get("lap", "PRE-RACE"))

                e_text = st.text_area("Updated Content", value=note.get("text", ""))
                btn_save, btn_cancel = st.columns(2)
                with btn_save:
                    save_edit = st.form_submit_button("💾 Save Updates", type="primary")
                with btn_cancel:
                    cancel_edit = st.form_submit_button("Cancel")

                if save_edit and e_text.strip():
                    note["author"] = e_author
                    note["priority"] = e_prio
                    note["lap"] = e_lap.strip()
                    note["text"] = e_text.strip()
                    st.session_state.edit_note_id = None
                    st.toast("✅ Strategic Note updated successfully!")
                    st.rerun()
                elif cancel_edit:
                    st.session_state.edit_note_id = None
                    st.rerun()
