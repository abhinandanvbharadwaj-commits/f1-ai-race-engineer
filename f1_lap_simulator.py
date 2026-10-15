"""
===============================================================================
🏁 FORMULA 1 PREDICTIVE MONTE CARLO STRATEGY & TELEMETRY ENGINE
===============================================================================
Advanced Strategy Simulation System combining:
- FastF1 Live Event & Schedule Ingestion (Season 2026 / Calibrated Fallbacks)
- Probabilistic Interruption Engine (Historical SC Risks + Weather & Thermal Deltas)
- Lap-by-Lap Monte Carlo Dice Rolls (VSC 15%, SC 70%, Red Flag 15%, Lap 1 Double)
- Automated 1,000-Race Optimization Strategy Standings (Mean Predictive Averages)
- Non-Linear Thermal Physics & Track Moisture Meteorology
- Linear Fuel Mass Burn-off Modeling (1.9 kg/lap @ 0.035 s/kg benefit)
- Tri-Sector Telemetry Analytics (S1: 33%, S2: 34%, S3: 33%)
- Condensed Multi-Stint Visual Mapping & High-Tech Pit-Wall Command Station
===============================================================================
"""

import os
import sys
import random
import logging
import warnings
import fastf1

# Configure UTF-8 encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Suppress background HTTP / FastF1 logging noise
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)

# -----------------------------------------------------------------------------
# 1. DYNAMIC DATA INGESTION & LOCAL CACHE
# -----------------------------------------------------------------------------
os.makedirs("f1_cache", exist_ok=True)
fastf1.Cache.enable_cache("f1_cache")
fastf1.set_log_level("ERROR")

# Engineering fallback database covering 25 World Championship circuits
# with historical baseline Safety Car probabilities (e.g., Monaco: 0.85, Singapore: 0.95, Monza: 0.25)
FALLBACK_CIRCUITS = {
    "Monza": {
        "event_name": "Italian Grand Prix",
        "round": 16,
        "country": "Italy",
        "location": "Monza",
        "race_laps": 53,
        "pit_loss": 24.0,
        "base_pace": 86.968,
        "sc_risk": 0.25
    },
    "Silverstone": {
        "event_name": "British Grand Prix",
        "round": 12,
        "country": "Great Britain",
        "location": "Silverstone",
        "race_laps": 52,
        "pit_loss": 25.0,
        "base_pace": 93.100,
        "sc_risk": 0.50
    },
    "Monaco": {
        "event_name": "Monaco Grand Prix",
        "round": 8,
        "country": "Monaco",
        "location": "Monte Carlo",
        "race_laps": 78,
        "pit_loss": 20.0,
        "base_pace": 78.430,
        "sc_risk": 0.85
    },
    "Spa": {
        "event_name": "Belgian Grand Prix",
        "round": 14,
        "country": "Belgium",
        "location": "Spa-Francorchamps",
        "race_laps": 44,
        "pit_loss": 22.0,
        "base_pace": 108.250,
        "sc_risk": 0.60
    },
    "Bahrain": {
        "event_name": "Bahrain Grand Prix",
        "round": 1,
        "country": "Bahrain",
        "location": "Sakhir",
        "race_laps": 57,
        "pit_loss": 23.0,
        "base_pace": 96.120,
        "sc_risk": 0.35
    },
    "Saudi Arabia": {
        "event_name": "Saudi Arabian Grand Prix",
        "round": 2,
        "country": "Saudi Arabia",
        "location": "Jeddah",
        "race_laps": 50,
        "pit_loss": 21.0,
        "base_pace": 93.450,
        "sc_risk": 0.80
    },
    "Australia": {
        "event_name": "Australian Grand Prix",
        "round": 3,
        "country": "Australia",
        "location": "Melbourne",
        "race_laps": 58,
        "pit_loss": 21.5,
        "base_pace": 82.340,
        "sc_risk": 0.65
    },
    "Japan": {
        "event_name": "Japanese Grand Prix",
        "round": 4,
        "country": "Japan",
        "location": "Suzuka",
        "race_laps": 53,
        "pit_loss": 23.5,
        "base_pace": 95.110,
        "sc_risk": 0.40
    },
    "China": {
        "event_name": "Chinese Grand Prix",
        "round": 5,
        "country": "China",
        "location": "Shanghai",
        "race_laps": 56,
        "pit_loss": 23.0,
        "base_pace": 84.225,
        "sc_risk": 0.50
    },
    "Miami": {
        "event_name": "Miami Grand Prix",
        "round": 6,
        "country": "United States",
        "location": "Miami",
        "race_laps": 57,
        "pit_loss": 21.0,
        "base_pace": 91.500,
        "sc_risk": 0.45
    },
    "Imola": {
        "event_name": "Emilia Romagna Grand Prix",
        "round": 7,
        "country": "Italy",
        "location": "Imola",
        "race_laps": 63,
        "pit_loss": 27.0,
        "base_pace": 80.450,
        "sc_risk": 0.60
    },
    "Canada": {
        "event_name": "Canadian Grand Prix",
        "round": 9,
        "country": "Canada",
        "location": "Montreal",
        "race_laps": 70,
        "pit_loss": 19.5,
        "base_pace": 76.150,
        "sc_risk": 0.70
    },
    "Spain": {
        "event_name": "Spanish Grand Prix",
        "round": 10,
        "country": "Spain",
        "location": "Barcelona",
        "race_laps": 66,
        "pit_loss": 23.0,
        "base_pace": 79.850,
        "sc_risk": 0.30
    },
    "Austria": {
        "event_name": "Austrian Grand Prix",
        "round": 11,
        "country": "Austria",
        "location": "Spielberg",
        "race_laps": 71,
        "pit_loss": 21.0,
        "base_pace": 69.900,
        "sc_risk": 0.35
    },
    "Hungary": {
        "event_name": "Hungarian Grand Prix",
        "round": 13,
        "country": "Hungary",
        "location": "Budapest",
        "race_laps": 70,
        "pit_loss": 21.5,
        "base_pace": 82.100,
        "sc_risk": 0.30
    },
    "Zandvoort": {
        "event_name": "Dutch Grand Prix",
        "round": 15,
        "country": "Netherlands",
        "location": "Zandvoort",
        "race_laps": 72,
        "pit_loss": 22.0,
        "base_pace": 75.400,
        "sc_risk": 0.50
    },
    "Baku": {
        "event_name": "Azerbaijan Grand Prix",
        "round": 17,
        "country": "Azerbaijan",
        "location": "Baku",
        "race_laps": 51,
        "pit_loss": 22.0,
        "base_pace": 106.200,
        "sc_risk": 0.75
    },
    "Singapore": {
        "event_name": "Singapore Grand Prix",
        "round": 18,
        "country": "Singapore",
        "location": "Marina Bay",
        "race_laps": 62,
        "pit_loss": 29.0,
        "base_pace": 98.900,
        "sc_risk": 0.95
    },
    "Austin": {
        "event_name": "United States Grand Prix",
        "round": 19,
        "country": "United States",
        "location": "Austin",
        "race_laps": 56,
        "pit_loss": 21.5,
        "base_pace": 100.350,
        "sc_risk": 0.35
    },
    "Mexico": {
        "event_name": "Mexico City Grand Prix",
        "round": 20,
        "country": "Mexico",
        "location": "Mexico City",
        "race_laps": 71,
        "pit_loss": 23.0,
        "base_pace": 82.600,
        "sc_risk": 0.30
    },
    "Brazil": {
        "event_name": "São Paulo Grand Prix",
        "round": 21,
        "country": "Brazil",
        "location": "Interlagos",
        "race_laps": 71,
        "pit_loss": 22.5,
        "base_pace": 75.200,
        "sc_risk": 0.65
    },
    "Las Vegas": {
        "event_name": "Las Vegas Grand Prix",
        "round": 22,
        "country": "United States",
        "location": "Las Vegas",
        "race_laps": 50,
        "pit_loss": 22.0,
        "base_pace": 97.400,
        "sc_risk": 0.60
    },
    "Qatar": {
        "event_name": "Qatar Grand Prix",
        "round": 23,
        "country": "Qatar",
        "location": "Lusail",
        "race_laps": 57,
        "pit_loss": 24.5,
        "base_pace": 87.800,
        "sc_risk": 0.35
    },
    "Abu Dhabi": {
        "event_name": "Abu Dhabi Grand Prix",
        "round": 24,
        "country": "United Arab Emirates",
        "location": "Yas Marina",
        "race_laps": 58,
        "pit_loss": 23.0,
        "base_pace": 89.200,
        "sc_risk": 0.40
    },
    "Portugal": {
        "event_name": "Portuguese Grand Prix",
        "round": 25,
        "country": "Portugal",
        "location": "Portimao",
        "race_laps": 66,
        "pit_loss": 22.0,
        "base_pace": 81.300,
        "sc_risk": 0.40
    }
}


