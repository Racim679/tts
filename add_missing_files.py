#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter les fichiers manquants au metadata.json
"""

import json
from pathlib import Path

dataset_dir = Path("dataset_training")
wav_dir = dataset_dir / "wavs"
metadata_file = dataset_dir / "metadata.json"

# Charger les métadonnées existantes
with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Trouver tous les fichiers WAV
all_wavs = set(f.name for f in wav_dir.glob('*.wav'))
in_metadata = set(item['audio_file'].replace('wavs/', '') for item in metadata)
missing = sorted(all_wavs - in_metadata)

print(f"Fichiers manquants: {len(missing)}")
print(f"Fichiers: {missing}")

# Ajouter les fichiers manquants
for wav_file in missing:
    # Utiliser le nom de fichier comme transcription temporaire
    transcription = wav_file.replace('.wav', '')
    
    metadata.append({
        "audio_file": f"wavs/{wav_file}",
        "text": transcription,
        "speaker_id": "darija_speaker"
    })
    print(f"Ajoute: {wav_file}")

# Sauvegarder
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"\n{len(missing)} fichiers ajoutes")
print(f"Total fichiers dans metadata.json: {len(metadata)}")

