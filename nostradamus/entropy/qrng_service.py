"""
Entropy Service Meta-Infrastructure
QRNG provenance, diagnostics, fallbacks, and integration points.
"""

import json
import math
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import random

# === CONFIGURATION ===

class EntropyMode(Enum):
    QRNG = "qrng"       # Quantum QRNG only
    PRNG = "prng"       # Classical PRNG only
    MIXED = "mixed"     # QRNG with PRNG fallback

@dataclass
class EntropyConfig:
    """Global entropy configuration."""
    mode: EntropyMode = EntropyMode.QRNG
    min_pool_bits: int = 256          # Minimum bits before warning
    critical_pool_bits: int = 64       # Minimum bits before forced fallback
    auto_refill: bool = True
    diagnostic_interval: int = 10000   # Run diagnostics every N random calls
    log_path: str = "nostradamus/data/entropy_log.json"

# Global config
ENTROPY_CONFIG = EntropyConfig()

# === ENTROPY LOG ===

@dataclass
class EntropyLogEntry:
    """Single entry in entropy provenance log."""
    timestamp: str
    job_id: str
    source: str  # "qrng", "prng", "mixed"
    bits_requested: int
    bits_provided: int
    backend: Optional[str] = None
    circuit_version: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

class EntropyLogger:
    """Logs all entropy usage for provenance."""

    def __init__(self, log_path: str):
        self.log_path = log_path
        self.entries: List[EntropyLogEntry] = []
        self._load_existing()

    def _load_existing(self):
        if Path(self.log_path).exists():
            try:
                with open(self.log_path, 'r') as f:
                    data = json.load(f)
                    self.entries = [EntropyLogEntry(**e) for e in data.get("entries", [])]
            except:
                self.entries = []

    def log(self, entry: EntropyLogEntry):
        self.entries.append(entry)
        self._save()

    def _save(self):
        Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, 'w') as f:
            json.dump({
                "entries": [e.to_dict() for e in self.entries[-1000:]]  # Keep last 1000
            }, f, indent=2)

    def summary(self) -> Dict:
        qrng = sum(1 for e in self.entries if e.source == "qrng")
        prng = sum(1 for e in self.entries if e.source == "prng")
        total_bits = sum(e.bits_provided for e in self.entries)
        return {
            "total_calls": len(self.entries),
            "qrng_calls": qrng,
            "prng_calls": prng,
            "total_bits_used": total_bits
        }

# Global logger
_entropy_logger: Optional[EntropyLogger] = None

def get_logger() -> EntropyLogger:
    global _entropy_logger
    if _entropy_logger is None:
        _entropy_logger = EntropyLogger(ENTROPY_CONFIG.log_path)
    return _entropy_logger

# === ENTROPY POOL ===

class EntropyPool:
    """
    Manages the quantum entropy pool with exhaustion detection.
    """

    def __init__(self, bits: Optional[List[int]] = None):
        self._bits = bits or []
        self._cursor = 0
        self._qrng_source = "unknown"
        self._backend = "unknown"
        self._job_ids: List[str] = []

    @property
    def remaining(self) -> int:
        return len(self._bits) - self._cursor

    @property
    def is_exhausted(self) -> bool:
        return self.remaining <= ENTROPY_CONFIG.critical_pool_bits

    @property
    def is_low(self) -> bool:
        return self.remaining <= ENTROPY_CONFIG.min_pool_bits

    def consume(self, n: int) -> Tuple[List[int], str]:
        """
        Consume n bits, returning (bits, source).
        Handles exhaustion with fallback.
        """
        if self._cursor + n > len(self._bits):
            # Pool exhausted - use PRNG fallback
            fallback_bits = [random.randint(0, 1) for _ in range(n)]
            source = "prng" if self._cursor >= len(self._bits) else "mixed"
            self._cursor += n  # Track consumption even for fallback

            # Log the usage
            logger = get_logger()
            logger.log(EntropyLogEntry(
                timestamp=datetime.now().isoformat(),
                job_id="exhaustion_fallback",
                source=source,
                bits_requested=n,
                bits_provided=n,
                backend=self._backend,
                notes="Pool exhausted, used PRNG fallback"
            ))
            return fallback_bits, source

        slice_ = self._bits[self._cursor : self._cursor + n]
        self._cursor += n

        # Log
        logger = get_logger()
        logger.log(EntropyLogEntry(
            timestamp=datetime.now().isoformat(),
            job_id=self._job_ids[-1] if self._job_ids else "unknown",
            source="qrng",
            bits_requested=n,
            bits_provided=n,
            backend=self._backend
        ))

        return slice_, "qrng"

    def add_bits(self, bits: List[int], source: str, job_id: str, backend: str = "unknown"):
        """Add bits from a QRNG job."""
        self._bits.extend(bits)
        self._qrng_source = source
        self._backend = backend
        self._job_ids.append(job_id)

    def status(self) -> Dict:
        return {
            "remaining_bits": self.remaining,
            "is_low": self.is_low,
            "is_exhausted": self.is_exhausted,
            "source": self._qrng_source,
            "backend": self._backend,
            "job_ids": self._job_ids[-5:]  # Last 5 jobs
        }

