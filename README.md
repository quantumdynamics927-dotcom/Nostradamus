# Nostradamus TKG Forecaster

**Temporal Knowledge Graph Forecasting with Quantum-Assisted Hypothesis Search**

A scientific framework for analyzing Nostradamus quatrains through 8 expert domains, using Chain-of-History reasoning and quantum-assisted search to generate hypotheses about future events.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NOSTRADAMUS ENGINE                       │
├─────────────┬─────────────┬─────────────┬────────────────┤
│  Linguistic │  Astrology  │   History   │   Theology     │
├─────────────┼─────────────┼─────────────┼────────────────┤
│ Numerology  │ Cryptography│  Pattern    │    QRNG       │
│             │             │   Engine    │  Entropy      │
└─────────────┴─────────────┴─────────────┴────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              TKG FORECASTER                                │
│  Temporal Knowledge Graph + Chain-of-History Reasoning     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│           QUANTUM HYPOTHESIS SEARCH                        │
│  Grover-style amplitude amplification over hypothesis      │
│  space: interpretations × events × cycles × numerology   │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

### Pattern Engine (`nostradamus/analysis/pattern_engine.py`)
- `EventSchema` - structured event (who/what/where/when)
- `TemporalKnowledgeGraph` - historical events + cycles
- `PatternEngine` - matches quatrains to historical patterns

### TKG Forecaster (`nostradamus/analysis/tkg_forecaster.py`)
- `ForecastHypothesis` - scenario output with uncertainty
- Chain-of-History reasoning: "Given cycle X, what comes next?"
- Horizon estimation with quantile-based uncertainty bands

### Quantum Hypothesis Search (`nostradamus/analysis/quantum_hypothesis_search.py`)
- `HypothesisSpace` - encodes combinatorial space
- `QuantumSearchEngine` - Grover-style search
- Classical vs quantum comparison capability

### Entropy System (`nostradamus/entropy/`)
- QRNG service using IBM Quantum hardware
- Provenance logging for all entropy usage
- Fallback to PRNG when quantum unavailable

## Scientific Framing

**This is NOT prophecy.** Every output is labeled `status: hypothesis` with:

```json
{
  "quatrain_id": "C10-Q99",
  "status": "hypothesis",
  "cycle_match": "rise-fall-empire",
  "event_type_predicted": "war",
  "horizon_years": "10-25",
  "horizon_uncertainty": {"median": 40, "q25": 25, "q75": 70},
  "confidence": "high",
  "pattern_strength": 0.9,
  "p_value_approximate": 0.05,
  "quantum_assisted": true
}
```

## Backtest Results

The cycles encode real historical patterns (validated against 87 period-sourced events):

| Cycle | Evidence |
|-------|----------|
| Plague-Famine-War | Plague 1580 → Famine 1590s ✓ |
| Rise-Fall-Empire | French Wars 1562-1598 → Fronde 1648 ✓ |
| Religious-Conflict | Reformation → Thirty Years War 1618 ✓ |

## Quick Start

```bash
# Run forecast analysis on high-crypto quatrains
python run_forecast_analysis.py

# Run quantum hypothesis search experiment
python run_quantum_experiment.py

# Backtest the forecaster against history
python run_backtest.py
```

## Data

- **951 quatrains** from Les Prophéties (bilingual)
- **87 historical events** from period sources (Froissart, de Thou, L'Estoile)
- **4 standard cycles**: plague-famine-war, religious-conflict, rise-fall-empire, political-assassination

## Period Source Compliance

All historical events cite primary sources:
- Jacques de Thou, *Historia Sui Temporis* (1609)
- Pierre de L'Estoile, *Mémoires-Journaux* (1574-1611)
- Jean Froissart, *Chroniques* (1480s)

See `references/PERIOD_SOURCES_INDEX.md` for full index.

## Limitations

- KB has only 87 events - insufficient for rigorous statistical validation
- Quantum advantage requires hypothesis spaces >10K states
- Cycle timing is uncertain (horizon bands, not dates)
- Monte Carlo shows no statistically significant past-match predictions (p~0.35)

## Scientific Use

This framework is designed for:

1. **Pattern discovery** - find recurring cycles in historical data
2. **Hypothesis generation** - generate plausible future scenarios
3. **Uncertainty quantification** - explicit confidence bands, not prophecy
4. **Quantum computing research** - test quantum search on real combinatorial problems

## License

Research use only. Nostradamus quatrains are public domain. Historical interpretations are speculative.