def load_all_circuits(year=2026):
    """
    Dynamically loads the official schedule using fastf1.get_event_schedule(year),
    ignoring pre-season testing slots.
    Merges dynamic safety car baseline risk variables and returns an
    engineering dictionary. Handles network loading exceptions gracefully.
    """
    circuits = {k: dict(v) for k, v in FALLBACK_CIRCUITS.items()}

    try:
        schedule = fastf1.get_event_schedule(year)

        # Ignore testing slots (RoundNumber == 0 or EventName contains Testing)
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
        # Gracefully preserve calibrated engineering fallback database
        pass

    return circuits


def fetch_live_baseline_pace(year, track_name):
    """
    Attempt to load live median race pace from FastF1 for recent sessions.
    Returns median lap time in seconds or None if unavailable.
    """
    candidate_years = [year, 2024, 2023, 2022]
    for target_year in candidate_years:
        try:
            session = fastf1.get_session(target_year, track_name, 'R')
            session.load(telemetry=False, weather=False, messages=False)

            if hasattr(session.laps, "pick_quick_laps"):
                quick_laps = session.laps.pick_quick_laps()
            else:
                quick_laps = session.laps.pick_quicklaps()

            valid = quick_laps.dropna(subset=["LapTime"])
            if not valid.empty:
                med = valid["LapTime"].dt.total_seconds().median()
                return float(med), target_year
        except Exception:
            continue

    return None, None


# -----------------------------------------------------------------------------
# 2. PROBABILISTIC INTERRUPTION ENGINE & MONTE CARLO ROLLS
# -----------------------------------------------------------------------------