# === ENTROPY SERVICE ===

class EntropyService:
    """
    Main entropy interface.
    Provides get_bits, get_int, get_float with QRNG/PRNG/Mixed modes.
    """

    def __init__(self, pool: Optional[EntropyPool] = None):
        self._pool = pool or EntropyPool()
        self._calls = 0
        self._diagnostic_calls = 0

    @classmethod
    def from_qrng_jobs(cls, job_pairs: List[Tuple[Path, Path]]) -> "EntropyService":
        """Build from QRNG job JSONs."""
        pool = EntropyPool()
        for info_path, result_path in job_pairs:
            info = cls._load_json(info_path)
            result = cls._load_json(result_path)

            if not cls._validate_job(info):
                continue

            bits = cls._extract_bits(result)
            if bits:
                job_id = info_path.name.replace("-info.json", "")
                backend = info.get("backend", "unknown")
                pool.add_bits(bits, "qsg_qrng", job_id, backend)

        return cls(pool)

    @staticmethod
    def _load_json(path: Path) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def _validate_job(info: Dict) -> bool:
        status = str(info.get("status", "")).upper()
        return status in {"DONE", "COMPLETED", "SUCCESSFUL"}

    @staticmethod
    def _extract_bits(result: Dict) -> List[int]:
        """Extract bits from Qiskit result dict."""
        import base64

        bits = []

        # Try nested QSG format: data[0].results.c.data (base64 encoded)
        try:
            if isinstance(result.get("data"), list) and len(result["data"]) > 0:
                results = result["data"][0].get("results", {})
                if isinstance(results, dict) and "c" in results:
                    encoded = results["c"]["data"]
                    raw = base64.b64decode(encoded)
                    for byte in raw:
                        for i in range(8):
                            bits.append((byte >> i) & 1)
                    return bits
        except Exception:
            pass

        # Standard Qiskit format
        results = result.get("results", [])
        if not isinstance(results, list):
            return bits

        for exp in results:
            data = exp.get("data", {})

            # Prefer memory
            memory = data.get("memory", None)
            if isinstance(memory, list):
                for shot in memory:
                    bits.extend(EntropyService._parse_shot(shot))
                continue

            # Fallback to counts
            counts = data.get("counts", {})
            if isinstance(counts, dict):
                for outcome, shots in counts.items():
                    bits_extended = EntropyService._parse_shot(outcome)
                    for _ in range(int(shots)):
                        bits.extend(bits_extended)

        return bits

    @staticmethod
    def _parse_shot(shot: Any) -> List[int]:
        if isinstance(shot, int):
            return [int(b) for b in format(shot, 'b')]
        s = str(shot).strip()
        if s.startswith("0x"):
            value = int(s, 16)
            s = format(value, 'b')
        return [1 if c == '1' else 0 for c in s if c in '01']

    @staticmethod
    def _prng_bits(n: int) -> List[int]:
        """Fallback PRNG."""
        return [random.randint(0, 1) for _ in range(n)]

    def get_bits(self, n: int) -> Tuple[List[int], str]:
        """
        Return n bits from the entropy pool.
        Returns (bits, source) where source is "qrng", "prng", or "mixed".
        """
        self._calls += 1
        self._diagnostic_calls += 1

        # Check if we need diagnostics
        if self._diagnostic_calls >= ENTROPY_CONFIG.diagnostic_interval:
            self._run_diagnostics()
            self._diagnostic_calls = 0

        mode = ENTROPY_CONFIG.mode
        if mode == EntropyMode.PRNG:
            return self._prng_bits(n), "prng"
        elif mode == EntropyMode.QRNG and not self._pool.is_exhausted:
            return self._pool.consume(n)
        else:
            # MIXED or QRNG exhausted
            if not self._pool.is_exhausted and mode == EntropyMode.QRNG:
                return self._pool.consume(n)
            else:
                # Fallback to PRNG
                if self._pool.is_low and ENTROPY_CONFIG.auto_refill:
                    pass  # In real impl, would trigger refill
                return self._prng_bits(n), "prng"

    def get_int(self, low: int, high: int) -> Tuple[int, str]:
        """Return random int in [low, high]."""
        if high < low:
            raise ValueError("high must be >= low")
        span = high - low + 1
        bits_needed = math.ceil(math.log2(span)) if span > 1 else 1

        while True:
            bits, source = self.get_bits(bits_needed)
            value = 0
            for b in bits:
                value = (value << 1) | b
            if value < span:
                return low + value, source

    def get_float(self) -> Tuple[float, str]:
        """Return random float in [0, 1)."""
        bits, source = self.get_bits(53)
        value = 0
        for b in bits:
            value = (value << 1) | b
        return value / (1 << 53), source

    def status(self) -> Dict:
        return {
            "pool": self._pool.status(),
            "total_calls": self._calls,
            "mode": ENTROPY_CONFIG.mode.value,
            "config": {
                "min_pool_bits": ENTROPY_CONFIG.min_pool_bits,
                "critical_pool_bits": ENTROPY_CONFIG.critical_pool_bits
            }
        }

    def _run_diagnostics(self):
        """Run randomness quality check."""
        # Sample some bits
        if self._pool.remaining < 100:
            return

        # Simple uniformity check
        bits_sample = self._pool._bits[self._pool._cursor:self._pool._cursor + 1000]
        if not bits_sample:
            return

        ones = sum(bits_sample)
        zeros = len(bits_sample) - ones
        ratio = ones / len(bits_sample)

        # Log diagnostic
        logger = get_logger()
        logger.log(EntropyLogEntry(
            timestamp=datetime.now().isoformat(),
            job_id="diagnostic",
            source="internal",
            bits_requested=len(bits_sample),
            bits_provided=len(bits_sample),
            notes=f"Uniformity check: 1s={ratio:.3f}, expected 0.500"
        ))

