#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter des fichiers M4A au dataset d'entraînement
Convertit les M4A en WAV 48kHz (qualité maximale) et les ajoute au dataset
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
    print("  Note: Vous aurez aussi besoin de ffmpeg pour convertir M4A")
    exit(1)

print("=" * 60)
print("Ajout de fichiers M4A au dataset d'entrainement")
print("Conversion en WAV 48kHz (qualite maximale)")
print("=" * 60)
print()

# Dossiers
dataset_dir = Path("dataset_training")
wav_dir = dataset_dir / "wavs"
wav_dir.mkdir(parents=True, exist_ok=True)

# Chercher les fichiers M4A dans plusieurs emplacements possibles
m4a_files = []

# 1. Dossier spécifique dans dataset_training (priorité)
specific_dir = dataset_dir / "drive-download-20251112T172017Z-1-001"
if specific_dir.exists() and specific_dir.is_dir():
    m4a_files = list(specific_dir.glob("*.m4a"))
    if m4a_files:
        print(f"Recherche dans le dossier '{specific_dir}'...")

# 2. Dossier audio/ (si pas trouvé)
if not m4a_files:
    audio_dir = Path("audio")
    if audio_dir.exists() and audio_dir.is_dir():
        m4a_files = list(audio_dir.glob("*.m4a"))
        if m4a_files:
            print(f"Recherche dans le dossier 'audio/'...")

# 3. Répertoire courant (si pas trouvé)
if not m4a_files:
    m4a_files = list(Path(".").glob("*.m4a"))
    if m4a_files:
        print(f"Recherche dans le repertoire courant...")

if not m4a_files:
    print("ERREUR: Aucun fichier M4A trouve!")
    print("  Placez vos fichiers M4A dans:")
    print("    - Le dossier 'audio/' (recommandé)")
    print("    - Ou le repertoire courant: " + str(Path(".").absolute()))
    exit(1)

print(f"Fichiers M4A trouves: {len(m4a_files)}")
for f in m4a_files:
    size_mb = f.stat().st_size / (1024 * 1024)
    print(f"  - {f.name} ({size_mb:.2f} MB)")
print()

# Charger les métadonnées existantes
metadata_file = dataset_dir / "metadata.json"
if metadata_file.exists():
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    print(f"Metadata existante chargee: {len(metadata)} fichiers")
    
    # Trouver le prochain numéro de fichier
    existing_numbers = []
    for item in metadata:
        audio_file = item.get("audio_file", "")
        if "audio_" in audio_file:
            try:
                num = int(audio_file.split("audio_")[1].split(".")[0].split("_")[0])
                existing_numbers.append(num)
            except:
                pass
    
    next_number = max(existing_numbers) + 1 if existing_numbers else 1
    print(f"Prochain numero de fichier: {next_number:03d}")
else:
    metadata = []
    next_number = 1
    print("Nouveau dataset - creation du fichier metadata.json")

print()

# Vérifier si un fichier de transcriptions existe
transcriptions_file = Path("transcriptions.json")
transcriptions = {}
if transcriptions_file.exists():
    with open(transcriptions_file, 'r', encoding='utf-8') as f:
        transcriptions = json.load(f)
    print(f"Transcriptions chargees: {len(transcriptions)} entrees")
    print()

# Traitement des fichiers M4A
errors = []
processed_count = 0

for i, m4a_file in enumerate(m4a_files, 1):
    print(f"[{i}/{len(m4a_files)}] Traitement: {m4a_file.name}")
    
    try:
        # Charger l'audio M4A
        print(f"  Chargement du fichier M4A...")
        audio = AudioSegment.from_file(str(m4a_file), format="m4a")
        
        # Vérifier la durée
        duration = len(audio) / 1000.0
        print(f"  Duree: {duration:.1f} secondes")
        
        # Convertir en mono si nécessaire
        if audio.channels > 1:
            print(f"  Conversion: Stereo -> Mono")
            audio = audio.set_channels(1)
        
        # Convertir en 48kHz (qualité maximale pour XTTS)
        if audio.frame_rate != 48000:
            print(f"  Resampling: {audio.frame_rate} Hz -> 48000 Hz")
            audio = audio.set_frame_rate(48000)
        
        # Normaliser le volume
        print(f"  Normalisation du volume...")
        audio = audio.normalize()
        
        # Nom du fichier de sortie
        output_name = f"audio_{next_number:03d}.wav"
        output_path = wav_dir / output_name
        
        # Exporter en WAV 48kHz
        print(f"  Export en WAV 48kHz...")
        audio.export(str(output_path), format="wav", parameters=["-ar", "48000"])
        print(f"  ✓ Fichier cree: {output_name}")
        
        # Vérifier la taille du fichier
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Taille: {file_size_mb:.2f} MB")
        
        # Récupérer la transcription
        transcription = transcriptions.get(m4a_file.name, "").strip()
        
        if not transcription:
            # Utiliser le nom de fichier comme transcription par défaut (sans extension)
            transcription = m4a_file.stem
            print(f"  ⚠️  Transcription non trouvee - utilisation du nom de fichier: {transcription}")
            print(f"  NOTE: Vous pourrez modifier les transcriptions dans metadata.json apres la conversion")
        else:
            print(f"  Transcription trouvee: {transcription[:50]}..." if len(transcription) > 50 else f"  Transcription: {transcription}")
        
        # Ajouter à la métadonnée
        metadata.append({
            "audio_file": f"wavs/{output_name}",
            "text": transcription,
            "speaker_id": "darija_speaker"
        })
        
        next_number += 1
        processed_count += 1
        print()
        
    except Exception as e:
        print(f"  ✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        errors.append(m4a_file.name)
        print()

# Sauvegarder les métadonnées
print("=" * 60)
if processed_count > 0:
    print(f"Sauvegarde des metadonnees...")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ {processed_count} fichier(s) ajoute(s) au dataset")
    print(f"  Total fichiers dans le dataset: {len(metadata)}")
else:
    print("Aucun fichier n'a ete ajoute.")

if errors:
    print()
    print("⚠️  ERREURS lors du traitement:")
    for error_file in errors:
        print(f"  - {error_file}")

print()
print("=" * 60)
print("TERMINE!")
print("=" * 60)
print()
print("Prochaines etapes:")
print("  1. Verifiez les transcriptions dans metadata.json")
print("  2. Si vous avez plus de fichiers M4A, relancez ce script")
print("  3. Lancez l'entrainement avec: python train_xtts_simple.py")
print()

