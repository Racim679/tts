#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour préparer les données d'entraînement pour XTTS-v2
avec un fichier de transcriptions
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
print("Preparation des donnees d'entrainement XTTS-v2")
print("=" * 60)
print()

# Créer le dossier pour les données d'entraînement
dataset_dir = Path("dataset_training")
dataset_dir.mkdir(exist_ok=True)

wav_dir = dataset_dir / "wavs"
wav_dir.mkdir(exist_ok=True)

print(f"Dossier dataset: {dataset_dir.absolute()}")
print()

# Chercher tous les fichiers WAV dans le dossier audio/ ou le répertoire courant
audio_dir = Path("audio")
if audio_dir.exists() and audio_dir.is_dir():
    wav_files = list(audio_dir.glob("*.wav"))
    print(f"Recherche dans le dossier 'audio/'...")
else:
    wav_files = []

# Si pas trouvé dans audio/, chercher dans le répertoire courant
if not wav_files:
    wav_files = list(Path(".").glob("*.wav"))
    print(f"Recherche dans le repertoire courant...")

# Exclure les fichiers de référence et de sortie
wav_files = [f for f in wav_files if f.name not in ["reference.wav", "output_darija.wav", "output_optimized.wav"]]

if not wav_files:
    print("ERREUR: Aucun fichier WAV trouve!")
    print("  Placez vos fichiers WAV dans:")
    print("    - Le dossier 'audio/' (recommandé)")
    print("    - Ou le repertoire courant: " + str(Path(".").absolute()))
    exit(1)

print(f"Fichiers WAV trouves: {len(wav_files)}")
print()

# Vérifier si un fichier de transcriptions existe
transcriptions_file = Path("transcriptions.json")
transcriptions = {}

if transcriptions_file.exists():
    print(f"Chargement des transcriptions depuis: {transcriptions_file}")
    try:
        with open(transcriptions_file, 'r', encoding='utf-8') as f:
            transcriptions = json.load(f)
        print(f"  {len(transcriptions)} transcriptions chargees")
        print()
    except Exception as e:
        print(f"  ERREUR lors du chargement: {e}")
        print("  Continuons sans transcriptions...")
        print()
        transcriptions = {}
else:
    print("Fichier de transcriptions non trouve: transcriptions.json")
    print("  Creation d'un fichier template...")
    print()
    
    # Créer un template
    template = {}
    for wav_file in wav_files:
        template[wav_file.name] = ""
    
    with open(transcriptions_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"  Fichier cree: {transcriptions_file}")
    print()
    print("=" * 60)
    print("INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. Ouvrez le fichier 'transcriptions.json'")
    print("2. Ajoutez la transcription (en Darija) pour chaque fichier audio")
    print("3. La transcription doit etre EXACTEMENT ce qui est dit dans l'audio")
    print("4. Relancez ce script: python prepare_training_data_with_file.py")
    print()
    print("Exemple:")
    print('  "ReelAudio-5577.wav": "كيفاش راك؟ شكون انت؟"')
    print()
    exit(0)

# Vérifier et préparer chaque fichier
metadata = []
errors = []

for i, wav_file in enumerate(wav_files, 1):
    print(f"[{i}/{len(wav_files)}] Traitement: {wav_file}")
    
    try:
        # Charger l'audio
        audio = AudioSegment.from_wav(str(wav_file))
        
        # Vérifier la durée
        duration = len(audio) / 1000.0
        print(f"  Duree: {duration:.1f} secondes")
        
        # Convertir en mono si nécessaire
        if audio.channels > 1:
            print(f"  Conversion: Stereo -> Mono")
            audio = audio.set_channels(1)
        
        # Convertir en 22050 Hz (format recommandé pour XTTS)
        if audio.frame_rate != 22050:
            print(f"  Resampling: {audio.frame_rate} Hz -> 22050 Hz")
            audio = audio.set_frame_rate(22050)
        
        # Normaliser le volume
        audio = audio.normalize()
        
        # Nom du fichier de sortie
        output_name = f"audio_{i:03d}.wav"
        output_path = wav_dir / output_name
        
        # Exporter
        audio.export(str(output_path), format="wav")
        print(f"  OK: {output_name}")
        
        # Récupérer la transcription
        transcription = transcriptions.get(wav_file.name, "").strip()
        
        if not transcription:
            print(f"  ATTENTION: Transcription vide pour {wav_file.name}!")
            print(f"  Utilisation du nom de fichier comme transcription.")
            transcription = wav_file.stem
        
        print(f"  Transcription: {transcription[:50]}..." if len(transcription) > 50 else f"  Transcription: {transcription}")
        
        # Ajouter à la métadonnée
        metadata.append({
            "audio_file": f"wavs/{output_name}",
            "text": transcription,
            "speaker_id": "darija_speaker"
        })
        
        print()
        
    except Exception as e:
        print(f"  ERREUR: {e}")
        errors.append(wav_file.name)
        print()

# Créer le fichier de métadonnées
metadata_file = dataset_dir / "metadata.json"
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("RESUME")
print("=" * 60)
print()
print(f"Fichiers traites: {len(metadata)}")
print(f"Fichiers en erreur: {len(errors)}")
print()
print(f"Fichier de metadonnees: {metadata_file}")
print(f"Dossier audio: {wav_dir}")
print()

if errors:
    print("Fichiers en erreur:")
    for err in errors:
        print(f"  - {err}")
    print()

if metadata:
    print("=" * 60)
    print("SUCCES!")
    print("=" * 60)
    print()
    print("Prochaine etape:")
    print("  Lancez: python train_xtts.py")
    print()
    print("Exemple de transcription dans metadata.json:")
    if metadata:
        print(f"  Audio: {metadata[0]['audio_file']}")
        print(f"  Texte: {metadata[0]['text']}")
else:
    print("ERREUR: Aucune donnee preparee!")