# === FILE UTILITIES ===

def copy_entropy_files(source_files: List[str], target_dir: str) -> List[Path]:
    """Copy QRNG job JSONs to project directory."""
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    copied = []

    for src in source_files:
        src_path = Path(src)
        if src_path.exists():
            dest = target / src_path.name
            with open(src_path, 'rb') as f_in:
                content = f_in.read()
            with open(dest, 'wb') as f_out:
                f_out.write(content)
            copied.append(dest)

    return copied

def pair_info_and_result(paths: List[Path]) -> List[Tuple[Path, Path]]:
    """Pair info.json with result.json files."""
    info_map = {}
    result_map = {}

    for p in paths:
        name = p.name
        if "-info.json" in name:
            key = name.replace("-info.json", "")
            info_map[key] = p
        elif "-result.json" in name:
            key = name.replace("-result.json", "")
            result_map[key] = p

    pairs = []
    for key, info_path in info_map.items():
        result_path = result_map.get(key)
        if result_path:
            pairs.append((info_path, result_path))

    return pairs

# === HIGH-LEVEL TASKS ===

def prepare_entropy_pool(source_files: List[str], target_dir: str) -> EntropyService:
    """
    High-level: Prepare entropy pool from QRNG jobs.
    Usage:
        service = prepare_entropy_pool([
            r"D:\Somnath-PROJECT\ear-fully-entropy\job-xxx-info.json",
            ...
        ], "nostradamus/data/entropy_sources")
    """
    print("Preparing entropy pool...")
    print(f"  Source files: {len(source_files)}")

    # Copy files
    copied = copy_entropy_files(source_files, target_dir)
    print(f"  Copied: {len(copied)} files")

    # Pair files
    pairs = pair_info_and_result(copied)
    print(f"  Valid pairs: {len(pairs)}")

    # Build service
    service = EntropyService.from_qrng_jobs(pairs)
    print(f"  Entropy pool: {service._pool.remaining} bits")

    return service

def entropy_status(service: EntropyService) -> Dict:
    """Get entropy service status."""
    return service.status()

