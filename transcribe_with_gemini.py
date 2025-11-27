#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour transcrire les fichiers audio avec Gemini Flash 2.0 exp
Utilise l'API Gemini pour la transcription intelligente en Darija algérienne
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import time

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Charger les variables d'environnement
env_path = Path(".env")
if env_path.exists():
    try:
        # Essayer de charger avec load_dotenv
        load_dotenv(str(env_path))
    except Exception as e:
        print(f"AVERTISSEMENT: Erreur lors du chargement du .env: {e}")
        print("Tentative de chargement manuel...")
    
    # Charger manuellement pour être sûr
    try:
        with open(env_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig gère le BOM
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Nettoyer le BOM si présent
                    key = key.strip().lstrip('\ufeff')
                    os.environ[key] = value.strip()
    except Exception as e:
        print(f"ERREUR: Impossible de charger le fichier .env: {e}")
else:
    print(f"AVERTISSEMENT: Fichier .env non trouve dans {Path.cwd()}")

try:
    import google.generativeai as genai
except ImportError:
    print("ERREUR: google-generativeai n'est pas installe!")
    print("  Installez-le avec: pip install google-generativeai python-dotenv")
    exit(1)

print("=" * 60)
print("Transcription audio avec Gemini Flash 2.0 exp")
print("Transcription intelligente en Darija algerienne")
print("=" * 60)
print()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERREUR: GEMINI_API_KEY non trouvee dans .env!")
    print("  Verifiez que le fichier .env contient: GEMINI_API_KEY=votre_cle")
    print(f"  Repertoire courant: {Path.cwd()}")
    print(f"  Fichier .env existe: {env_path.exists()}")
    if env_path.exists():
        print(f"  Contenu du .env:")
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                print(f"    {f.read()}")
        except Exception as e:
            print(f"    Erreur lecture: {e}")
    exit(1)

# Configurer Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Utiliser Gemini Flash 2.0 exp
model_name = "gemini-2.0-flash-exp"
try:
    model = genai.GenerativeModel(model_name)
    print(f"✓ Modele charge: {model_name}")
except Exception as e:
    print(f"ERREUR: Impossible de charger le modele {model_name}")
    print(f"  Erreur: {e}")
    print("  Essayez avec 'gemini-1.5-flash' si 2.0 n'est pas disponible")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        print(f"✓ Modele de secours charge: gemini-1.5-flash")
    except:
        exit(1)

print()

# Dossiers
dataset_dir = Path("dataset_training")
wav_dir = dataset_dir / "wavs"
metadata_file = dataset_dir / "metadata.json"

# Charger les métadonnées
if not metadata_file.exists():
    print(f"ERREUR: {metadata_file} n'existe pas!")
    exit(1)

with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"Metadata chargee: {len(metadata)} fichiers")
print()

# Prompt pour la transcription
TRANSCRIPTION_PROMPT = "Transcris cet audio intelligement (il est en darija algerienne)."

# Fonction pour détecter si une transcription est valide (pas un UUID)
def is_valid_transcription(text):
    """Vérifie si la transcription est valide (pas un UUID ou nom de fichier)"""
    if not text or not text.strip():
        return False
    # Si c'est un UUID (contient des tirets et des caractères hexadécimaux)
    if len(text) > 30 and '-' in text and all(c in '0123456789abcdef-' for c in text.lower()):
        return False
    # Si c'est juste le nom de fichier sans extension
    if text.startswith('audio_') and len(text.split('_')) > 2:
        return False
    return True

# Compter les fichiers à transcrire
files_to_transcribe = []
for item in metadata:
    text = item.get("text", "").strip()
    if not is_valid_transcription(text):
        files_to_transcribe.append(item)

print(f"Fichiers a transcrire: {len(files_to_transcribe)}")
print(f"Fichiers deja transcrits: {len(metadata) - len(files_to_transcribe)}")
print()

if not files_to_transcribe:
    print("✓ Tous les fichiers sont deja transcrits!")
    exit(0)

