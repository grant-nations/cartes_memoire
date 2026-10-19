#!/usr/bin/env python3

from pathlib import Path


PAQUETS_DIR = Path(__file__).parent / "paquets"


for paquet in sorted(PAQUETS_DIR.iterdir()):
    if not paquet.is_file() or paquet.suffix.lower() != ".csv":
        continue

    renamed_paquet = paquet.with_suffix("")
    if renamed_paquet.exists():
        print(f"Skipped: {renamed_paquet.name} already exists")
        continue

    paquet.rename(renamed_paquet)
    print(f"Renamed: {paquet.name} -> {renamed_paquet.name}")
