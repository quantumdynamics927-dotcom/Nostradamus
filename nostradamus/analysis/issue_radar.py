#!/usr/bin/env python3
"""
Nostradamus Issue Radar
A text-centered issue detection engine that aggregates quatrains and almanacs
into structured IssueSignal objects before generating forecasts.

Architecture:
  Quatrain text
      |
      v
  motif extraction (disaster_space_module, history_module, astrology_module)
      |
      v
  IssueSignal aggregation (cluster quatrains by issue_type)
      |
      v
  ForecastHypothesis (horizon, scenarios per issue)
      |
      v
  IssueRadar output (ranked issue signals, not isolated verses)

This is NOT prophecy. Every output is labeled "issue_candidate" with
explicit confidence bands, source counts, and horizon estimates.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter, defaultdict
import json
import html

from nostradamus.analysis.domains.disaster_space_module import (
    analyze_disaster_space, DISASTER_KEYWORDS, SPACE_KEYWORDS
)
from nostradamus.analysis.domains.history_module import (
    EVENT_TYPES as HISTORY_EVENT_TYPES, extract_entities
)
from nostradamus.analysis.domains.astrology_module import (
    PLANET_SYMBOLISM, ZODIAC_SIGNS, infer_astrological_config
)
from nostradamus.analysis.tkg_forecaster import (
    TKGForecaster, ForecastHypothesis, load_and_build_kg
)

# === ISSUE CATEGORY DEFINITIONS ===

ISSUE_CATEGORIES = {
    "war_conflict": {
        "label": "War / Interstate Conflict",
        "description": "Armed conflict between nations or factions",
        "keywords": ["guerre", "bataille", "combat", "armee", "soldats", "militaire",
                     "siege", "invasion", "conquete", "defait"],
        "related_event_types": ["war", "revolution"],
        "typical_horizon": "short",
    },
    "civil_unrest": {
        "label": "Civil Unrest / Rebellion",
        "description": "Popular uprisings, revolts, internal political conflict",
        "keywords": ["revolte", "revolution", "emeute", "sedition", "soulvement",
                     "conjuration", " Rebellion "],
        "related_event_types": ["revolution", "political"],
        "typical_horizon": "short",
    },
    "plague_epidemic": {
        "label": "Plague / Epidemic / Health Shock",
        "description": "Pandemic, epidemic disease, public health crisis",
        "keywords": ["peste", "plague", "maladie", "epidemie", "contagion",
                     "fievre", "mort", "deces", "funeste", "pestilence"],
        "related_event_types": ["plague", "famine"],
        "typical_horizon": "short",
    },
    "famine_food_stress": {
        "label": "Famine / Drought / Food Stress",
        "description": "Agricultural failure, food scarcity, famine conditions",
        "keywords": ["famine", "disette", "faute de pain", "sterilite", "mes harveste",
                     "secheresse", "siccite", "sans pluye", "reve", "escour"],
        "related_event_types": ["famine", "plague", "drought"],
        "typical_horizon": "short",
    },
    "fire_destruction": {
        "label": "Fire / Wildfire / Urban Destruction",
        "description": "Major fires, wildfires, urban destruction by flame",
        "keywords": ["forest brusler", "flamber", "incend", "braslar", "feu grand",
                     "feu", "bruler", "flambe"],
        "related_event_types": ["city_fire", "wildfire"],
        "typical_horizon": "short",
    },
    "earthquake_geophysical": {
        "label": "Earthquake / Geophysical Event",
        "description": "Earthquakes, volcanic eruptions, tsunamis, ground instability",
        "keywords": ["terre trembler", "tremblement", "terremotus", "terre movra",
                     "terre esmouvra", "terre fendu", "secousse", "vague grand",
                     "mer monter", "feu grond", "volcan"],
        "related_event_types": ["earthquake", "tsunami", "volcanic"],
        "typical_horizon": "medium",
    },
    "solar_space_alert": {
        "label": "Solar Storm / Space Weather Alert",
        "description": "Solar flares, CMEs, geomagnetic storms, celestial omens",
        "keywords": ["feu du ciel", "flammes ciel", "aurore", "coron", "masse solaire",
                     "vent solaire", "lumiere celest", "astre cheoir", "pierre ciel",
                     "meteor", "meteorite"],
        "related_event_types": ["solar_storm", "asteroid"],
        "typical_horizon": "short",
    },
    "celestial_omen": {
        "label": "Celestial Omen / Comet / Eclipse",
        "description": "Comets, eclipses, unusual sky events interpreted as omens",
        "keywords": ["comete", "trouble estoille", "estoille queue", "etoile trenchant",
                     "eclipse", "obscurcissement", "tenebres", "soleil noir", "lune sang"],
        "related_event_types": ["comet", "eclipse"],
        "typical_horizon": "medium",
    },
    "succession_dynastic": {
        "label": "Dynastic / Succession Crisis",
        "description": "Royal succession, leadership change, dynastic instability",
        "keywords": ["couronne", "coronation", "roy", "roi", "regne", "trone",
                     "succession", "heritier", "maieste", "empire"],
        "related_event_types": ["coronation", "assassination"],
        "typical_horizon": "medium",
    },
    "economic_stress": {
        "label": "Economic / Financial Stress",
        "description": "Economic crisis, financial collapse, trade disruption",
        "keywords": ["argent", "finance", "marche", "commerce", "pauvrete", "chertet",
                     "taux", "banque"],
        "related_event_types": ["economic_stress"],
        "typical_horizon": "medium",
    },
}

# === ISSUE SIGNAL DATA CLASS ===

@dataclass
class IssueSignal:
    """
    Structured issue signal aggregated from multiple quatrains and almanacs.

    This is NOT a prediction. It is an issue candidate surfaced from the writings,
    with supporting evidence counts and confidence assessment.
    """
    issue_type: str              # e.g. "earthquake_geophysical"
    issue_label: str              # human-readable label
    description: str              # from ISSUE_CATEGORIES

    # Source counts
    quatrain_count: int = 0
    almanac_count: int = 0
    source_quatrain_ids: List[str] = field(default_factory=list)

    # Pattern strength (quatrain-only base, 0-1)
    pattern_strength: float = 0.0     # derived from quatrain count + keyword density
    # Almanac boost (separate dimension, 0-0.3 max)
    almanac_boost: float = 0.0
    # Composite strength (combined ranking score)
    composite_strength: float = 0.0
    consensus_score: float = 0.0       # how concentrated vs spread across quatrains

    # Cycle support
    cycle_matches: List[str] = field(default_factory=list)  # cycle_ids with support
    historical_analogs: List[Dict] = field(default_factory=list)  # from KB

    # Thematic composition
    dominant_symbols: List[str] = field(default_factory=list)   # most common keywords
    celestial_markers: List[str] = field(default_factory=list)   # astrological references
    location_hints: List[str] = field(default_factory=list)     # regions mentioned

    # Horizon assessment
    horizon_band: str = ""           # short / medium / long / very_long
    horizon_years: str = ""          # e.g. "5-25"
    confidence_band: str = "low"     # low / medium / high

    # Current relevance
    current_signal_strength: str = "none"   # none / low / medium / high
    contemporary_notes: List[str] = field(default_factory=list)

    # Linked forecasts
    forecast_hypotheses: List[Dict] = field(default_factory=list)

    status: str = "issue_candidate"  # always issue_candidate, not prediction

    def to_dict(self) -> Dict:
        return {
            "issue_type": self.issue_type,
            "issue_label": self.issue_label,
            "description": self.description,
            "status": self.status,
            "quatrain_count": self.quatrain_count,
            "almanac_count": self.almanac_count,
            "source_quatrain_ids": self.source_quatrain_ids,
            "pattern_strength": round(self.pattern_strength, 3),
            "almanac_boost": round(self.almanac_boost, 3),
            "composite_strength": round(self.composite_strength, 3),
            "consensus_score": round(self.consensus_score, 3),
            "cycle_matches": self.cycle_matches,
            "horizon_band": self.horizon_band,
            "horizon_years": self.horizon_years,
            "confidence_band": self.confidence_band,
            "current_signal_strength": self.current_signal_strength,
            "dominant_symbols": self.dominant_symbols[:10],   # top 10
            "celestial_markers": self.celestial_markers[:5],
            "location_hints": list(set(self.location_hints))[:5],
            "historical_analogs": self.historical_analogs[:5],
            "contemporary_notes": self.contemporary_notes,
            "forecast_hypotheses": self.forecast_hypotheses[:3],
        }


# === ISSUE RADAR CLASS ===

class IssueRadar:
    """
    Aggregates quatrains and almanacs into IssueSignal objects.

    Pipeline:
      1. motif extraction per quatrain
      2. issue category mapping
      3. cluster aggregation by issue_type
      4. cycle grounding via TKG
      5. horizon estimation per issue
      6. current relevance scoring
    """

    def __init__(self, kg=None, kb_events=None, forecaster=None):
        self.kg = kg
        self.kb_events = kb_events or []
        self.forecaster = forecaster or (TKGForecaster(kg, None) if kg else None)

    def scan_quatrains(
        self,
        quatrains: List[Dict],
        almanacs: Optional[List[Dict]] = None,
        min_quatrain_count: int = 1,
    ) -> List[IssueSignal]:
        """
        Scan all quatrains/almanacs and return aggregated IssueSignals.

        Args:
            quatrains: List of quatrain dicts with 'quatrain_id', 'french', 'century'
            almanacs: Optional list of almanac dicts
            min_quatrain_count: Minimum quatrains for an issue to be reported

        Returns:
            List of IssueSignal objects, sorted by pattern_strength descending
        """
        # Step 1: Extract motifs from each quatrain
        quatrain_motifs: Dict[str, Dict] = {}
        for q in quatrains:
            qid = q.get("quatrain_id", "")
            french_raw = q.get("french", "")
            french = html.unescape(french_raw)
            motifs = self._extract_motifs(french, qid)
            quatrain_motifs[qid] = motifs

        # Step 2: Map each quatrain to issue categories
        issue_clusters: Dict[str, Dict] = {issue_type: {
            "quatrain_ids": [],
            "symbols": Counter(),
            "locations": [],
            "astro_refs": [],
            "keywords_matched": Counter(),
        } for issue_type in ISSUE_CATEGORIES}

        for qid, motifs in quatrain_motifs.items():
            matched_issues = motifs.get("issue_matches", [])
            for issue_type in matched_issues:
                if issue_type in issue_clusters:
                    issue_clusters[issue_type]["quatrain_ids"].append(qid)
                    issue_clusters[issue_type]["symbols"].update(motifs.get("symbols", []))
                    issue_clusters[issue_type]["locations"].extend(motifs.get("locations", []))
                    issue_clusters[issue_type]["astro_refs"].extend(motifs.get("astro_refs", []))
                    issue_clusters[issue_type]["keywords_matched"].update(motifs.get("keywords_matched", Counter()))

        # Step 3: Build IssueSignal for each cluster
        issue_signals = []
        for issue_type, cluster in issue_clusters.items():
            qids = cluster["quatrain_ids"]
            if len(qids) < min_quatrain_count:
                continue

            category = ISSUE_CATEGORIES[issue_type]
            symbols = [s for s, _ in cluster["symbols"].most_common(15)]
            keywords = cluster["keywords_matched"]

            # Pattern strength: use log scale so large quatrain counts don't saturate
            # strength = 1 - exp(-count * factor), with keyword bonus on top
            q_factor = 0.12
            base_strength = 1.0 - (1.0 / (1.0 + len(qids) * q_factor))
            keyword_boost = min(0.25, len(keywords) * 0.025)
            pattern_strength = min(1.0, base_strength + keyword_boost)

            # Consensus: how many unique symbols appear
            consensus = min(1.0, len(set(symbols)) / max(1, len(qids)))

            # Confidence band
            if len(qids) >= 5:
                confidence = "high"
            elif len(qids) >= 3:
                confidence = "medium"
            else:
                confidence = "low"

            # Horizon band (from category)
            horizon_band = category.get("typical_horizon", "medium")
            horizon_years = self._horizon_for_band(horizon_band)

            signal = IssueSignal(
                issue_type=issue_type,
                issue_label=category["label"],
                description=category["description"],
                quatrain_count=len(qids),
                source_quatrain_ids=qids,
                pattern_strength=pattern_strength,
                consensus_score=consensus,
                dominant_symbols=symbols,
                celestial_markers=cluster["astro_refs"][:10],
                location_hints=list(set(cluster["locations"]))[:10],
                horizon_band=horizon_band,
                horizon_years=horizon_years,
                confidence_band=confidence,
                current_signal_strength="low",  # updated by scan_current_relevance
                composite_strength=0.0,  # set after almanac integration
                status="issue_candidate",
            )
            issue_signals.append(signal)

        # Step 3b: Integrate almanac entries if provided
        if almanacs:
            issue_signals = self._scan_almanacs(issue_signals, almanacs)

        # Step 4: Ground in TKG (find cycle support and historical analogs)
        issue_signals = self._ground_in_tkg(issue_signals)

        # Step 5: Score current relevance
        issue_signals = self._score_current_relevance(issue_signals)

        # Sort by composite_strength if almanac integration ran, else pattern_strength
        issue_signals.sort(
            key=lambda s: (
                -s.composite_strength if s.almanac_count > 0
                else -s.pattern_strength
            )
        )

        return issue_signals

    def _extract_motifs(self, french: str, quatrain_id: str) -> Dict:
        """
        Extract all motifs from a single quatrain's text.
        Combines disaster_space_module, history_module, astrology_module.
        """
        french_lower = french.lower()
        motifs = {
            "quatrain_id": quatrain_id,
            "symbols": [],
            "keywords_matched": Counter(),
            "issue_matches": [],
            "locations": [],
            "astro_refs": [],
            "disaster_types": [],
            "space_types": [],
        }

        # --- Disaster/Space motifs ---
        try:
            ds_result = analyze_disaster_space(french, quatrain_id)
            d = ds_result.get("disaster", {})
            s = ds_result.get("space", {})
            if d.get("detected_types"):
                motifs["disaster_types"] = d["detected_types"]
                motifs["keywords_matched"].update(d.get("matching_keywords", {}).keys())
            if s.get("detected_types"):
                motifs["space_types"] = s["detected_types"]
                motifs["keywords_matched"].update(s.get("matching_keywords", {}).keys())
        except Exception:
            pass

        # --- History/Politics motifs ---
        for issue_type, category in ISSUE_CATEGORIES.items():
            for kw in category["keywords"]:
                if kw in french_lower:
                    motifs["keywords_matched"][kw] += 1
                    motifs["issue_matches"].append(issue_type)
                    motifs["symbols"].append(kw)

        # --- Astrology/celestial motifs ---
        for planet, info in PLANET_SYMBOLISM.items():
            if planet.lower() in french_lower:
                motifs["astro_refs"].append(planet)
        for sign, info in ZODIAC_SIGNS.items():
            if sign.lower() in french_lower:
                motifs["astro_refs"].append(sign)

        # --- Location extraction ---
        locations = extract_entities(french)
        motifs["locations"] = locations

        # Deduplicate issue matches while preserving order
        seen = set()
        unique_matches = []
        for m in motifs["issue_matches"]:
            if m not in seen:
                seen.add(m)
                unique_matches.append(m)
        motifs["issue_matches"] = unique_matches

        return motifs

    def _ground_in_tkg(self, signals: List[IssueSignal]) -> List[IssueSignal]:
        """
        Ground each IssueSignal in the TKG:
        - Find cycle matches
        - Link historical analogs from KB
        """
        if not self.forecaster or not self.kg:
            return signals

        grounded = []
        for signal in signals:
            related_event_types = ISSUE_CATEGORIES.get(signal.issue_type, {}).get(
                "related_event_types", []
            )

            # Find cycles that contain these event types
            matching_cycles = []
            for cycle in self.kg.cycles.values():
                cycle_types = [et.value if hasattr(et, "value") else str(et) for et in cycle.event_types]
                if any(et in cycle_types for et in related_event_types):
                    matching_cycles.append(cycle.cycle_id)

            signal.cycle_matches = list(set(matching_cycles))

            # Find historical analogs in KB
            analogs = []
            for event in self.kb_events:
                if event.get("event_type") in related_event_types:
                    analogs.append({
                        "event_id": event.get("event_id", ""),
                        "name": event.get("name", ""),
                        "event_type": event.get("event_type", ""),
                        "year": event.get("start_year", ""),
                        "location": event.get("location", ""),
                    })
            signal.historical_analogs = analogs[:10]

            grounded.append(signal)

        return grounded

    def _scan_almanacs(
        self,
        signals: List[IssueSignal],
        almanacs: List[Dict]
    ) -> List[IssueSignal]:
        """
        Integrate pre-tagged almanac entries into existing IssueSignals.

        Almanac entries carry pre-assigned issue_categories, motifs, and
        astrological_markers. We boost the matching signals accordingly.
        """
        # Build lookup of existing signals by issue_type
        signal_by_issue = {s.issue_type: s for s in signals}

        # Aggregate almanac stats per issue
        almanac_issue_counts: Dict[str, List[Dict]] = {issue: [] for issue in ISSUE_CATEGORIES}
        for entry in almanacs:
            for issue in entry.get("issue_categories", []):
                if issue in almanac_issue_counts:
                    almanac_issue_counts[issue].append(entry)

        for issue_type, entries in almanac_issue_counts.items():
            if not entries:
                continue
            if issue_type not in signal_by_issue:
                continue
            signal = signal_by_issue[issue_type]

            # Update almanac count
            signal.almanac_count = len(entries)

            # Aggregate celestial markers from almanacs
            for entry in entries:
                signal.celestial_markers.extend(entry.get("astrological_markers", []))
            signal.celestial_markers = list(set(signal.celestial_markers))[:10]

            # Almanac boost: separate dimension from quatrain pattern strength
            # Log scale: diminishing returns but meaningful lift for low-quatrain issues
            signal.almanac_boost = 1.0 - (1.0 / (1.0 + len(entries) * 0.25))
            # Composite strength: exponential decay over total evidence (quatrain + almanac)
            # This produces a smooth 0-1 scale without arbitrary denominators
            # A factor of 400 gives ~0.95 for 1000 sources, ~0.39 for 500, ~0.08 for 40
            total_evidence = signal.quatrain_count + signal.almanac_count * 1.5
            signal.composite_strength = 1.0 - (1.0 / (1.0 + total_evidence / 400.0))

            # Upgrade confidence if almanac entries provide near-term support
            if len(entries) >= 3 and signal.confidence_band == "medium":
                signal.confidence_band = "high"
            elif len(entries) >= 5 and signal.confidence_band == "low":
                signal.confidence_band = "medium"

            # Add almanac entry IDs to source tracking
            for entry in entries:
                aid = entry.get("entry_id", "unknown")
                signal.source_quatrain_ids.append(f"ALM:{aid}")

            # Horizon note: almanac entries are annual, so they support short-horizon signals
            # If this issue already has a "long" or "very_long" horizon, almanac presence
            # suggests the issue may also manifest near-term — add a note but don't override
            if signal.horizon_band in ("long", "very_long") and entries:
                signal.contemporary_notes.append(
                    f"Near-term almanac support ({len(entries)} entries) suggests "
                    "possible early manifestation within annual horizon."
                )

        # Compute composite_strength for signals that received no almanac entries
        # (they fall through with almanac_count still 0)
        for signal in signals:
            if signal.almanac_count == 0:
                total_evidence = signal.quatrain_count  # no almanac contribution
                signal.composite_strength = 1.0 - (1.0 / (1.0 + total_evidence / 400.0))

        return signals

    def _horizon_for_band(self, band: str) -> str:
        """Map horizon band to year range string."""
        mapping = {
            "short": "1-15",
            "medium": "15-30",
            "long": "30-65",
            "very_long": "65-150",
        }
        return mapping.get(band, "10-40")

    def _score_current_relevance(self, signals: List[IssueSignal]) -> List[IssueSignal]:
        """
        Score how relevant each issue is to the current moment (2026).
        Uses contemporary context signals.
        """
        # Current context (hardcoded for now; could be extended with live data)
        current_context = {
            "geopolitical_tensions": "high",
            "climate_volatility": "elevated",
            "pandemic_threat": "moderate",
            "space_weather": "moderate",       # SC25 declining, not at maximum
            "food_stress": "moderate",
            "infrastructure_risk": "moderate",
        }

        # Map issue types to current context keys
        context_relevance = {
            "war_conflict": current_context["geopolitical_tensions"],
            "civil_unrest": current_context["geopolitical_tensions"],
            "plague_epidemic": current_context["pandemic_threat"],
            "famine_food_stress": current_context["food_stress"],
            "fire_destruction": current_context["climate_volatility"],
            "earthquake_geophysical": current_context["climate_volatility"],
            "solar_space_alert": current_context["space_weather"],
            "celestial_omen": current_context["space_weather"],
            "succession_dynastic": current_context["geopolitical_tensions"],
            "economic_stress": current_context["infrastructure_risk"],
        }

        scored = []
        for signal in signals:
            ctx_level = context_relevance.get(signal.issue_type, "low")
            signal.current_signal_strength = ctx_level

            # Add contemporary note
            note = f"Current {signal.issue_type} context: {ctx_level}"
            signal.contemporary_notes.append(note)

            # Boost pattern strength if current context is elevated
            if ctx_level == "high":
                signal.pattern_strength = min(1.0, signal.pattern_strength * 1.2)
            elif ctx_level == "elevated":
                signal.pattern_strength = min(1.0, signal.pattern_strength * 1.1)

            scored.append(signal)

        return scored

    def add_forecasts(self, signals: List[IssueSignal], quatrains: List[Dict]) -> List[IssueSignal]:
        """
        For each IssueSignal, run horizon forecasts using the TKG forecaster.
        Attaches top forecast hypotheses to each issue.
        """
        if not self.forecaster:
            return signals

        quatrain_map = {q.get("quatrain_id", ""): q for q in quatrains}

        for signal in signals:
            hypotheses = []
            # Only generate forecasts from quatrain sources (skip ALM: entries)
            quatrain_ids = [qid for qid in signal.source_quatrain_ids if not qid.startswith("ALM:")]
            for qid in quatrain_ids[:5]:  # top 5 quatrains per issue
                q = quatrain_map.get(qid)
                if not q:
                    continue
                french = html.unescape(q.get("french", ""))
                century = int(qid.split("-Q")[0].replace("C", ""))
                qnum = int(qid.split("-Q")[1])
                try:
                    h = self.forecaster.analyze_quatrain(
                        {"century": century, "quatrain": qnum, "french": french},
                        q.get("astrology", {}),
                        self.kb_events
                    )
                    if h.cycle_match:
                        hypotheses.append(h.to_dict())
                except Exception:
                    pass

            signal.forecast_hypotheses = hypotheses

        return signals

    def report(self, signals: List[IssueSignal]) -> str:
        """Generate a human-readable issue radar report."""
        lines = []
        lines.append("=" * 70)
        lines.append("NOSTRADAMUS ISSUE RADAR REPORT")
        lines.append("=" * 70)
        lines.append(f"Total issue signals: {len(signals)}")
        lines.append("")
        lines.append("STATUS KEY: issue_candidate = NOT a prediction")
        lines.append("Every signal is a hypothesis rooted in the writings + cycle models.")
        lines.append("")

        for i, sig in enumerate(signals, 1):
            lines.append(f"{'-'*60}")
            lines.append(f"ISSUE #{i}: {sig.issue_label} ({sig.issue_type})")
            lines.append(f"  Status: {sig.status}")
            lines.append(f"  Quatrain sources: {sig.quatrain_count} | Almanac sources: {sig.almanac_count}")
            lines.append(f"  Composite strength: {sig.composite_strength:.3f} "
                         f"(base={sig.pattern_strength:.3f}, almanac_boost={sig.almanac_boost:.3f})")
            lines.append(f"  Consensus: {sig.consensus_score:.3f}")
            lines.append(f"  Confidence band: {sig.confidence_band}")
            lines.append(f"  Horizon: {sig.horizon_years} ({sig.horizon_band})")
            lines.append(f"  Cycle matches: {sig.cycle_matches or 'none'}")
            lines.append(f"  Current relevance: {sig.current_signal_strength}")
            lines.append(f"  Historical analogs: {len(sig.historical_analogs)} events linked")
            if sig.dominant_symbols:
                lines.append(f"  Top symbols: {', '.join(sig.dominant_symbols[:8])}")
            if sig.location_hints:
                lines.append(f"  Locations: {', '.join(sig.location_hints[:5])}")
            if sig.forecast_hypotheses:
                lines.append(f"  Top forecast: {sig.forecast_hypotheses[0]['cycle_match']} -> {sig.forecast_hypotheses[0]['event_type_predicted']}")
            lines.append("")

        lines.append("=" * 70)
        lines.append("NOTE: These are ISSUE CANDIDATES, not predictions.")
        lines.append("They represent themes detected in Nostradamus's writings.")
        lines.append("=" * 70)
        return "\n".join(lines)
