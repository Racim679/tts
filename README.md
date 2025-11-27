# XTTS-v2 Fine-tuning - Darija Algérienne

Projet de fine-tuning du modèle XTTS-v2 pour la génération de voix en Darija algérienne.

## Configuration

- **Modèle**: XTTS-v2 (Coqui TTS)
- **Sample Rate**: 48 kHz (qualité maximale)
- **Précision**: FP32
- **Dataset**: 1518 fichiers audio segmentés
- **Langue**: Darija algérienne

## Prérequis

- Python 3.11+
- GPU NVIDIA avec 24GB VRAM (recommandé)
- CUDA installé
- FFmpeg installé

## Installation

### 1. Cloner le repository

```bash
git clone <URL_DU_REPO>
cd "arable tts"
```

### 2. Créer l'environnement virtuel

```powershell
python -m venv venv_tts
.\venv_tts\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```bash
pip install TTS torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install soundfile pandas python-dotenv google-generativeai
```

### 4. Installer FFmpeg (si nécessaire)

```powershell
# Via Chocolatey
choco install ffmpeg

# Ou télécharger depuis https://ffmpeg.org/download.html
```

### 5. Télécharger les fichiers du modèle XTTS-v2

Le modèle de base sera téléchargé automatiquement lors du premier lancement, ou vous pouvez le télécharger manuellement :

```python
from TTS.utils.manage import ModelManager
manager = ModelManager()
manager.download_model("tts_models/multilingual/multi-dataset/xtts_v2")
```

## Structure du projet

```
.
├── dataset_training/
│   ├── wavs/              # 1518 fichiers audio WAV (48 kHz, mono)
│   ├── metadata.json      # Métadonnées avec transcriptions
│   ├── metadata_train.csv # Split train (généré automatiquement)
│   └── metadata_eval.csv  # Split eval (généré automatiquement)
├── train_xtts_simple.py   # Script d'entraînement principal
├── generate_finetuned_direct.py  # Génération audio avec modèle fine-tuné
├── transcribe_with_gemini.py     # Transcription automatique avec Gemini
├── add_m4a_to_dataset.py          # Conversion M4A → WAV
├── split_audio_segments.py        # Segmentation des fichiers longs
└── xtts_finetuned/        # Checkpoints (à télécharger séparément)
```

## Utilisation

### Entraînement

```powershell
.\lancer_entrainement.ps1
```

Ou directement :

```bash
python train_xtts_simple.py
```

**Configuration actuelle :**
- Epoques: 120
- Batch size: 4
- Learning rate: 3e-6
- Gradient accumulation: 4
- Précision: FP32

**Temps estimé :** Plusieurs heures (dépend du GPU)

**Checkpoints :** Sauvegardés dans `xtts_finetuned/run/training/`

### Génération audio

```bash
python generate_finetuned_direct.py "Votre texte en darija"
```

Ou avec un fichier PLS/text :

```bash
python generate_finetuned_direct.py --file input.txt --output-dir output/
```

### Transcription automatique

1. Créer un fichier `.env` avec votre clé Gemini :

```
GEMINI_API_KEY=votre_cle_api
```

2. Lancer la transcription :

```powershell
.\transcrire.ps1
```

## Notes importantes

- **VRAM requise**: ~20-22 GB pour la configuration actuelle
- **Fichiers volumineux**: Les checkpoints ne sont pas dans Git (voir `.gitignore`)
- **Transcriptions**: 1496 fichiers ont besoin de transcription (utiliser `transcribe_with_gemini.py`)
- **Audio de référence**: Utiliser un fichier du dataset pour la génération

## Partage des checkpoints

Les checkpoints sont trop volumineux pour Git. Options :

1. **Google Drive / OneDrive** : Partager le dossier `xtts_finetuned/`
2. **Hugging Face Hub** : Uploader les checkpoints
3. **USB/Disque externe** : Pour transfert local

## Support

Pour toute question, vérifier :
- Les logs dans `xtts_finetuned/run/training/*/trainer_0_log.txt`
- TensorBoard : `tensorboard --logdir xtts_finetuned/run/training/`

