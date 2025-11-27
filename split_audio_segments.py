#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour segmenter les fichiers audio longs en segments de ~10 secondes
XTTS a une limite de ~10 secondes par fichier audio
"""

import sys
import os
import json
from pathlib import Path

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from pydub import AudioSegment
except ImportError:
    print("ERREUR: pydub n'est pas installe!")
    print("  Installez-le avec: pip install pydub")
    exit(1)

print("=" * 60)
print("Segmentation des fichiers audio longs (>10 secondes)")
print("Segments de ~10 secondes pour XTTS")
print("=" * 60)
print()

# Configuration
dataset_dir = Path("dataset_training")
wav_dir = dataset_dir / "wavs"
metadata_file = dataset_dir / "metadata.json"
MAX_DURATION_MS = 10000  # 10 secondes en millisecondes
SEGMENT_DURATION_MS = 10000  # Durée cible des segments (10 secondes)
OVERLAP_MS = 500  # Chevauchement de 500ms pour éviter de couper les mots

# Charger les métadonnées
if not metadata_file.exists():
    print(f"ERREUR: {metadata_file} n'existe pas!")
    exit(1)

with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"Metadata chargee: {len(metadata)} fichiers")
print()

# Traiter les fichiers
new_metadata = []
files_to_remove = []
segmented_count = 0
total_segments = 0

for i, item in enumerate(metadata, 1):
    audio_file = item.get("audio_file", "")
    text = item.get("text", "")
    speaker_id = item.get("speaker_id", "darija_speaker")
    
    audio_path = dataset_dir / audio_file
    
    if not audio_path.exists():
        print(f"[{i}/{len(metadata)}] ⚠️  Fichier non trouve: {audio_file}")
        # Garder quand même dans les métadonnées
        new_metadata.append(item)
        continue
    
    try:
        # Charger l'audio
        audio = AudioSegment.from_wav(str(audio_path))
        duration_ms = len(audio)
        duration_sec = duration_ms / 1000.0
        
        print(f"[{i}/{len(metadata)}] {audio_file}")
        print(f"  Duree: {duration_sec:.1f} secondes")
        
        # Si le fichier est <= 10 secondes, le garder tel quel
        if duration_ms <= MAX_DURATION_MS:
            print(f"  ✓ Fichier OK (<= 10s)")
            new_metadata.append(item)
            print()
            continue
        
        # Segmenter le fichier
        print(f"  → Segmentation en cours...")
        num_segments = (duration_ms + SEGMENT_DURATION_MS - OVERLAP_MS - 1) // (SEGMENT_DURATION_MS - OVERLAP_MS)
        print(f"  Nombre de segments: {num_segments}")
        
        # Créer les segments
        segments_created = []
        start_ms = 0
        segment_num = 0
        
        while start_ms < duration_ms:
            # Calculer la fin du segment
            end_ms = min(start_ms + SEGMENT_DURATION_MS, duration_ms)
            
            # Extraire le segment
            segment = audio[start_ms:end_ms]
            
            # Nom du fichier segment
            base_name = audio_path.stem
            segment_name = f"{base_name}_seg{segment_num:03d}.wav"
            segment_path = wav_dir / segment_name
            
            # Exporter le segment
            segment.export(str(segment_path), format="wav", parameters=["-ar", "48000"])
            
            # Ajouter à la métadonnée
            segment_item = {
                "audio_file": f"wavs/{segment_name}",
                "text": text,  # Même transcription pour tous les segments
                "speaker_id": speaker_id
            }
            new_metadata.append(segment_item)
            segments_created.append(segment_name)
            total_segments += 1
            segment_num += 1
            
            # Avancer pour le prochain segment (avec chevauchement)
            start_ms = end_ms - OVERLAP_MS
            
            # Éviter les segments trop courts à la fin
            if duration_ms - start_ms < SEGMENT_DURATION_MS * 0.3:  # Si moins de 30% de la durée cible
                break
        
        print(f"  ✓ {len(segments_created)} segments crees")
        for seg_name in segments_created[:3]:  # Afficher les 3 premiers
            print(f"    - {seg_name}")
        if len(segments_created) > 3:
            print(f"    ... et {len(segments_created) - 3} autres")
        
        # Marquer le fichier original pour suppression
        files_to_remove.append(audio_path)
        segmented_count += 1
        print()
        
    except Exception as e:
        print(f"  ✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        # En cas d'erreur, garder le fichier original
        new_metadata.append(item)
        print()

# Sauvegarder les nouvelles métadonnées
print("=" * 60)
print(f"Sauvegarde des nouvelles metadonnees...")
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(new_metadata, f, ensure_ascii=False, indent=2)

print(f"✓ {len(new_metadata)} fichiers dans le dataset (apres segmentation)")
print(f"✓ {segmented_count} fichiers segmentes")
print(f"✓ {total_segments} segments crees au total")
print()

# Supprimer les fichiers originaux segmentés
if files_to_remove:
    print(f"Suppression des fichiers originaux segmentes...")
    removed_count = 0
    for file_path in files_to_remove:
        try:
            file_path.unlink()
            removed_count += 1
        except Exception as e:
            print(f"  ⚠️  Impossible de supprimer {file_path.name}: {e}")
    print(f"✓ {removed_count} fichiers originaux supprimes")
    print()

print("=" * 60)
print("TERMINE!")
print("=" * 60)
print()
print("Prochaines etapes:")
print("  1. Verifiez les transcriptions dans metadata.json")
print("  2. Les fichiers longs ont ete segmentes en segments de ~10 secondes")
print("  3. Lancez l'entrainement avec: python train_xtts_simple.py")
print()

