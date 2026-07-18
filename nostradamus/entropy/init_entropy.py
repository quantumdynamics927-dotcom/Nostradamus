#!/usr/bin/env python3
"""
Initialize QRNG entropy pool from existing QSG job files.
Copies job JSONs and prepares EntropyService for use.
"""

import json
import os
from pathlib import Path

# Source QRNG jobs - correct path is near-fully-entropy
QRNG_JOBS = [
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kkrti4lglc73fvjdn0-info.json",
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kkrti4lglc73fvjdn0-result.json",
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kks0a4lglc73fvjdqg-info.json",
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kks0a4lglc73fvjdqg-result.json",
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kks2oe7usc73f4uhl0-info.json",
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kks2oe7usc73f4uhl0-result.json",
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kks58e7usc73f4uhng-info.json",
    r"D:\Somnath-PROJECT\near-fully-entropy\job-d7kks58e7usc73f4uhng-result.json",
]

# Teleportation calibration jobs
TELEPORT_JOBS = [
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8qp24lglc7380atlg-info.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8qp24lglc7380atlg-result.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8qri4lglc7380atr0-info.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8qri4lglc7380atr0-result.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8qtokj84c73ceo7tg-info.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8qtokj84c73ceo7tg-result.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8r1i8ui0s73b648q0-info.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8r1i8ui0s73b648q0-result.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8r028ui0s73b648ng-info.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8r028ui0s73b648ng-result.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8r38kj84c73ceo860-info.json",
    r"D:\Somnath-PROJECT\teleport_circuit_4-\job-d7l8r38kj84c73ceo860-result.json",
]

TARGET_QRNG_DIR = r"D:\Nostradamus\nostradamus\data\entropy_sources\qrng"
TARGET_TELEPORT_DIR = r"D:\Nostradamus\nostradamus\data\entropy_sources\teleport"

def copy_files(source_files, target_dir):
    """Copy source files to target directory."""
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    copied = []
    for src in source_files:
        src_path = Path(src)
        if src_path.exists():
            dest = Path(target_dir) / src_path.name
            with open(src_path, 'rb') as f_in:
                content = f_in.read()
            with open(dest, 'wb') as f_out:
                f_out.write(content)
            copied.append(str(dest))
            print(f"  Copied: {src_path.name}")
        else:
            print(f"  Missing: {src}")
    return copied

def main():
    print("=" * 60)
    print("QRNG & TELEPORTATION INITIALIZATION")
    print("=" * 60)

    # Copy QRNG jobs
    print("\n[1/2] Copying QRNG jobs...")
    qrng_copied = copy_files(QRNG_JOBS, TARGET_QRNG_DIR)
    print(f"  Total QRNG files: {len(qrng_copied)}")

    # Copy teleportation jobs
    print("\n[2/2] Copying Teleportation jobs...")
    tele_copied = copy_files(TELEPORT_JOBS, TARGET_TELEPORT_DIR)
    print(f"  Total Teleportation files: {len(tele_copied)}")

    # Load and process with EntropyService
    print("\n[3/3] Initializing EntropyService...")
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from entropy.qrng_service import (
        EntropyService, pair_info_and_result, EntropyConfig, EntropyMode
    )

    # Load QRNG
    qrng_paths = [Path(p) for p in qrng_copied]
    qrng_pairs = pair_info_and_result(qrng_paths)
    print(f"  QRNG pairs: {len(qrng_pairs)}")

    if qrng_pairs:
        service = EntropyService.from_qrng_jobs(qrng_pairs)
        print(f"  Entropy pool: {service._pool.remaining} bits")
        print(f"  Source: {service._pool._qrng_source}")
        print(f"  Backend: {service._pool._backend}")

        # Save service state for later use
        import pickle
        service_file = Path(TARGET_QRNG_DIR) / "entropy_service.pkl"
        with open(service_file, 'wb') as f:
            pickle.dump(service, f)
        print(f"  Saved service to: {service_file}")
    else:
        print("  No valid QRNG pairs found")

    # Load and process teleportation
    print("\n[4/4] Computing Teleportation Fidelity...")
    tele_paths = [Path(p) for p in tele_copied]
    tele_pairs = pair_info_and_result(tele_paths)
    print(f"  Teleportation pairs: {len(tele_pairs)}")

    if tele_pairs:
        from entropy.qrng_service import TeleportationCalibrator
        calibrator = TeleportationCalibrator(tele_pairs)
        summary = calibrator.summary()
        print(f"  Mean fidelity: {summary['mean_fidelity']:.4f}")
        print(f"  Health: {summary['health']}")

        # Save calibration report
        calib_file = Path(TARGET_TELEPORT_DIR) / "calibration_report.json"
        with open(calib_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  Saved calibration to: {calib_file}")

    print("\n" + "=" * 60)
    print("INITIALIZATION COMPLETE")
    print("=" * 60)
    print(f"""
To use in analysis:
    import sys
    sys.path.insert(0, 'nostradamus')
    from entropy.qrng_service import EntropyService, EntropyConfig, EntropyMode

    # Configure mode
    EntropyConfig.mode = EntropyMode.QRNG

    # Load service
    import pickle
    with open('{TARGET_QRNG_DIR}/entropy_service.pkl', 'rb') as f:
        service = pickle.load(f)

    # Use for Monte Carlo
    bits, source = service.get_bits(256)
    value, source = service.get_int(0, 100)
""")

if __name__ == "__main__":
    main()