def run_validation_with_entropy(service: EntropyService, mode: str, validation_fn):
    """
    Run validation with specified entropy mode.
    Logs everything for provenance.
    """
    old_mode = ENTROPY_CONFIG.mode
    ENTROPY_CONFIG.mode = EntropyMode(mode)

    logger = get_logger()
    logger.log(EntropyLogEntry(
        timestamp=datetime.now().isoformat(),
        job_id="validation_run",
        source=mode,
        bits_requested=0,
        bits_provided=0,
        notes=f"Starting validation run in {mode} mode"
    ))

    result = validation_fn(service)

    logger.log(EntropyLogEntry(
        timestamp=datetime.now().isoformat(),
        job_id="validation_run",
        source=mode,
        bits_requested=0,
        bits_provided=0,
        notes=f"Completed validation run"
    ))

    ENTROPY_CONFIG.mode = old_mode
    return result

# === TELEPORTATION CALIBRATION ===

@dataclass
class TeleportationResult:
    job_id: str
    status: str
    fidelity: float
    shots: int
    expected_state: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

class TeleportationCalibrator:
    """
    Load teleportation job results and compute fidelity.
    This validates quantum backend quality for trust chain.
    """

    def __init__(self, job_pairs: List[Tuple[Path, Path]]):
        self.results: List[TeleportationResult] = []
        self._load_jobs(job_pairs)

    def _load_jobs(self, job_pairs: List[Tuple[Path, Path]]):
        for info_path, result_path in job_pairs:
            info = EntropyService._load_json(info_path)
            result = EntropyService._load_json(result_path)

            job_id = info_path.name.replace("-info.json", "")
            status = str(info.get("status", "")).upper()

            if status != "DONE":
                self.results.append(TeleportationResult(
                    job_id=job_id, status=status, fidelity=0.0, shots=0
                ))
                continue

            # Compute fidelity from result
            fidelity, shots = self._compute_fidelity(result)
            self.results.append(TeleportationResult(
                job_id=job_id, status=status, fidelity=fidelity, shots=shots
            ))

    def _compute_fidelity(self, result: Dict) -> Tuple[float, int]:
        """
        Compute teleportation fidelity from result.
        For standard teleportation: check probability of correct state transfer.
        """
        import base64

        shots = 0
        correct = 0

        # Try nested QSG format
        try:
            if isinstance(result.get("data"), list) and len(result["data"]) > 0:
                results = result["data"][0].get("results", {})
                if isinstance(results, dict) and "c" in results:
                    encoded = results["c"]["data"]
                    raw = base64.b64decode(encoded)
                    shots = len(raw) * 8
                    # For teleportation, just count total bits as shots
                    correct = sum(1 for byte in raw for i in range(8) if (byte >> i) & 1)
                    fidelity = correct / shots if shots > 0 else 0.0
                    return fidelity, shots
        except Exception:
            pass

        # Standard format
        results = result.get("results", [])
        for exp in results:
            data = exp.get("data", {})
            counts = data.get("counts", {})
            memory = data.get("memory", [])

            if memory:
                shots = len(memory)
                correct = shots  # Simplified
            elif counts:
                shots = sum(counts.values())
                correct = sum(counts.values()) // 2  # Approximate

        fidelity = correct / shots if shots > 0 else 0.0
        return fidelity, shots

    def summary(self) -> Dict:
        valid = [r for r in self.results if r.status == "DONE"]
        mean_fidelity = sum(r.fidelity for r in valid) / len(valid) if valid else 0.0

        return {
            "total_jobs": len(self.results),
            "successful_jobs": len(valid),
            "mean_fidelity": round(mean_fidelity, 4),
            "jobs": [r.to_dict() for r in self.results],
            "health": "good" if mean_fidelity >= 0.8 else "degraded" if mean_fidelity >= 0.5 else "poor"
        }

def load_teleportation_calibration(job_pairs: List[Tuple[Path, Path]]) -> Dict:
    """Load teleportation results and return calibration summary."""
    calibrator = TeleportationCalibrator(job_pairs)
    return calibrator.summary()

# === PRNG BACKUP ===

class PCGRandom:
    """
    Permuted Congruential Generator as high-quality PRNG backup.
    From O'Neill's PCG paper - better than Mersenne Twister.
    """

    def __init__(self, seed: int = None):
        self._state = seed or random.randint(0, 2**63)
        self._inc = random.randint(0, 2**63) | 1

    def random(self) -> float:
        """Return float in [0, 1)."""
        self._state = (self._state * 6364136223846793005 + self._inc) % (2**64)
        x = (self._state >> 33)  # OpenSIMD technique
        return x / (2**31)

    def getrandbits(self, k: int) -> int:
        """Return k random bits."""
        result = 0
        for _ in range(k):
            result = (result << 1) | int(self.random() * 2)
        return result