# Demander confirmation
print("Voulez-vous continuer? (cela peut prendre du temps)")
print("Appuyez sur Entree pour continuer, ou Ctrl+C pour annuler...")
try:
    input()
except KeyboardInterrupt:
    print("\nAnnule.")
    exit(0)

print()
print("=" * 60)
print("DEBUT DE LA TRANSCRIPTION")
print("=" * 60)
print()

# Traiter les fichiers
transcribed_count = 0
error_count = 0
errors = []

for i, item in enumerate(files_to_transcribe, 1):
    audio_file = item.get("audio_file", "")
    audio_path = dataset_dir / audio_file
    
    if not audio_path.exists():
        print(f"[{i}/{len(files_to_transcribe)}] ⚠️  Fichier non trouve: {audio_file}")
        error_count += 1
        errors.append(audio_file)
        continue
    
    print(f"[{i}/{len(files_to_transcribe)}] {audio_file}")
    
    try:
        # Préparer le prompt avec l'audio
        print(f"  Envoi a Gemini...")
        
        # Utiliser l'API Gemini pour transcrire
        # Gemini 2.0 Flash exp supporte les fichiers audio directement
        # Uploader le fichier audio
        audio_file_obj = None
        try:
            audio_file_obj = genai.upload_file(path=str(audio_path), mime_type="audio/wav")
            
            # Attendre que le fichier soit prêt
            import time
            while audio_file_obj.state.name == "PROCESSING":
                time.sleep(2)
                audio_file_obj = genai.get_file(audio_file_obj.name)
            
            if audio_file_obj.state.name == "FAILED":
                raise Exception(f"Upload failed: {audio_file_obj.state}")
            
            # Générer la transcription
            response = model.generate_content([
                TRANSCRIPTION_PROMPT,
                audio_file_obj
            ])
        finally:
            # Supprimer le fichier uploadé après utilisation
            if audio_file_obj:
                try:
                    genai.delete_file(audio_file_obj.name)
                except:
                    pass
        
        transcription = response.text.strip()
        
        if not transcription:
            print(f"  ⚠️  Transcription vide")
            error_count += 1
            errors.append(audio_file)
            continue
        
        # Limiter à 166 caractères pour XTTS (limite pour l'arabe)
        if len(transcription) > 166:
            transcription = transcription[:166]
            print(f"  ⚠️  Transcription tronquee a 166 caracteres")
        
        # Mettre à jour la métadonnée
        item["text"] = transcription
        
        # Afficher la transcription
        print(f"  ✓ Transcription: {transcription[:80]}..." if len(transcription) > 80 else f"  ✓ Transcription: {transcription}")
        
        transcribed_count += 1
        
        # Sauvegarder périodiquement (tous les 10 fichiers)
        if transcribed_count % 10 == 0:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"  → Sauvegarde intermediaire...")
        
        # Pause pour éviter de dépasser les limites de l'API
        time.sleep(0.5)
        print()
        
    except Exception as e:
        print(f"  ✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        error_count += 1
        errors.append(audio_file)
        print()
        
        # En cas d'erreur API, attendre un peu plus
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            print("  ⚠️  Limite de l'API atteinte, attente de 60 secondes...")
            time.sleep(60)

# Sauvegarder les métadonnées finales
print("=" * 60)
print(f"Sauvegarde finale des metadonnees...")
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"✓ {transcribed_count} fichiers transcrits avec succes")
if error_count > 0:
    print(f"⚠️  {error_count} erreurs")
    if errors:
        print("Fichiers en erreur:")
        for err_file in errors[:10]:
            print(f"  - {err_file}")
        if len(errors) > 10:
            print(f"  ... et {len(errors) - 10} autres")

print()
print("=" * 60)
print("TERMINE!")
print("=" * 60)
print()
print("Prochaines etapes:")
print("  1. Verifiez les transcriptions dans metadata.json")
print("  2. Corrigez les transcriptions si necessaire")
print("  3. Lancez l'entrainement avec: python train_xtts_simple.py")
print()