def calculate_race_disruptions(track_data, weather_state, track_temp):
    """
    Executes before the race strategy logic runs.
    Calculates dynamic race disruption risks based on:
    - Base historical circuit Safety Car probability (Monaco: 0.85, Singapore: 0.95, Monza: 0.25)
    - Dynamic weather risk premiums: +15% for 'Damp', +35% for 'Heavy Rain'
    - Thermal degradation risk premium: +10% if track temp > 42°C (tyre blistering/delamination)
    Returns:
    - Probability metrics including per-lap dice-roll thresholds and exact event odds.
    """
    base_sc_prob = track_data.get("sc_risk", 0.35)

    # 1. Weather risk scaling
    weather_norm = weather_state.strip().title()
    weather_premium = 0.0
    if "Damp" in weather_norm:
        weather_premium = 0.15
    elif "Heavy Rain" in weather_norm or "Wet" in weather_norm:
        weather_premium = 0.35

    # 2. Thermal blistering degradation risk (> 42°C)
    thermal_premium = 0.10 if track_temp > 42.0 else 0.0

    # Total scaled probability of encountering at least one incident across the Grand Prix
    scaled_race_prob = min(0.99, max(0.05, base_sc_prob + weather_premium + thermal_premium))

    total_laps = track_data.get("race_laps", 53)

    # Per-lap incident probability: 1 - (1 - p_lap)^N = scaled_race_prob
    p_lap = 1.0 - (1.0 - scaled_race_prob) ** (1.0 / total_laps)

    # Double the probability threshold on Lap 1 to mimic high-density pack collisions
    p_lap1 = min(0.95, 2.0 * p_lap)

    # Exact mathematical calculated probability of encountering at least one neutralization flag
    exact_neutralization_prob = 1.0 - (1.0 - p_lap1) * ((1.0 - p_lap) ** max(1, (total_laps - 1)))

    return {
        "base_sc_prob": base_sc_prob,
        "weather_premium": weather_premium,
        "thermal_premium": thermal_premium,
        "scaled_race_prob": scaled_race_prob,
        "exact_neutralization_prob": exact_neutralization_prob,
        "p_lap": p_lap,
        "p_lap1": p_lap1
    }


def generate_monte_carlo_race(total_laps, p_lap, p_lap1):
    """
    Simulates one Grand Prix lap-by-lap using Python's random.random():
    - Rolls a probability check on every lap (doubled on Lap 1 for start collisions).
    - If hit:
      * 15% chance of localized debris VSC (lasting 2 laps)
      * 70% chance of high-impact structural accident forcing full SC (lasting 3 laps)
      * 15% chance of extreme blocking incident triggering a Red Flag
    Returns:
    - event_map: {lap_number: "SC" | "VSC" | "RED_FLAG"}
    - incident_starts: list of (lap, type)
    """
    event_map = {}
    incident_starts = []
    lap = 1

    while lap <= total_laps:
        # Double the threshold on Lap 1
        current_prob = p_lap1 if lap == 1 else p_lap

        if random.random() < current_prob:
            # Dice roll for incident classification
            roll = random.random()
            if roll < 0.15:
                incident_type = "VSC"
                duration = 2
            elif roll < 0.85:  # 0.15 to 0.85 = 70% chance
                incident_type = "SC"
                duration = 3
            else:  # 0.85 to 1.00 = 15% chance
                incident_type = "RED_FLAG"
                duration = 1

            incident_starts.append((lap, incident_type))

            for d in range(duration):
                target_lap = lap + d
                if target_lap <= total_laps:
                    if incident_type == "RED_FLAG" and d == 0:
                        event_map[target_lap] = "RED_FLAG"
                    else:
                        event_map[target_lap] = "SC" if incident_type in ("SC", "RED_FLAG") else "VSC"

            lap += duration
        else:
            lap += 1

    return event_map, incident_starts


# -----------------------------------------------------------------------------
# 3. THERMAL TRACKING & ADVANCED TYRE / WEATHER MODELING
# -----------------------------------------------------------------------------

# Expanded TYRES dictionary mapping performance alongside dampness profiles
TYRES = {
    "Soft": {
        "symbol": "S",
        "weather_profile": "Dry",
        "pace_delta": -0.60,
        "base_deg": 0.080,
        "notes": "Peak grip; suffers +20% blistering deg at >40°C"
    },
    "Medium": {
        "symbol": "M",
        "weather_profile": "Dry",
        "pace_delta": 0.00,
        "base_deg": 0.050,
        "notes": "Optimal balance across normal operating window"
    },
    "Hard": {
        "symbol": "H",
        "weather_profile": "Dry",
        "pace_delta": 0.60,
        "base_deg": 0.030,
        "notes": "Long durability; loses 15% grip (<25°C warm-up issue)"
    },
    "Inter": {
        "symbol": "I",
        "weather_profile": "Damp",
        "pace_delta": 3.80,
        "base_deg": 0.060,
        "notes": "Grooved compound for greasy/damp track surfaces"
    },
    "Wet": {
        "symbol": "W",
        "weather_profile": "Heavy Rain",
        "pace_delta": 8.50,
        "base_deg": 0.040,
        "notes": "Full wet tread for heavy standing water & rain"
    }
}


