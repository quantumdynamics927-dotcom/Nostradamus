"""
Pattern Engine - Core of the Nostradamus Analysis System
Turns vague quatrains into structured patterns tested against real events.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import json
from pathlib import Path

# === EVENT SCHEMA DEFINITIONS ===

class EventType(Enum):
    WAR = "war"
    PLAGUE = "plague"
    FAMINE = "famine"
    CORONATION = "coronation"
    REVOLUTION = "revolution"
    ALLIANCE = "alliance"
    ECLIPSE = "eclipse"
    FLOOD = "flood"
    ASSASSINATION = "assassination"
    CITY_FIRE = "city_fire"
    RELIGIOUS_SCHISM = "religious_schism"
    ECONOMIC_STRESS = "economic_stress"
    POLITICAL = "political"
    UNKNOWN = "unknown"
    # Natural Disasters
    EARTHQUAKE = "earthquake"
    TSUNAMI = "tsunami"
    VOLCANIC = "volcanic"
    WILDFIRE = "wildfire"
    DROUGHT = "drought"
    # Space / Planetary Events
    SOLAR_STORM = "solar_storm"
    ASTEROID = "asteroid"
    COMET = "comet"
    # Infrastructure / Technological
    INFRASTRUCTURE = "infrastructure"

class Region(Enum):
    FRANCE = "France"
    ENGLAND = "England"
    SPAIN = "Spain"
    ITALY = "Italy"
    GERMANY = "Germany"
    EUROPE = "Europe"
    OTTOMAN = "Ottoman"
    MEDITERRANEAN = "Mediterranean"
    EAST = "East"
    BELGIUM = "Belgium"
    SCOTLAND = "Scotland"
    PACIFIC_RIM = "Pacific_Rim"
    SOUTH_ASIA = "South_Asia"
    GLOBAL = "Global"
    UNKNOWN = "Unknown"

@dataclass
class EventSchema:
    """
    Structured event schema extracted from a quatrain.
    who, what, where, when, conditions, outcome.
    """
    quatrain_id: str
    event_type: EventType
    primary_actor: Optional[str] = None
    secondary_actors: List[str] = field(default_factory=list)
    location: Region = Region.UNKNOWN
    specific_location: Optional[str] = None
    time_conditions: List[str] = field(default_factory=list)  # astrological conditions
    outcome: Optional[str] = None
    symbols: List[str] = field(default_factory=list)  # animal, color, metal symbols
    planetary_config: Optional[str] = None  # e.g., "Mars-Saturn conjunction"
    confidence: float = 0.0
    extraction_notes: List[str] = field(default_factory=list)

@dataclass
class HistoricalEvent:
    """
    Node in the temporal knowledge graph.
    """
    event_id: str
    name: str
    event_type: EventType
    start_year: int
    end_year: Optional[int] = None
    location: Region = Region.UNKNOWN
    specific_location: Optional[str] = None
    actors: List[str] = field(default_factory=list)
    period_sources: List[str] = field(default_factory=list)  # de Thou, L'Estoile, etc.
    related_events: List[str] = field(default_factory=list)  # event_ids
    description: str = ""
    astrology_notes: Optional[str] = None

@dataclass
class PatternMatch:
    """
    Result of matching a quatrain schema to historical events.
    """
    quatrain_id: str
    event_id: str
    event_name: str
    match_score: float
    matched_components: Dict[str, float]  # entity, location, type, astrological
    cycle_membership: List[str] = field(default_factory=list)  # cycles this match participates in
    is_strong_match: bool = False
    notes: str = ""

@dataclass
class Cycle:
    """
    Cyclical pattern in history.
    e.g., "economic stress -> religious radicalization -> conflict -> regime change"
    """
    cycle_id: str
    name: str
    event_types: List[EventType]
    typical_duration_years: Optional[int] = None
    occurrences: List[str] = field(default_factory=list)  # event_ids
    quatrain_mappings: List[str] = field(default_factory=list)  # quatrain_ids

# === KNOWLEDGE GRAPH ===

class TemporalKnowledgeGraph:
    """
    Temporal knowledge graph of historical events.
    Nodes: HistoricalEvent objects
    Edges: temporal, causal, spatial relationships
    """

    def __init__(self):
        self.events: Dict[str, HistoricalEvent] = {}
        self.cycles: Dict[str, Cycle] = {}
        self._event_index: Dict[Tuple[EventType, Region, int], List[str]] = {}

    def add_event(self, event: HistoricalEvent) -> None:
        self.events[event.event_id] = event
        # Index for fast lookup
        key = (event.event_type, event.location, event.start_year)
        if key not in self._event_index:
            self._event_index[key] = []
        self._event_index[key].append(event.event_id)

    def add_cycle(self, cycle: Cycle) -> None:
        self.cycles[cycle.cycle_id] = cycle

    def query_events(
        self,
        event_type: Optional[EventType] = None,
        location: Optional[Region] = None,
        year_range: Optional[Tuple[int, int]] = None,
        actor: Optional[str] = None
    ) -> List[HistoricalEvent]:
        """Query events by type, location, year range, or actor."""
        results = []
        for event in self.events.values():
            if event_type and event.event_type != event_type:
                continue
            if location and event.location != location:
                continue
            if year_range:
                start, end = year_range
                if event.end_year and event.end_year < start:
                    continue
                if event.start_year > end:
                    continue
            if actor and actor.lower() not in [a.lower() for a in event.actors]:
                continue
            results.append(event)
        return results

    def find_cycles_in_sequence(self, event_ids: List[str]) -> List[str]:
        """Detect which known cycles appear in a sequence of events."""
        found_cycles = []
        for cycle in self.cycles.values():
            # Check if this cycle's event types appear in sequence
            cycle_types = [et.value for et in cycle.event_types]
            event_types_seq = [self.events[eid].event_type.value for eid in event_ids if eid in self.events]

            # Simple subsequence check
            for i in range(len(event_types_seq) - len(cycle_types) + 1):
                if event_types_seq[i:i+len(cycle_types)] == cycle_types:
                    found_cycles.append(cycle.cycle_id)
                    break
        return found_cycles

    def to_json(self) -> Dict:
        return {
            "events": {
                eid: {
                    "event_id": e.event_id,
                    "name": e.name,
                    "event_type": e.event_type.value,
                    "start_year": e.start_year,
                    "end_year": e.end_year,
                    "location": e.location.value,
                    "actors": e.actors,
                    "period_sources": e.period_sources,
                    "related_events": e.related_events
                }
                for eid, e in self.events.items()
            },
            "cycles": {
                cid: {
                    "cycle_id": c.cycle_id,
                    "name": c.name,
                    "event_types": [et.value for et in c.event_types],
                    "occurrences": c.occurrences
                }
                for cid, c in self.cycles.items()
            }
        }

    @classmethod
    def from_json(cls, data: Dict) -> "TemporalKnowledgeGraph":
        kg = cls()
        for eid, edata in data.get("events", {}).items():
            event = HistoricalEvent(
                event_id=edata["event_id"],
                name=edata["name"],
                event_type=EventType(edata["event_type"]),
                start_year=edata["start_year"],
                end_year=edata.get("end_year"),
                location=Region(edata.get("location", "UNKNOWN")),
                actors=edata.get("actors", []),
                period_sources=edata.get("period_sources", []),
                related_events=edata.get("related_events", [])
            )
            kg.add_event(event)
        for cid, cdata in data.get("cycles", {}).items():
            cycle = Cycle(
                cycle_id=cdata["cycle_id"],
                name=cdata["name"],
                event_types=[EventType(et) for et in cdata["event_types"]],
                occurrences=cdata.get("occurrences", [])
            )
            kg.add_cycle(cycle)
        return kg

# === PATTERN ENGINE ===

class PatternEngine:
    """
    Core pattern matching engine.
    For each quatrain:
    1. Builds event schemas from text + symbols
    2. Queries historical graph for matches
    3. Weighs astrological context
    4. Computes validation scores
    5. Identifies cycle membership
    """

    def __init__(self, knowledge_graph: TemporalKnowledgeGraph):
        self.kg = knowledge_graph
        self.matches: List[PatternMatch] = []

    def extract_schema(self, quatrain: Dict, astrology_config: Dict) -> EventSchema:
        """
        Extract structured event schema from a quatrain.
        Uses: event type keywords, location keywords, astrology config.
        """
        text = quatrain.get("french", "").lower()
        qid = f"C{quatrain['century']}-Q{quatrain['quatrain']}"

        # Extract event type
        event_type = self._infer_event_type(text)

        # Extract actors
        actors = self._extract_actors(text)

        # Extract location
        location = self._infer_location(text)

        # Extract symbols
        symbols = self._extract_symbols(text)

        # Extract astrological conditions
        astro_refs = astrology_config.get("references", [])
        planetary_config = None
        if astro_refs:
            planets = [r["name"] for r in astro_refs if r["type"] == "planet"]
            if planets:
                planetary_config = "-".join(planets)

        return EventSchema(
            quatrain_id=qid,
            event_type=event_type,
            primary_actor=actors[0] if actors else None,
            secondary_actors=actors[1:],
            location=location,
            symbols=symbols,
            planetary_config=planetary_config,
            confidence=0.5  # initial confidence
        )

    def _infer_event_type(self, text: str) -> EventType:
        """Infer event type from text keywords."""
        type_keywords = {
            EventType.WAR: ["guerre", "bataille", "combat", "armee", "soldats", "militaire"],
            EventType.PLAGUE: ["peste", "plague", "maladie", "epidemie", "mort", "deces"],
            EventType.FAMINE: ["famine", "disette", "reve", "sterilite"],
            EventType.CORONATION: ["couronne", "roi", "coronation", "regne", "trone"],
            EventType.REVOLUTION: ["revolte", "revolution", "emeute", "sedition"],
            EventType.ALLIANCE: ["alliance", "mariage", "traite", "paix"],
            EventType.ECLIPSE: ["eclipse", "obscurcissement", "tenebres"],
            EventType.FLOOD: ["inondation", "deluge", "pluie", "eaux"],
            EventType.ASSASSINATION: ["assassin", "tuer", "meurtre", "mort traytre"],
            EventType.CITY_FIRE: ["feu", "bruler", "incendie", "flambe"],
            EventType.POLITICAL: ["senat", "peuple", "republique", "empire", "prince"],
        }

        for et, keywords in type_keywords.items():
            if any(kw in text for kw in keywords):
                return et
        return EventType.UNKNOWN

    def _extract_actors(self, text: str) -> List[str]:
        """Extract named actors from text."""
        actors = []
        # Roman/Greek names commonly in Nostradamus
        known_actors = {
            "heliogabale": "Heliogabalus", "nero": "Nero", "cesar": "Caesar",
            "auguste": "Augustus", "constantin": "Constantine",
            "mahomet": "Muhammad", "soliman": "Suleiman",
            "marc": "Marc Antony", "brutus": "Brutus",
            "henri": "Henri", "lou": "Louis", "charles": "Charles"
        }
        for name, full_name in known_actors.items():
            if name in text:
                actors.append(full_name)
        return actors

    def _infer_location(self, text: str) -> Region:
        """Infer geographical region from text."""
        location_keywords = {
            Region.FRANCE: ["france", "francais", "paris", "lyon", "marseille"],
            Region.ENGLAND: ["angleterre", "anglais", "londres"],
            Region.SPAIN: ["espagne", "espagnol", "madrid"],
            Region.ITALY: ["italie", "rome", "florence"],
            Region.GERMANY: ["allemagne", "allemand"],
            Region.OTTOMAN: ["turc", "ottoman", "constantin"],
        }
        for region, keywords in location_keywords.items():
            if any(kw in text for kw in keywords):
                return region
        return Region.UNKNOWN

    def _extract_symbols(self, text: str) -> List[str]:
        """Extract symbolic references (animals, colors, metals)."""
        symbols = []
        symbolic_keywords = {
            "lion": ["lion", "leo"],
            "aigle": ["aigle", "eagle"],
            "corbeau": ["corbeau", "raven"],
            "loup": ["loup", "wolf"],
            "serpent": ["serpent", "snake"],
            "soleil": ["soleil", "sun"],
            "lune": ["lune", "moon"],
            "feu": ["feu", "fire"],
            "or": ["or", "gold"],
            "argent": ["argent", "silver"],
            "rouge": ["rouge", "red"],
            "bleu": ["bleu", "blue"],
        }
        for symbol, keywords in symbolic_keywords.items():
            if any(kw in text for kw in keywords):
                symbols.append(symbol)
        return symbols

    def match_to_events(self, schema: EventSchema) -> List[PatternMatch]:
        """
        Match a quatrain schema against the knowledge graph.
        Returns ranked list of matches with scores.
        """
        matches = []

        # Query events by type and location
        candidates = self.kg.query_events(
            event_type=schema.event_type if schema.event_type != EventType.UNKNOWN else None,
            location=schema.location if schema.location != Region.UNKNOWN else None
        )

        for event in candidates:
            score = self._compute_match_score(schema, event)
            if score["composite"] > 0.1:
                # Check cycle membership
                cycle_ids = self.kg.find_cycles_in_sequence(
                    [schema.quatrain_id, event.event_id]
                )

                match = PatternMatch(
                    quatrain_id=schema.quatrain_id,
                    event_id=event.event_id,
                    event_name=event.name,
                    match_score=score["composite"],
                    matched_components=score,
                    cycle_membership=cycle_ids,
                    is_strong_match=score["composite"] > 0.7
                )
                matches.append(match)

        # Sort by score
        matches.sort(key=lambda m: m.match_score, reverse=True)
        return matches

    def _compute_match_score(self, schema: EventSchema, event: HistoricalEvent) -> Dict[str, float]:
        """Compute composite match score between schema and event."""
        entity_score = 0.0
        location_score = 0.0
        type_score = 0.0
        astro_score = 0.0

        # Type match
        if schema.event_type == event.event_type:
            type_score = 1.0
        elif schema.event_type == EventType.UNKNOWN:
            type_score = 0.3

        # Location match
        if schema.location == event.location:
            location_score = 1.0
        elif schema.location != Region.UNKNOWN:
            location_score = 0.3

        # Actor match
        if schema.primary_actor:
            for actor in event.actors:
                if schema.primary_actor.lower() in actor.lower():
                    entity_score = 1.0
                    break

        # Astrological match (bonus)
        if schema.planetary_config and event.astrology_notes:
            # Check if planetary config aligns with event's astrology notes
            astro_score = 0.2

        composite = (entity_score * 0.3 + location_score * 0.3 +
                     type_score * 0.3 + astro_score * 0.1)

        return {
            "entity_score": entity_score,
            "location_score": location_score,
            "type_score": type_score,
            "astro_score": astro_score,
            "composite": round(composite, 3)
        }

    def run_full_analysis(self, quatrains: List[Dict], astrology_configs: List[Dict]) -> List[PatternMatch]:
        """
        Run complete pattern analysis on all quatrains.
        Returns all matches with cycle membership and validation scores.
        """
        all_matches = []

        for i, (quatrain, astro) in enumerate(zip(quatrains, astrology_configs)):
            schema = self.extract_schema(quatrain, astro)
            matches = self.match_to_events(schema)

            if matches:
                all_matches.extend(matches)
                # Keep best match
                self.matches.append(matches[0])

            if i % 100 == 0:
                print(f"  Pattern analysis: {i}/{len(quatrains)}")

        return all_matches

# === CYCLE DEFINITIONS ===

STANDARD_CYCLES = [
    Cycle(
        cycle_id="rise-fall-empire",
        name="Rise and Fall of Empires",
        event_types=[EventType.WAR, EventType.REVOLUTION, EventType.ECONOMIC_STRESS],
        typical_duration_years=50
    ),
    Cycle(
        cycle_id="religious-conflict-cycle",
        name="Religious Conflict Cycle",
        event_types=[EventType.RELIGIOUS_SCHISM, EventType.WAR, EventType.REVOLUTION],
        typical_duration_years=30
    ),
    Cycle(
        cycle_id="plague-famine-war",
        name="Plague-Famine-War Triangle",
        event_types=[EventType.FAMINE, EventType.PLAGUE, EventType.WAR],
        typical_duration_years=20
    ),
    Cycle(
        cycle_id="political-assassination",
        name="Political Assassination Sequence",
        event_types=[EventType.ASSASSINATION, EventType.REVOLUTION, EventType.WAR],
        typical_duration_years=10
    ),
    # Natural Disaster Cycles
    Cycle(
        cycle_id="disaster-famine-unrest",
        name="Disaster-Famine-Unrest Chain",
        event_types=[EventType.EARTHQUAKE, EventType.FAMINE, EventType.REVOLUTION],
        typical_duration_years=15
    ),
    Cycle(
        cycle_id="solar-storm-infrastructure",
        name="Solar Storm Infrastructure Failure",
        event_types=[EventType.SOLAR_STORM, EventType.INFRASTRUCTURE, EventType.ECONOMIC_STRESS],
        typical_duration_years=8
    ),
    Cycle(
        cycle_id="asteroid-threat-cycle",
        name="Asteroid Threat Response Cycle",
        event_types=[EventType.ASTEROID, EventType.ECONOMIC_STRESS, EventType.POLITICAL],
        typical_duration_years=50
    ),
    # Comet / Celestial Omen Cycles
    Cycle(
        cycle_id="comet-omen-cycle",
        name="Comet / Celestial Omen Sequence",
        event_types=[EventType.COMET, EventType.ECONOMIC_STRESS, EventType.WAR],
        typical_duration_years=30
    ),
    # Wildfire / Fire Cycles
    Cycle(
        cycle_id="wildfire-plague-cycle",
        name="Wildfire-Plague-Famine Chain",
        event_types=[EventType.WILDFIRE, EventType.PLAGUE, EventType.FAMINE],
        typical_duration_years=20
    ),
]

# === API ===

def build_knowledge_graph(events_data: List[Dict]) -> TemporalKnowledgeGraph:
    """Build knowledge graph from historical events data."""
    kg = TemporalKnowledgeGraph()

    # Add standard cycles
    for cycle in STANDARD_CYCLES:
        kg.add_cycle(cycle)

    # Add events
    for edata in events_data:
        event = HistoricalEvent(
            event_id=edata["event_id"],
            name=edata["name"],
            event_type=EventType(edata.get("event_type", "unknown")),
            start_year=edata.get("start_year", 1500),
            end_year=edata.get("end_year"),
            location=Region(edata.get("location", "UNKNOWN")),
            actors=edata.get("actors", []),
            period_sources=edata.get("period_sources", []),
            related_events=edata.get("related_events", []),
            astrology_notes=edata.get("astrology_notes")
        )
        kg.add_event(event)

    return kg

def analyze_quatrains(quatrains: List[Dict], astrology_configs: List[Dict],
                     events_data: List[Dict]) -> Dict:
    """
    Main entry point: analyze all quatrains against historical patterns.
    Returns structured dossier with matches, cycles, and statistics.
    """
    print("Building knowledge graph...")
    kg = build_knowledge_graph(events_data)
    print(f"  {len(kg.events)} events, {len(kg.cycles)} cycles loaded")

    print("Initializing pattern engine...")
    engine = PatternEngine(kg)

    print("Running pattern analysis...")
    matches = engine.run_full_analysis(quatrains, astrology_configs)
    print(f"  Found {len(matches)} matches")

    # Statistics
    strong_matches = [m for m in matches if m.is_strong_match]
    cycle_matches = [m for m in matches if m.cycle_membership]

    stats = {
        "total_matches": len(matches),
        "strong_matches": len(strong_matches),
        "weak_matches": len(matches) - len(strong_matches),
        "cycle_membership_count": len(cycle_matches),
        "by_event_type": {},
        "by_region": {}
    }

    # Aggregate by type
    for match in matches:
        event = kg.events.get(match.event_id)
        if event:
            et = event.event_type.value
            stats["by_event_type"][et] = stats["by_event_type"].get(et, 0) + 1

    return {
        "knowledge_graph": kg.to_json(),
        "matches": [
            {
                "quatrain_id": m.quatrain_id,
                "event_id": m.event_id,
                "event_name": m.event_name,
                "score": m.match_score,
                "components": m.matched_components,
                "cycles": m.cycle_membership,
                "is_strong": m.is_strong_match
            }
            for m in matches[:50]  # Top 50 matches
        ],
        "statistics": stats
    }
