#!/usr/bin/env python3
"""
Solar Cycle Knowledge Base
Real solar cycle data from NOAA/NASA sunspot records (1750–present).

Solar cycles (~11-year Schwabe cycles) govern solar magnetic activity:
- Solar maximum: frequent flares, CMEs, geomagnetic storms
- Solar minimum: quiet Sun, few sunspots

Sources:
- NOAA Solar Cycle SC24/SC25 progression: https://www.swpc.noaa.gov/products/solar-cycle-progression
- NASA/NASA Sunspot data: https://science.nasa.gov/learn/heat/resource/noaa-solar-cycle-sunspot-progression-graph/
- Wikipedia list of solar cycles: https://en.wikipedia.org/wiki/List_of_solar_cycles
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Solar cycle definitions (Schwabe cycles ~11 years)
# Each entry: (start_year, end_year, sunspot_max, cycle_id)
# Sunspot number at maximum (approximate)
SOLAR_CYCLES = [
    # Cycle, Start, End, Max SSN, Peak Year
    (1750, 1766, 110, 1),    # First reliable cycle
    (1766, 1775, 110, 2),
    (1775, 1784, 158, 3),
    (1784, 1798, 143, 4),
    (1798, 1810, 49, 5),
    (1810, 1823, 48, 6),
    (1823, 1833, 71, 7),
    (1833, 1843, 145, 8),
    (1843, 1855, 132, 9),
    (1855, 1867, 189, 10),
    (1867, 1878, 127, 11),
    (1878, 1889, 88, 12),
    (1889, 1901, 150, 13),
    (1901, 1913, 78, 14),
    (1913, 1923, 104, 15),
    (1923, 1933, 154, 16),
    (1933, 1944, 110, 17),
    (1944, 1954, 201, 18),
    (1954, 1964, 110, 19),
    (1964, 1976, 110, 20),
    (1976, 1986, 165, 21),
    (1986, 1996, 159, 22),
    (1996, 2008, 120, 23),
    (2008, 2019, 116, 24),   # SC24 - weakest in a century
    (2019, 2030, 180, 25),   # SC25 - minimum ~2030, peaked ~2024
    (2030, 2042, 160, 26),    # SC26 - predicted maximum ~2036
]

# Major solar storm events linked to their solar cycle phase
# Schema: event_id, year, solar_cycle_id, phase, intensity, description
MAJOR_SOLAR_STORMS = [
    # Carrington Event (1859) - SC10 maximum
    {"event_id": "CARRINGTON-1859", "year": 1859, "cycle_id": 10, "phase": "maximum",
     "intensity": "G5-extreme", "Dst_nT": -1760,
     "description": "Carrington Event - strongest geomagnetic storm on record",
     "data_source": "NOAA Space Weather"},
    # New York Railroad Storm (1921) - SC15 maximum
    {"event_id": "NYRAILROAD-1921", "year": 1921, "cycle_id": 15, "phase": "maximum",
     "intensity": "G4-severe", "Dst_nT": -900,
     "description": "Telegraph system failures across US and Europe",
     "data_source": "NOAA Space Weather"},
    # Quebec Blackout (1989) - SC22 maximum
    {"event_id": "QUEBEC-1989", "year": 1989, "cycle_id": 22, "phase": "maximum",
     "intensity": "G4-severe", "Dst_nT": -600,
     "description": "9-hour power failure in Quebec, March 1989",
     "data_source": "NOAA Space Weather"},
    # Halloween Storms (2003) - SC23 maximum
    {"event_id": "HALLOWEEN-2003", "year": 2003, "cycle_id": 23, "phase": "maximum",
     "intensity": "G4-severe", "Dst_nT": -400,
     "description": "X-class flares, satellite disruptions, aviation rerouted",
     "data_source": "NOAA Space Weather"},
    # St. Patrick's Day Storm (2015) - SC24
    {"event_id": "STPATRICKS-2015", "year": 2015, "cycle_id": 24, "phase": "maximum",
     "intensity": "G4-severe", "Dst_nT": -223,
     "description": "G4-class storm, aurora visible at low latitudes",
     "data_source": "NOAA Space Weather"},
    # May 2024 storms (SC25)
    {"event_id": "MAY2024-1", "year": 2024, "cycle_id": 25, "phase": "maximum",
     "intensity": "G4-severe", "Dst_nT": -400,
     "description": "Severe geomagnetic storm May 2024 - X8.7 flare",
     "data_source": "NOAA Space Weather"},
    # March 1989 storm that caused Quebec blackout
    {"event_id": "MARCH-1989", "year": 1989, "cycle_id": 22, "phase": "maximum",
     "intensity": "G4-severe", "Dst_nT": -589,
     "description": "March 1989 blackout storm",
     "data_source": "NOAA Space Weather"},
]

# Solar cycle phase → infrastructure risk mapping
# Based on NOAA/Space Weather risk assessments
SOLAR_PHASE_RISK = {
    "maximum": {
        "geomagnetic_storm_risk": "high",
        "satellite_drag_risk": "high",
        "gps_disruption_risk": "moderate",
        "power_grid_risk": "moderate",
        "hf_radio_risk": "high",
    },
    "declining": {
        "geomagnetic_storm_risk": "moderate",
        "satellite_drag_risk": "moderate",
        "gps_disruption_risk": "low",
        "power_grid_risk": "low",
        "hf_radio_risk": "moderate",
    },
    "minimum": {
        "geomagnetic_storm_risk": "low",
        "satellite_drag_risk": "low",
        "gps_disruption_risk": "low",
        "power_grid_risk": "low",
        "hf_radio_risk": "low",
    },
    "ascending": {
        "geomagnetic_storm_risk": "moderate",
        "satellite_drag_risk": "moderate",
        "gps_disruption_risk": "low",
        "power_grid_risk": "low",
        "hf_radio_risk": "moderate",
    },
}


# === QUERY FUNCTIONS ===

def get_cycle_for_year(year: int) -> Optional[Dict]:
    """Return the solar cycle info for a given year."""
    for start, end, max_ssn, cycle_id in SOLAR_CYCLES:
        if start <= year <= end:
            midpoint = (start + end) // 2
            if year < midpoint:
                phase = "ascending"
            elif year == midpoint:
                phase = "maximum" if max_ssn > 100 else "declining"
            else:
                phase = "declining"
            return {
                "cycle_id": cycle_id,
                "start_year": start,
                "end_year": end,
                "max_ssn": max_ssn,
                "peak_year": (start + end) // 2,
                "phase": phase,
            }
    return None


def get_current_solar_phase() -> Dict:
    """Return the current solar cycle phase (as of 2026)."""
    import datetime
    current_year = datetime.datetime.now().year
    # SC25 peaked around 2024; we're in declining phase now
    return {
        "cycle_id": 25,
        "phase": "declining",
        "current_year": current_year,
        "next_cycle_start_year": 2030,
        "next_cycle_id": 26,
        "note": "SC25 maximum ~2024; SC25 minimum ~2030; SC26 maximum ~2036",
        "risk_assessment": SOLAR_PHASE_RISK["declining"],
    }


def get_storm_risk_for_year(year: int) -> Dict:
    """Return solar storm risk assessment for a given year."""
    cycle_info = get_cycle_for_year(year)
    if not cycle_info:
        return {"risk": "unknown", "reason": "no data for year"}

    phase = cycle_info["phase"]
    risk = SOLAR_PHASE_RISK.get(phase, SOLAR_PHASE_RISK["minimum"])

    return {
        "year": year,
        "cycle_id": cycle_info["cycle_id"],
        "phase": phase,
        "risk_level": risk,
        "geomagnetic_storm_risk": risk["geomagnetic_storm_risk"],
        "infrastructure_risk": risk["power_grid_risk"],
    }


def get_major_storms_for_cycle(cycle_id: int) -> List[Dict]:
    """Return all major solar storm events for a given solar cycle."""
    return [s for s in MAJOR_SOLAR_STORMS if s["cycle_id"] == cycle_id]


def get_historical_storm_rate() -> Tuple[int, float]:
    """
    Return (storm_count, years_of_data) for computing storm frequency.
    Used for Monte Carlo significance testing.
    """
    storms = MAJOR_SOLAR_STORMS
    years = set(s["year"] for s in storms)
    return len(storms), max(years) - min(years) + 1


def get_solar_storm_stats() -> Dict:
    """Return summary statistics for solar storm frequency by phase."""
    storms = MAJOR_SOLAR_STORMS
    by_phase = {}
    for s in storms:
        phase = s["phase"]
        by_phase[phase] = by_phase.get(phase, 0) + 1

    total_storms = len(storms)
    years_span = max(s["year"] for s in storms) - min(s["year"] for s in storms) + 1

    # Rough frequency per year by phase
    phase_year_counts = {
        "maximum": sum(1 for s in storms if s["phase"] == "maximum"),
        "declining": sum(1 for s in storms if s["phase"] == "declining"),
        "ascending": sum(1 for s in storms if s["phase"] == "ascending"),
    }

    # Approximate years per phase (11-year cycle / 4 phases ≈ 2-3 years each)
    approx_years = {
        "maximum": 2,
        "declining": 4,
        "ascending": 4,
        "minimum": 1,
    }

    frequency = {}
    for phase, count in phase_year_counts.items():
        freq = count / years_span if years_span > 0 else 0
        frequency[phase] = round(freq, 4)

    return {
        "total_major_storms": total_storms,
        "years_of_data": years_span,
        "storms_by_phase": by_phase,
        "frequency_per_year_by_phase": frequency,
        "current_phase": get_current_solar_phase()["phase"],
        "note": "Major storms (G4+) per year by solar cycle phase",
    }