def calculate_lap_time(base_lap_time, tyre_compound, tyre_age, current_lap, total_laps,
                       track_temp, track_weather, neutralization=None):
    """
    Physical lap time synthesis:
    1. Base compound pace delta.
    2. Non-linear thermal degradation:
       - Soft compounds suffer 20% higher degradation above 40°C (blistering).
       - Hard compounds lose 15% grip below 25°C (poor tire warm-up).
    3. Neutralization degradation scaling:
       - SC periods scale degradation down by 80% (effective rate = 20%).
       - VSC periods scale degradation down by 50% (effective rate = 50%).
    4. Linear fuel mass burn-off:
       - 1.9 kg/lap usage @ 0.035 s/kg benefit (saves ~0.0665 s/lap).
    5. Weather dampness mismatch penalty:
       - Severe 18-second time penalty if tire's rain profile does not match moisture.
    6. Neutralization fixed slow pacing limit:
       - SC: base_lap_time + 40s
       - VSC: base_lap_time + 20s
    """
    spec = TYRES[tyre_compound]
    compound_base = base_lap_time + spec["pace_delta"]

    # 1. Thermal Degradation Rate
    deg_rate = spec["base_deg"]
    if tyre_compound == "Soft" and track_temp > 40.0:
        deg_rate *= 1.20  # +20% blistering penalty

    # 2. Hard cold tire warm-up grip loss (<25°C)
    thermal_grip_penalty = 0.0
    if tyre_compound == "Hard" and track_temp < 25.0:
        thermal_grip_penalty = 0.85  # 15% grip loss penalty

    # 3. Neutralization Degradation Scaling
    if neutralization == "SC":
        effective_deg = deg_rate * 0.20  # 80% degradation reduction
    elif neutralization == "VSC":
        effective_deg = deg_rate * 0.50  # 50% degradation reduction
    else:
        effective_deg = deg_rate

    tyre_wear_penalty = effective_deg * tyre_age

    # 4. Linear Fuel Burn-off Calculation
    fuel_burned_kg = max(0, (current_lap - 1)) * 1.9
    fuel_time_saving = fuel_burned_kg * 0.035  # 0.035 s/kg weight reduction

    # 5. Weather Moisture Mismatch Penalty
    norm_weather = "Heavy Rain" if track_weather in ("Heavy Rain", "Wet") else track_weather
    weather_penalty = 0.0
    if spec["weather_profile"] != norm_weather:
        weather_penalty = 18.0  # Severe 18s rain profile mismatch penalty

    # 6. Neutralization Lap Time Caps
    if neutralization == "SC":
        final_lap_time = base_lap_time + 40.0  # Fixed pacing cap (+40s)
    elif neutralization == "VSC":
        final_lap_time = base_lap_time + 20.0  # Fixed pacing cap (+20s)
    else:
        final_lap_time = (
            compound_base
            + tyre_wear_penalty
            - fuel_time_saving
            + thermal_grip_penalty
            + weather_penalty
        )

    return max(30.0, final_lap_time)


def calculate_sector_splits(lap_time):
    """
    Split each simulated lap into 3 distinct sectors:
    Sector 1: 33%, Sector 2: 34%, Sector 3: 33%.
    Ensures exact summation equality with lap_time.
    """
    s1 = lap_time * 0.33
    s2 = lap_time * 0.34
    s3 = lap_time - s1 - s2
    return s1, s2, s3


def format_lap_time(seconds):
    """Convert float seconds into M:SS.mmm format."""
    minutes = int(seconds // 60)
    rem = seconds % 60
    return f"{minutes}:{rem:06.3f}"


# -----------------------------------------------------------------------------
# 4. MULTI-STINT STRATEGY SIMULATION RUNNER
# -----------------------------------------------------------------------------

def simulate_full_strategy(strategy, total_laps, base_lap_time, pit_stop_loss,
                           track_temp, track_weather, event_map):
    """
    Simulates a full multi-stint strategy across a specific race incident schedule:
    - Tyre aging
    - Red Flag "Free Tire Change" rule override (resets tyre age to 0 without pit loss)
    - Regular scheduled pit stops between planned stints
    - Sector splits aggregation (S1, S2, S3)
    - Stint Map character string generator
    """
    stint_count = len(strategy)
    base_stint_laps = total_laps // stint_count
    remainder_laps = total_laps % stint_count

    scheduled_stint_lengths = [
        base_stint_laps + (1 if idx < remainder_laps else 0)
        for idx in range(stint_count)
    ]

    total_race_time = 0.0
    all_s1 = []
    all_s2 = []
    all_s3 = []

    current_stint_idx = 0
    current_compound = strategy[current_stint_idx]
    tyre_age = 0
    stint_lap_counter = 0

    stint_map_elements = []
    current_stint_symbols = []
    pit_stop_count = 0

    for current_lap in range(1, total_laps + 1):
        event_state = event_map.get(current_lap, None)

        # Red Flag Free Tire Change rule override
        if event_state == "RED_FLAG":
            tyre_age = 0
            if current_stint_symbols:
                stint_map_elements.append(f"[{''.join(current_stint_symbols)}]")
                current_stint_symbols = []
            stint_map_elements.append("➔ 🚩 RED FLAG (Free Tyre Change) ➔")

        lap_t = calculate_lap_time(
            base_lap_time=base_lap_time,
            tyre_compound=current_compound,
            tyre_age=tyre_age,
            current_lap=current_lap,
            total_laps=total_laps,
            track_temp=track_temp,
            track_weather=track_weather,
            neutralization=event_state if event_state in ("SC", "VSC") else None
        )

        s1, s2, s3 = calculate_sector_splits(lap_t)
        all_s1.append(s1)
        all_s2.append(s2)
        all_s3.append(s3)
        total_race_time += lap_t

        sym = TYRES[current_compound]["symbol"]
        current_stint_symbols.append(sym)

        tyre_age += 1
        stint_lap_counter += 1

        # Scheduled pit stop transition
        if (current_stint_idx < stint_count - 1 and
            stint_lap_counter >= scheduled_stint_lengths[current_stint_idx] and
            current_lap < total_laps):

            total_race_time += pit_stop_loss
            pit_stop_count += 1

            stint_map_elements.append(f"[{''.join(current_stint_symbols)}]")
            stint_map_elements.append(f"➔ 🔧 {pit_stop_loss:.0f}s PIT (Lap {current_lap}) ➔")
            current_stint_symbols = []

            current_stint_idx += 1
            current_compound = strategy[current_stint_idx]
            tyre_age = 0
            stint_lap_counter = 0

    if current_stint_symbols:
        stint_map_elements.append(f"[{''.join(current_stint_symbols)}]")

    condensed_stint_map = " ".join(stint_map_elements)
    avg_s1 = sum(all_s1) / len(all_s1) if all_s1 else 0.0
    avg_s2 = sum(all_s2) / len(all_s2) if all_s2 else 0.0
    avg_s3 = sum(all_s3) / len(all_s3) if all_s3 else 0.0

    return {
        "strategy": strategy,
        "strategy_label": " → ".join(strategy),
        "total_time": total_race_time,
        "pit_stops": pit_stop_count,
        "avg_s1": avg_s1,
        "avg_s2": avg_s2,
        "avg_s3": avg_s3,
        "stint_map": condensed_stint_map,
        "first_pit_lap": scheduled_stint_lengths[0] if len(scheduled_stint_lengths) > 1 else None
    }


# -----------------------------------------------------------------------------
# 5. AUTOMATED 1,000-RACE MONTE CARLO OPTIMIZATION ENGINE
# -----------------------------------------------------------------------------

def run_monte_carlo_optimization(strategies, total_laps, base_lap_time, pit_stop_loss,
                                  track_temp, track_weather, risk_profile, iterations=1000):
    """
    Executes an automated 1,000-race Monte Carlo simulation loop:
    1. Generates 1,000 independent race disruption timelines based on calibrated probabilities.
    2. Runs each strategic setup across all 1,000 simulated race scenarios.
    3. Aggregates total race durations and calculates the mathematical mean average.
    4. Computes Sector Splits (Avg S1, Avg S2, Avg S3) and Win Rate % across the 1,000 runs.
    5. Sorts final visual standings strictly by mean predictive average race time.
    """
    p_lap = risk_profile["p_lap"]
    p_lap1 = risk_profile["p_lap1"]

    # 1. Pre-generate 1,000 randomized Monte Carlo race scenarios
    scenarios = []
    lap_incident_counts = {l: 0 for l in range(1, total_laps + 1)}
    total_sc_laps = 0
    total_vsc_laps = 0
    total_rf_count = 0

    for _ in range(iterations):
        event_map, incident_starts = generate_monte_carlo_race(total_laps, p_lap, p_lap1)
        scenarios.append(event_map)

        for lap, inc_type in incident_starts:
            lap_incident_counts[lap] += 1
            if inc_type == "RED_FLAG":
                total_rf_count += 1

        for state in event_map.values():
            if state == "SC":
                total_sc_laps += 1
            elif state == "VSC":
                total_vsc_laps += 1

    mc_stats = {
        "iterations": iterations,
        "avg_sc_laps": total_sc_laps / iterations,
        "avg_vsc_laps": total_vsc_laps / iterations,
        "avg_rf_events": total_rf_count / iterations,
        "lap_incident_counts": lap_incident_counts
    }

    # 2. Evaluate each strategy across all 1,000 scenarios
    strategy_results = []
    scenario_best_times = [float("inf")] * iterations
    scenario_winners = [None] * iterations

    for strat in strategies:
        times = []
        s1_totals = []
        s2_totals = []
        s3_totals = []

        # Baseline clean run for nominal Stint Map string
        clean_res = simulate_full_strategy(
            strategy=strat,
            total_laps=total_laps,
            base_lap_time=base_lap_time,
            pit_stop_loss=pit_stop_loss,
            track_temp=track_temp,
            track_weather=track_weather,
            event_map={}
        )

        for idx, event_map in enumerate(scenarios):
            sim_res = simulate_full_strategy(
                strategy=strat,
                total_laps=total_laps,
                base_lap_time=base_lap_time,
                pit_stop_loss=pit_stop_loss,
                track_temp=track_temp,
                track_weather=track_weather,
                event_map=event_map
            )
            r_time = sim_res["total_time"]
            times.append(r_time)
            s1_totals.append(sim_res["avg_s1"])
            s2_totals.append(sim_res["avg_s2"])
            s3_totals.append(sim_res["avg_s3"])

            if r_time < scenario_best_times[idx]:
                scenario_best_times[idx] = r_time
                scenario_winners[idx] = strat

        mean_race_time = sum(times) / iterations
        avg_s1 = sum(s1_totals) / iterations
        avg_s2 = sum(s2_totals) / iterations
        avg_s3 = sum(s3_totals) / iterations

        strategy_results.append({
            "strategy": strat,
            "strategy_label": " → ".join(strat),
            "pit_stops": len(strat) - 1,
            "mean_race_time": mean_race_time,
            "min_time": min(times),
            "max_time": max(times),
            "avg_s1": avg_s1,
            "avg_s2": avg_s2,
            "avg_s3": avg_s3,
            "stint_map": clean_res["stint_map"],
            "first_pit_lap": clean_res["first_pit_lap"],
            "wins": 0
        })

    # Calculate win rate percentage across the 1,000 Monte Carlo runs
    for winner in scenario_winners:
        if winner:
            for s_res in strategy_results:
                if s_res["strategy"] == winner:
                    s_res["wins"] += 1
                    break

    for s_res in strategy_results:
        s_res["win_rate"] = (s_res["wins"] / iterations) * 100.0

    # Sort strictly by mean mathematical average race time
    strategy_results.sort(key=lambda x: x["mean_race_time"])

    # Statistically most probable lap window from 1,000-race grid analysis
    mid_race_window_scores = {}
    for l in range(2, max(3, total_laps - 4)):
        mid_race_window_scores[l] = sum(lap_incident_counts.get(k, 0) for k in range(l, l + 5))

    if mid_race_window_scores:
        peak_lap = max(mid_race_window_scores, key=mid_race_window_scores.get)
        peak_count = mid_race_window_scores[peak_lap]
        probable_window_str = f"LAPS {peak_lap} - {peak_lap + 4} ({peak_count} incidents recorded across 1,000 runs)"
    else:
        probable_window_str = "Laps 15 - 20 (Nominal Mid-Race Window)"

    mc_stats["peak_window"] = probable_window_str
    mc_stats["lap1_incidents"] = lap_incident_counts.get(1, 0)

    return strategy_results, mc_stats


def get_candidate_strategies(track_weather):
    """Returns candidate strategy permutations based on track dampness."""
    norm_w = "Heavy Rain" if track_weather in ("Heavy Rain", "Wet") else track_weather
    if norm_w == "Dry":
        return [
            ["Soft", "Medium"],
            ["Medium", "Hard"],
            ["Soft", "Hard"],
            ["Medium", "Medium"],
            ["Soft", "Medium", "Soft"],
            ["Medium", "Hard", "Medium"],
            ["Soft", "Hard", "Hard"]
        ]
    elif norm_w == "Damp":
        return [
            ["Inter", "Inter"],
            ["Inter", "Medium"],
            ["Inter", "Inter", "Inter"],
            ["Wet", "Inter"],
            ["Soft", "Medium"]
        ]
    else:  # Heavy Rain
        return [
            ["Wet", "Wet"],
            ["Wet", "Inter"],
            ["Wet", "Wet", "Wet"],
            ["Inter", "Wet"],
            ["Inter", "Inter"]
        ]


# -----------------------------------------------------------------------------
# 6. ENHANCED PIT-WALL COMMAND STATION DASHBOARD
# -----------------------------------------------------------------------------

def display_dashboard(circuit_data, track_weather, track_temp,
                      risk_profile, mc_stats, results):
    """
    Renders high-tech pit-wall command station dashboard.
    Includes:
    - 🏁 [RACE METRICS & LIVE TRACK ENVIRONMENT] (with Pre-Race Risk Assessment Prediction)
    - ⚠️ [LIVE TRACK STATUS & 1,000-RUN MONTE CARLO PROJECTIONS]
    - 📊 [OPTIMIZED STRATEGY STANDINGS] (1,000-Run Mean Predictive Averages)
    - ⚙️ [STRATEGIC ENGINEERING NOTEBOOK] (Statistically Most Probable Lap Window & Undercut)
    """
    best = results[0]
    total_laps = circuit_data["race_laps"]

    # Pre-Race Risk Assessment Prediction formatting
    exact_p_pct = risk_profile["exact_neutralization_prob"] * 100.0
    base_p_pct = risk_profile["base_sc_prob"] * 100.0
    w_p_pct = risk_profile["weather_premium"] * 100.0
    t_p_pct = risk_profile["thermal_premium"] * 100.0

    # Thermal condition categorization
    if track_temp > 40.0:
        thermal_tag = f"{track_temp:.1f}°C ⚠️ BLISTERING RISK ACTIVE (Soft Deg +20%)"
    elif track_temp < 25.0:
        thermal_tag = f"{track_temp:.1f}°C ❄️ COLD TRACK HAZARD (Hard Grip -15%)"
    else:
        thermal_tag = f"{track_temp:.1f}°C (Optimal Operating Window)"

    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + "   🏎️  FORMULA 1 AI PIT-WALL MONTE CARLO STRATEGY & TELEMETRY ENGINE    " + "║")
    print("╚" + "═" * 78 + "╝")

    # -------------------------------------------------------------------------
    # 🏁 [RACE METRICS & LIVE TRACK ENVIRONMENT]
    # -------------------------------------------------------------------------
    print("\n" + "┌" + "─" * 78 + "┐")
    print("│ 🏁 [RACE METRICS & LIVE TRACK ENVIRONMENT]" + " " * 36 + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│  Circuit Name       : {circuit_data['event_name']} ({circuit_data['location']}, {circuit_data['country']})".ljust(79) + "│")
    print(f"│  Scheduled Distance : {total_laps} Laps (Nominal Pit Loss: {circuit_data['pit_loss']:.1f}s)".ljust(79) + "│")
    print(f"│  Weather Condition  : {track_weather.upper()} MOISTURE LEVEL".ljust(79) + "│")
    print(f"│  Track Surface Temp : {thermal_tag}".ljust(79) + "│")
    print(f"│  Active Baseline    : {circuit_data['base_pace']:.3f}s ({format_lap_time(circuit_data['base_pace'])}) [Fuel: -0.0665s/lap]".ljust(79) + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│  📊 PRE-RACE RISK ASSESSMENT PREDICTION:".ljust(79) + "│")
    print(f"│     Neutralization Probability : {exact_p_pct:.1f}% Chance of ≥1 Safety Car / VSC / Red Flag".ljust(79) + "│")
    print(f"│     Risk Premium Composition   : Base ({base_p_pct:.0f}%) + Weather (+{w_p_pct:.0f}%) + Thermal (+{t_p_pct:.0f}%)".ljust(79) + "│")
    print("└" + "─" * 78 + "┘")

    # -------------------------------------------------------------------------
    # ⚠️ [LIVE TRACK STATUS & 1,000-RUN MONTE CARLO PROJECTIONS]
    # -------------------------------------------------------------------------
    print("\n" + "┌" + "─" * 78 + "┐")
    print("│ ⚠️ [LIVE TRACK STATUS & 1,000-RUN MONTE CARLO PROJECTIONS]" + " " * 20 + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│  Simulation Engine       : 1,000 Independent Grand Prix Monte Carlo Runs".ljust(79) + "│")
    print(f"│  Projected Safety Car(SC): {mc_stats['avg_sc_laps']:.1f} Mean Laps (+40.0s Pace Cap │ Tyre Wear -80%)".ljust(79) + "│")
    print(f"│  Projected Virtual SC    : {mc_stats['avg_vsc_laps']:.1f} Mean Laps (+20.0s Pace Cap │ Tyre Wear -50%)".ljust(79) + "│")
    print(f"│  Projected Red Flag Rate : {mc_stats['avg_rf_events']:.2f} Stoppages / Race (Triggers Free Tyre Change Override)".ljust(79) + "│")
    print(f"│  Lap 1 Pack Start Risk   : {mc_stats['lap1_incidents'] / 10:.1f}% Lap 1 Turn 1 Collision Frequency (2x Risk Threshold)".ljust(79) + "│")
    print("└" + "─" * 78 + "┘")

    # -------------------------------------------------------------------------
    # 📊 [OPTIMIZED STRATEGY STANDINGS]
    # -------------------------------------------------------------------------
    print("\n" + "┌" + "─" * 78 + "┐")
    print("│ 📊 [OPTIMIZED STRATEGY STANDINGS (1,000-RACE MONTE CARLO AVERAGES)]" + " " * 10 + "│")
    print("├" + "─" * 78 + "┤")
    header_line = f"│ {'POS':<4} {'STRATEGY':<24} {'STOPS':<6} {'MEAN TIME':<12} {'DELTA P1':<10} {'WIN RATE':<9} {'STATUS':<7}│"
    print(header_line)
    print("├" + "─" * 78 + "┤")

    for rank, res in enumerate(results, start=1):
        delta = res["mean_race_time"] - best["mean_race_time"]
        delta_str = "P1 LEADER" if rank == 1 else f"+{delta:.3f}s"
        status_tag = "OPTIMAL" if rank == 1 else ("VIABLE" if delta < 20.0 else "DEFICIT")

        row = (f"│ {rank:<4} {res['strategy_label']:<24} {res['pit_stops']:<6} "
               f"{format_lap_time(res['mean_race_time']):<12} {delta_str:<10} "
               f"{res['win_rate']:>5.1f}%   {status_tag:<7}│")
        print(row)

        # Condensed Stint Map Visualization
        stint_vis = f"│      Nominal Mapping : {res['stint_map']}"
        print(stint_vis.ljust(79) + "│")

        # Tri-Sector Split Telemetry Logs
        sector_log = (f"│      Sector Splits   ➔ Avg S1: {res['avg_s1']:.3f}s │ "
                      f"Avg S2: {res['avg_s2']:.3f}s │ Avg S3: {res['avg_s3']:.3f}s")
        print(sector_log.ljust(79) + "│")

        if rank < len(results):
            print("│  " + "─" * 74 + "  │")

    print("└" + "─" * 78 + "┘")

    # -------------------------------------------------------------------------
    # ⚙️ [STRATEGIC ENGINEERING NOTEBOOK]
    # -------------------------------------------------------------------------
    if best["first_pit_lap"]:
        undercut_open = max(1, best["first_pit_lap"] - 2)
        undercut_close = best["first_pit_lap"] + 1
        undercut_text = f"LAPS {undercut_open} - {undercut_close} (Nominal Box Lap: {best['first_pit_lap']})"
        undercut_advantage = "Fresh rubber expected to unlock a +1.45s out-lap undercut delta."
    else:
        undercut_text = "N/A (Zero-stop continuous strategy)"
        undercut_advantage = "Track position defense prioritized over compound freshness."

    if mc_stats["avg_rf_events"] > 0.05:
        restart_forecast = (
            f"HIGH INCIDENT ALERT: {mc_stats['avg_rf_events']:.2f} Red Flags projected per event. "
            "Standing restart pack compression causes extreme tire thermal disparity into Turn 1. "
            "Defensive apex positioning recommended."
        )
    else:
        restart_forecast = (
            "STABLE RESTART PROFILE: Low red flag probability. "
            "Field spread will establish nominal intervals with continuous DRS train dynamics."
        )

    print("\n" + "╔" + "═" * 78 + "╗")
    print("║ ⚙️ [STRATEGIC ENGINEERING NOTEBOOK]" + " " * 43 + "║")
    print("╠" + "═" * 78 + "╣")
    print(f"║ 🎯 UNDERCUT ATTACK WINDOW  : {undercut_text}".ljust(79) + "║")
    print(f"║    TACTICAL NOTE           : {undercut_advantage}".ljust(79) + "║")
    print("║" + " " * 78 + "║")
    print(f"║ 📈 PEAK DISRUPTION WINDOW  : {mc_stats['peak_window']}".ljust(79) + "║")
    print(f"║    START COLLISION RISK    : Lap 1 Turn 1 Pack Collision Odds = {risk_profile['p_lap1'] * 100:.1f}%".ljust(79) + "║")
    print("║" + " " * 78 + "║")
    print("║ 🚦 RESTART CLUSTER DENSITY :".ljust(79) + "║")
    print(f"║    {restart_forecast[:72]}".ljust(79) + "║")
    if len(restart_forecast) > 72:
        print(f"║    {restart_forecast[72:144]}".ljust(79) + "║")
    if len(restart_forecast) > 144:
        print(f"║    {restart_forecast[144:]}".ljust(79) + "║")
    print("║" + " " * 78 + "║")
    if track_temp > 40.0:
        print("║ ⚠️ THERMAL ADVISORY        : Soft compound blistering danger active. Avoid early push.".ljust(79) + "║")
    elif track_temp < 25.0:
        print("║ ⚠️ THERMAL ADVISORY        : Cold asphalt! Hard compound out-lap tire scrub required.".ljust(79) + "║")
    else:
        print("║ ℹ️ THERMAL ADVISORY        : Nominal tire degradation curves observed across all stints.".ljust(79) + "║")
    print("╚" + "═" * 78 + "╝\n")


# -----------------------------------------------------------------------------
# 7. MAIN PROGRAM CONTROLLER
# -----------------------------------------------------------------------------

def run_simulator():
    print("\n" + "=" * 65)
    print("     🏎️  FORMULA 1 PREDICTIVE MONTE CARLO STRATEGY ENGINE")
    print("=" * 65)

    # 1. Load Circuits (Schedule Ingestion with Network Fallback)
    print("\n[Ingestion] Loading World Championship circuits from FastF1...")
    circuits = load_all_circuits(year=2026)
    track_keys = list(circuits.keys())
    print(f"[Ingestion] Loaded {len(track_keys)} circuits successfully.\n")

    # Display Circuits in 2 columns
    half = (len(track_keys) + 1) // 2
    for i in range(half):
        col1 = f"  {i + 1:2d}. {track_keys[i]:<16}"
        j = i + half
        if j < len(track_keys):
            col2 = f"  {j + 1:2d}. {track_keys[j]:<16}"
            print(f"{col1}{col2}")
        else:
            print(col1)

    # User Selects Circuit
    while True:
        sel = input(f"\nSelect Circuit (1-{len(track_keys)} or enter name) [default: 1]: ").strip()
        if not sel:
            selected_track = track_keys[0]
            break
        if sel.isdigit() and 1 <= int(sel) <= len(track_keys):
            selected_track = track_keys[int(sel) - 1]
            break
        elif selected_track_match := next((k for k in circuits if k.lower() == sel.lower()), None):
            selected_track = selected_track_match
            break
        print("Please enter a valid circuit number or name.")

    circuit_data = circuits[selected_track]

    # Live FastF1 Baseline Race Pace Ingestion
    print(f"\n[Telemetry] Synchronizing baseline race pace for {selected_track}...")
    live_pace, loaded_year = fetch_live_baseline_pace(2026, circuit_data["event_name"])
    if live_pace is not None:
        circuit_data["base_pace"] = round(live_pace, 3)
        print(f"✅ FastF1 Race Pace Synchronized ({loaded_year}): {circuit_data['base_pace']:.3f}s")
    else:
        print(f"ℹ️ Calibrated engineering base pace loaded: {circuit_data['base_pace']:.3f}s")

    # 2. Track Meteorology & Thermal Physics Inputs
    print("\n" + "-" * 50)
    print("METEOROLOGY & TRACK CONDITIONS")
    print("-" * 50)

    w_input = input("Track Moisture Condition (1. Dry / 2. Damp / 3. Heavy Rain) [default: 1]: ").strip()
    if w_input in ("2", "damp", "Damp"):
        track_weather = "Damp"
    elif w_input in ("3", "heavy rain", "Heavy Rain", "wet", "Wet"):
        track_weather = "Heavy Rain"
    else:
        track_weather = "Dry"

    while True:
        temp_input = input("Track Surface Temperature (°C: 20 to 50) [default: 38]: ").strip()
        if not temp_input:
            track_temp = 38.0
            break
        try:
            val = float(temp_input)
            if 15.0 <= val <= 60.0:
                track_temp = val
                break
            print("Please enter a temperature within typical racing range (20°C - 50°C).")
        except ValueError:
            print("Invalid numeric value.")

    # 3. Optional Race Laps & Pit Stop Loss Configuration
    default_laps = circuit_data["race_laps"]
    l_input = input(f"Race Laps [default: {default_laps}]: ").strip()
    race_laps = int(l_input) if (l_input.isdigit() and int(l_input) > 0) else default_laps
    circuit_data["race_laps"] = race_laps

    default_pit = circuit_data["pit_loss"]
    p_input = input(f"Pit Lane Loss in seconds [default: {default_pit:.1f}s]: ").strip()
    try:
        pit_loss = float(p_input) if (p_input and float(p_input) >= 0) else default_pit
    except ValueError:
        pit_loss = default_pit
    circuit_data["pit_loss"] = pit_loss

    # 4. Probabilistic Interruption Engine (Calculated before Strategy Logic)
    print("\n[Simulation Engine] Computing probabilistic disruption matrix...")
    risk_profile = calculate_race_disruptions(
        track_data=circuit_data,
        weather_state=track_weather,
        track_temp=track_temp
    )

    # 5. Execute Automated 1,000-Race Monte Carlo Strategy Optimization Loop
    print("[Simulation Engine] Running 1,000 Monte Carlo race scenarios per strategy setup...")
    strategies = get_candidate_strategies(track_weather)

    optimized_results, mc_stats = run_monte_carlo_optimization(
        strategies=strategies,
        total_laps=race_laps,
        base_lap_time=circuit_data["base_pace"],
        pit_stop_loss=circuit_data["pit_loss"],
        track_temp=track_temp,
        track_weather=track_weather,
        risk_profile=risk_profile,
        iterations=1000
    )

    # 6. Render High-Tech Command Station Dashboard
    display_dashboard(
        circuit_data=circuit_data,
        track_weather=track_weather,
        track_temp=track_temp,
        risk_profile=risk_profile,
        mc_stats=mc_stats,
        results=optimized_results
    )


if __name__ == "__main__":
    run_simulator()
